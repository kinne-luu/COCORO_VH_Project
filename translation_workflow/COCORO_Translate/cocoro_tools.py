#!/usr/bin/env python3
"""
COCORO translation tools (đặt cạnh file COCORO_Dialogue.xlsx)

  python cocoro_tools.py status [scene]          tiến độ, kế hoạch batch, batch kế tiếp
  python cocoro_tools.py extract <scene> <N>     xuất batch N ra work/<scene>_bNN_src.txt
  python cocoro_tools.py check   <scene> <N>     hậu kiểm out/<scene>_bNN.txt
  python cocoro_tools.py merge   <scene> [N]     ghi bản dịch đã qua kiểm tra vào cột Vietnamese

Tùy chọn chung: --xlsx đường_dẫn  --root thư_mục  --min 50 --target 60 --max 80
Cần: pip install openpyxl
"""
import argparse, csv, re, shutil, sys, datetime
from pathlib import Path

try:
    import openpyxl
except ImportError:
    sys.exit("Thiếu openpyxl: pip install openpyxl")

NL = "⏎"  # ký hiệu thay cho xuống dòng thật trong ô
# Mã điều khiển thật của engine (đã quét từ file): \n  %n;  %n;#00ff0000;  %130;  %80;  %R  %L  %C
CODE_RE = re.compile(r"\\[A-Za-z]|%(?:[A-Za-z0-9]*;(?:#[0-9A-Fa-f]{6,8};)?|[A-Z])")
# Furigana dạng [よみ]漢字 (cách đọc đứng trước chữ Hán): chỉ là cách đọc tiếng Nhật, BẮT BUỘC bỏ khi dịch
RUBY_RE = re.compile(r"\[[ぁ-ゟ゠-ヿー・]+\]")
KANA_RE = re.compile(r"[\u3040-\u30ff\u31f0-\u31ff\uff66-\uff9f]")
HAN_RE = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff]")

HEADER_MATCH = {
    "id":     lambda h: h.lower() == "id",
    "scene":  lambda h: h.lower().startswith("scenario"),
    "spk_jp": lambda h: h.lower().startswith("speaker (jp"),
    "spk_en": lambda h: h.lower().startswith("speaker (en"),
    "jp":     lambda h: h.lower().startswith("japanese"),
    "en":     lambda h: h.lower().startswith("english"),
    "vi":     lambda h: h.lower().startswith("vietnamese"),
    "cn":     lambda h: h.lower().startswith("chinese simplified"),
}


def clean(v):
    if v is None:
        return ""
    s = str(v).replace("\r\n", "\n").replace("\r", "\n").strip()
    return s.replace("\n", NL)


def load(xlsx, primary=None):
    """Đọc sheet chính (mặc định All_Dialogues). Các sheet scene có cùng ID được coi là bản phản chiếu."""
    wb = openpyxl.load_workbook(xlsx)
    sheets = {}
    for ws in wb.worksheets:
        cols = {}
        for c in range(1, ws.max_column + 1):
            h = " ".join(str(ws.cell(1, c).value or "").split())
            for key, fn in HEADER_MATCH.items():
                if key not in cols and h and fn(h):
                    cols[key] = c
        if {"id", "jp", "vi"} <= cols.keys():
            sheets[ws.title] = (ws, cols)
    if not sheets:
        sys.exit("Không tìm thấy sheet nào có cột ID / Japanese / Vietnamese ở dòng 1.")
    name = primary or ("All_Dialogues" if "All_Dialogues" in sheets else next(iter(sheets)))
    if name not in sheets:
        sys.exit(f"Không có sheet '{name}'. Các sheet hợp lệ: {', '.join(list(sheets)[:6])}...")
    mirror = {}
    for t, (w, c) in sheets.items():
        if t == name:
            continue
        for r in range(2, w.max_row + 1):
            rid = clean(w.cell(r, c["id"]).value)
            if rid:
                mirror.setdefault(rid, []).append((w, r, c["vi"]))
    ws, cols = sheets[name]
    rows, scenes, seen = [], {}, set()
    for r in range(2, ws.max_row + 1):
        rid = clean(ws.cell(r, cols["id"]).value)
        if not rid:
            continue
        if rid in seen:
            sys.exit(f"ID trùng trong sheet {name}: {rid}")
        seen.add(rid)
        sc = clean(ws.cell(r, cols["scene"]).value) if "scene" in cols else ""
        sc = sc[:-3] if sc.endswith(".ks") else (sc or rid.rsplit("_", 1)[0])
        g = lambda k: clean(ws.cell(r, cols[k]).value) if k in cols else ""
        row = dict(id=rid, scene=sc, spk_jp=g("spk_jp"), spk_en=g("spk_en"),
                   jp=g("jp"), en=g("en"), cn=g("cn"), vi=g("vi"),
                   ws=ws, r=r, vi_col=cols["vi"], mirrors=mirror.get(rid, []))
        rows.append(row)
        scenes.setdefault(sc, []).append(row)
    info = dict(sheet=name, mirrors=sum(1 for t in sheets if t != name))
    return wb, rows, scenes, info


def plan_batches(rows, mn, tg, mx):
    """Chia scene thành batch 50-80 dòng, ưu tiên cắt ở chỗ đổi người nói."""
    n, i, out = len(rows), 0, []
    while i < n:
        rem = n - i
        if rem <= mx:
            out.append((i, n)); break
        best = None
        for c in range(i + mn, min(i + mx, n - 1) + 1):
            if rows[c - 1]["spk_jp"] != rows[c]["spk_jp"]:
                d = abs(c - (i + tg))
                if best is None or d < best[0]:
                    best = (d, c)
        c = best[1] if best else i + tg
        if n - c < mn // 2:
            c = i + rem // 2
        out.append((i, c)); i = c
    return out


def parse_out(path):
    res, order = {}, []
    for ln in Path(path).read_text(encoding="utf-8").splitlines():
        if not ln.strip():
            continue
        m = re.match(r"^\s*(\S+?)\s*\|\s?(.*)$", ln)
        if not m:
            res[f"__bad__{len(order)}"] = ln; order.append(f"__bad__{len(order)}"); continue
        order.append(m.group(1)); res[m.group(1)] = m.group(2).strip()
    return order, res


def log(root, cmd, scene, batch, status, detail=""):
    p = root / "logs"; p.mkdir(exist_ok=True)
    new = not (p / "run_log.csv").exists()
    with open(p / "run_log.csv", "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if new: w.writerow(["time", "cmd", "scene", "batch", "status", "detail"])
        w.writerow([datetime.datetime.now().isoformat(timespec="seconds"), cmd, scene, batch, status, detail])


def get_batch(scenes, scene, n, a):
    if scene not in scenes:
        sys.exit(f"Không có scene '{scene}'. Scene hiện có: {', '.join(list(scenes)[:5])}...")
    rows = scenes[scene]
    plan = plan_batches(rows, a.min, a.target, a.max)
    if not 1 <= n <= len(plan):
        sys.exit(f"Scene {scene} có {len(plan)} batch, không có batch {n}.")
    s, e = plan[n - 1]
    return rows, plan, rows[s:e], s, e


def out_path(root, scene, n): return root / "out" / f"{scene}_b{n:02d}.txt"
def src_path(root, scene, n): return root / "work" / f"{scene}_b{n:02d}_src.txt"


def batch_state(root, scene, n, batch_rows):
    if all(r["vi"] for r in batch_rows if r["jp"]):
        return "merged"
    return "out-ready" if out_path(root, scene, n).exists() else "todo"


# ---------------------------------------------------------------- status
def cmd_status(a, root, scenes, info=None):
    if info:
        print(f"Sheet chính: {info['sheet']} (+{info['mirrors']} sheet phản chiếu cùng ID)")
    names = [a.scene] if a.scene else list(scenes)
    nxt = None
    for sc in names:
        rows = scenes[sc]
        done = sum(1 for r in rows if r["vi"])
        plan = plan_batches(rows, a.min, a.target, a.max)
        states = [batch_state(root, sc, i + 1, rows[s:e]) for i, (s, e) in enumerate(plan)]
        print(f"{sc:<12} {done:>4}/{len(rows):<4} [{100*done//len(rows):>3}%]  batch: {states.count('merged')}/{len(plan)}")
        if a.scene:
            for i, ((s, e), st) in enumerate(zip(plan, states), 1):
                print(f"   b{i:02d}  dòng {s+1}-{e}  ({e-s} dòng)  {st}")
        if nxt is None and any(st != "merged" for st in states):
            i = next(k for k, st in enumerate(states) if st != "merged")
            nxt = (sc, i + 1, len(plan), plan[i], states[i])
    if nxt:
        print(f"\nKẾ TIẾP: {nxt[0]} batch {nxt[1]}/{nxt[2]} (dòng {nxt[3][0]+1}-{nxt[3][1]}) - trạng thái: {nxt[4]}")
    else:
        print("\nĐã dịch xong tất cả scene được liệt kê.")


# --------------------------------------------------------------- extract
def cmd_extract(a, root, scenes):
    rows, plan, br, s, e = get_batch(scenes, a.scene, a.batch, a)
    lines = [f"# scene={a.scene} batch={a.batch}/{len(plan)} dòng {s+1}-{e} / {len(rows)}",
             "# ĐỊNH DẠNG: ID | Speaker | Japanese | English | Chinese(Simp)   (⏎ = xuống dòng trong ô)",
             "# Furigana [よみ]漢字: chỉ là cách đọc, BỎ khi dịch. Mã %n; %R %L %C %130; \\n: GIỮ NGUYÊN."]
    prev = {}
    if a.batch > 1:
        ps, pe = plan[a.batch - 2]
        po = out_path(root, a.scene, a.batch - 1)
        if po.exists():
            prev = parse_out(po)[1]
    ctx = rows[max(0, s - 5):s]
    if ctx:
        lines.append("# --- NGỮ CẢNH (đã dịch, KHÔNG dịch lại): JP => VI")
        for r in ctx:
            vi = r["vi"] or prev.get(r["id"], "")
            lines.append(f"# {r['id']} | {r['jp']} => {vi}")
    lines.append("# --- CẦN DỊCH")
    for r in br:
        spk = r["spk_jp"] + (f"({r['spk_en']})" if r["spk_en"] else "") or "-"
        lines.append(f"{r['id']} | {spk} | {r['jp']} | {r['en']} | {r['cn']}")
    p = src_path(root, a.scene, a.batch); p.parent.mkdir(exist_ok=True)
    p.write_text("\n".join(lines) + "\n", encoding="utf-8")
    log(root, "extract", a.scene, a.batch, "ok", f"{len(br)} dòng")
    print(f"Đã ghi {p} ({len(br)} dòng cần dịch)")


# ----------------------------------------------------------------- check
def run_check(a, root, scenes, scene, n):
    rows, plan, br, s, e = get_batch(scenes, scene, n, a)
    p = out_path(root, scene, n)
    errs, warns = [], []
    if not p.exists():
        return [f"Không thấy file {p}"], [], br, {}
    order, res = parse_out(p)
    bad = [k for k in order if k.startswith("__bad__")]
    for k in bad: errs.append(f"Dòng sai định dạng (cần 'ID | bản dịch'): {res[k][:60]}")
    got = [k for k in order if not k.startswith("__bad__")]
    exp = [r["id"] for r in br]
    if len(got) != len(exp):
        errs.append(f"Số dòng: nhận {len(got)}, cần {len(exp)}")
    if got != exp:
        miss = [x for x in exp if x not in got]; extra = [x for x in got if x not in exp]
        if miss: errs.append(f"Thiếu ID: {', '.join(miss[:8])}{' ...' if len(miss)>8 else ''}")
        if extra: errs.append(f"ID thừa/lạ: {', '.join(extra[:8])}")
        if not miss and not extra: errs.append("ID đủ nhưng sai thứ tự hoặc trùng lặp")
    for r in br:
        if r["id"] not in res: continue
        vi, jp, en = res[r["id"]], r["jp"], r["en"]
        tag = r["id"]
        if jp and not vi: errs.append(f"{tag}: bản dịch rỗng"); continue
        if not jp: continue
        jp_nr, vi_nr = RUBY_RE.sub("", jp), RUBY_RE.sub("", vi)
        if vi == jp and (KANA_RE.search(jp) or HAN_RE.search(jp)):
            errs.append(f"{tag}: giống hệt bản gốc tiếng Nhật")
        if RUBY_RE.search(vi):
            errs.append(f"{tag}: còn furigana dạng [よみ] trong bản dịch (phải bỏ)")
        if KANA_RE.search(vi_nr) or HAN_RE.search(vi_nr):
            errs.append(f"{tag}: còn chữ Nhật/Hán trong bản dịch")
        cj, cv = CODE_RE.findall(jp_nr), CODE_RE.findall(vi_nr)
        if cj != cv:
            errs.append(f"{tag}: mã điều khiển lệch (gốc {cj} / dịch {cv})")
        if jp.count(NL) != vi.count(NL):
            errs.append(f"{tag}: số ký hiệu {NL} lệch ({jp.count(NL)} → {vi.count(NL)})")
        if en and vi == en: warns.append(f"{tag}: giống hệt bản tiếng Anh")
        lj = len(re.sub(r"\s+", "", CODE_RE.sub("", jp_nr)))
        if lj >= 8:
            ratio = len(re.sub(r"\s+", "", CODE_RE.sub("", vi_nr))) / lj
            if ratio > 4.5: warns.append(f"{tag}: bản dịch dài bất thường (x{ratio:.1f} so với gốc)")
            if ratio < 0.7: warns.append(f"{tag}: bản dịch ngắn bất thường (x{ratio:.1f} so với gốc), có thể bị rút gọn")
    return errs, warns, br, res


def cmd_check(a, root, scenes):
    errs, warns, br, _ = run_check(a, root, scenes, a.scene, a.batch)
    for w in warns: print("  CẢNH BÁO:", w)
    for x in errs: print("  LỖI:", x)
    st = "FAIL" if errs else "PASS"
    print(f"{st}: {a.scene} batch {a.batch} ({len(br)} dòng, {len(errs)} lỗi, {len(warns)} cảnh báo)")
    log(root, "check", a.scene, a.batch, st, f"{len(errs)} lỗi; {len(warns)} cảnh báo")
    sys.exit(1 if errs else 0)


# ----------------------------------------------------------------- merge
def cmd_merge(a, root, scenes):
    wb, rows, scenes, info = load(a.xlsx, a.sheet)  # nạp lại bản mới nhất để ghi
    plan = plan_batches(scenes[a.scene], a.min, a.target, a.max)
    todo = [a.batch] if a.batch else [i + 1 for i in range(len(plan)) if out_path(root, a.scene, i + 1).exists()]
    if not todo:
        sys.exit("Không có file out/ nào để ghi.")
    bak = root / "backup" / f"{Path(a.xlsx).stem}_{a.scene}_truoc_khi_ghi.xlsx"
    if not bak.exists():
        bak.parent.mkdir(exist_ok=True); shutil.copy2(a.xlsx, bak)
    written = 0
    for n in todo:
        errs, _, br, res = run_check(a, root, scenes, a.scene, n)
        if errs:
            print(f"BỎ QUA batch {n}: chưa qua kiểm tra ({len(errs)} lỗi). Chạy 'check' để xem.")
            log(root, "merge", a.scene, n, "skip", "check fail"); continue
        conflicts = [r["id"] for r in br if r["vi"] and r["vi"] != res.get(r["id"], "") and not a.force]
        if conflicts:
            print(f"BỎ QUA batch {n}: {len(conflicts)} ô Vietnamese đã có nội dung khác (dùng --force để ghi đè): {conflicts[:3]}")
            log(root, "merge", a.scene, n, "skip", "conflict"); continue
        for r in br:
            val = res[r["id"]].replace(NL, "\n") or None
            r["ws"].cell(r["r"], r["vi_col"]).value = val
            for (mw, mr, mc) in r["mirrors"]:
                mw.cell(mr, mc).value = val
        written += len(br)
        log(root, "merge", a.scene, n, "ok", f"{len(br)} dòng")
        print(f"Đã ghi batch {n} ({len(br)} dòng)")
    if written:
        try:
            wb.save(a.xlsx)
        except PermissionError:
            sys.exit("Không lưu được: hãy đóng file Excel đang mở rồi chạy lại.")
        print(f"Đã lưu {a.xlsx}. Bản sao lưu trước scene: {bak}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", default=str(Path(__file__).resolve().parent))
    ap.add_argument("--xlsx", default=None)
    ap.add_argument("--sheet", default=None, help="sheet chính (mặc định All_Dialogues)")
    ap.add_argument("--min", type=int, default=50)
    ap.add_argument("--target", type=int, default=60)
    ap.add_argument("--max", type=int, default=80)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("status"); s.add_argument("scene", nargs="?")
    s = sub.add_parser("extract"); s.add_argument("scene"); s.add_argument("batch", type=int)
    s = sub.add_parser("check"); s.add_argument("scene"); s.add_argument("batch", type=int)
    s = sub.add_parser("merge"); s.add_argument("scene"); s.add_argument("batch", type=int, nargs="?")
    s.add_argument("--force", action="store_true")
    a = ap.parse_args()
    root = Path(a.root)
    a.xlsx = a.xlsx or str(root / "COCORO_Dialogue.xlsx")
    if not Path(a.xlsx).exists():
        sys.exit(f"Không thấy file {a.xlsx}")
    _, _, scenes, info = load(a.xlsx, a.sheet)
    if getattr(a, "scene", None) and a.scene not in scenes:
        sys.exit(f"Không có scene '{a.scene}'.")
    if a.cmd == "status":
        cmd_status(a, root, scenes, info)
    else:
        {"extract": cmd_extract, "check": cmd_check, "merge": cmd_merge}[a.cmd](a, root, scenes)


if __name__ == "__main__":
    main()
