# -*- coding: utf-8 -*-
"""
COCORO - Full Vietnamese Translation Repacker (50 Scenarios + 15 UI TLG5)
- Translates dialogues using COCORO_Dialogue-chinh-sua.xlsx
- Integrates verified 15 UI TLG5 images from tlg_msgtool
- Encrypts using 100% official Frontwing HXV4 FilterRuntimeState (DripProgram)
- Patches E:\\Games\\COCORO.FIXED\\game\\data.xp3
- Syncs COCORO_Patch_VietHoa/patch_data and patch_manifest.json
"""
import os
import sys
import struct
import zlib
import shutil
import re
import json
from pathlib import Path
from collections import Counter
import openpyxl

# Add cxdec tools
sys.path.insert(0, r"E:\Extract Tools\cxdec-hxv4\src\common")
from xp3_inspect import DripProgram, read_archive, load_index, parse_hxv4_table, FilterRuntimeState

ROOT_DIR = Path(r"D:\Software\Antigravity\Project\Cocoro")
EXCEL_PATH = ROOT_DIR / "COCORO_Dialogue-chinh-sua.xlsx"
EXTRACTED_DIR = ROOT_DIR / "extracted_data" / "data"
GLOSSARY_PATH = ROOT_DIR / "COCORO_Translate" / "config" / "glossary.json"
SCENE_TITLES_PATH = ROOT_DIR / "COCORO_Translate" / "config" / "scene_titles.json"
TLG_MSGTOOL_DIR = ROOT_DIR / "tlg_msgtool"

GAME_DIR = Path(r"E:\Games\COCORO.FIXED\game")
XP3_PATH = GAME_DIR / "data.xp3"
BAK_PATH = GAME_DIR / "data.xp3.original.bak"
DRIP_PATH = Path(r"E:\Extract Tools\cxdec-hxv4\data\static_recover\drip_program_COCORO.exe.unpacked.json")

PATCH_DATA_DIR = ROOT_DIR / "COCORO_Patch_VietHoa" / "patch_data"
PATCH_DATA_UI_DIR = PATCH_DATA_DIR / "ui"
PATCH_DATA_PBD_DIR = PATCH_DATA_DIR / "pbd"
PATCH_DATA_CONF_DIR = PATCH_DATA_DIR / "conf"
DATA_UIPSD_DIR = ROOT_DIR / "data" / "uipsd"
PATCH_DATA_DIR.mkdir(parents=True, exist_ok=True)
PATCH_DATA_UI_DIR.mkdir(parents=True, exist_ok=True)
PATCH_DATA_PBD_DIR.mkdir(parents=True, exist_ok=True)
PATCH_DATA_CONF_DIR.mkdir(parents=True, exist_ok=True)
DATA_UIPSD_DIR.mkdir(parents=True, exist_ok=True)

PBD_NAME_MAP = {
    "pc_game_qmenu.pbd": 2157,
    "pc_game_qmenu": 2157,
    "title.pbd": 2161,
    "title": 2161,
    "pc_game_side.pbd": 2056,
    "pc_game_side": 2056,
}

def calc_adler32(data: bytes) -> int:
    return zlib.adler32(data) & 0xFFFFFFFF

def parse_psb_strings(psb_bytes):
    hdr = struct.unpack('<11I', psb_bytes[:44])
    off_arr = hdr[4]
    off_data = hdr[5]
    count_len = psb_bytes[off_arr] - 12
    count = int.from_bytes(psb_bytes[off_arr+1 : off_arr+1+count_len], 'little')
    elem_len = psb_bytes[off_arr+1+count_len] - 12
    elems_start = off_arr + 1 + count_len + 1
    offsets = [int.from_bytes(psb_bytes[elems_start + i*elem_len : elems_start + (i+1)*elem_len], 'little') for i in range(count)]
    strings = [psb_bytes[off_data + off:].split(b'\x00')[0].decode('utf-8', errors='ignore') for off in offsets]
    return hdr, strings

def rebuild_psb_strings(psb_bytes, new_strings):
    hdr = list(struct.unpack('<11I', psb_bytes[:44]))
    off_arr = hdr[4]
    off_data = hdr[5]
    
    new_data = bytearray()
    new_offsets = []
    for s in new_strings:
        new_offsets.append(len(new_data))
        new_data.extend(s.encode('utf-8'))
        new_data.append(0)
        
    count = len(new_strings)
    max_off = max(new_offsets) if new_offsets else 0
    if max_off < 0x100: elem_len = 1
    elif max_off < 0x10000: elem_len = 2
    elif max_off < 0x1000000: elem_len = 3
    else: elem_len = 4
    
    count_bytes = count.to_bytes(4, 'little').rstrip(b'\x00') or b'\x00'
    count_len = len(count_bytes)
    
    new_arr = bytearray()
    new_arr.append(12 + count_len)
    new_arr.extend(count_bytes)
    new_arr.append(12 + elem_len)
    for off in new_offsets:
        new_arr.extend(off.to_bytes(elem_len, 'little'))
        
    prefix = psb_bytes[44:off_arr]
    shift_arr = 44 + len(prefix)
    shift_data = shift_arr + len(new_arr)
    delta_data_end = (shift_data + len(new_data)) - (off_data + (hdr[6] - hdr[5]))
    
    hdr[4] = shift_arr
    hdr[5] = shift_data
    for i in (6, 7, 8):
        hdr[i] += delta_data_end
        
    old_data_end = off_data + (struct.unpack('<11I', psb_bytes[:44])[6] - off_data)
    suffix = psb_bytes[old_data_end:]
    
    res = bytearray(struct.pack('<11I', *hdr))
    res.extend(prefix)
    res.extend(new_arr)
    res.extend(new_data)
    res.extend(suffix)
    return bytes(res)

special_manual_fallbacks = {
    'scn00_00_0005': ['"No, that\'s not your cry."', '                              "No, that\'s not your cry."', '                              "No, that\'s not %i1your%id cry."'],
    'scn00_00_0006': ['"That\'s not your pain."', '                              "That\'s not your pain."', '                              "That\'s not %i1your%id pain."'],
    'scn00_00_0007': ['"These are not your last—"', '                              "These are not your last—"', '                              "These are not %i1your%id last—"'],
    'scn00_04_0298': ['"Actually, if there\'s anything about me that %i1doesn\'t%id look human, I\'d like you to tell me."', '"Actually, if there\'s anything about me that doesn\'t look human, I\'d like you to tell me."'],
    'scn00_06_0156': ["So %i1that's%id why she stopped coming to the garden after that day.", "So that's why she stopped coming to the garden after that day."],
    'scn00_20_0082': ['"Huh!? No! I mean, %i1that\'s%id when I started liking you!"', '"Huh!? No! I mean, that\'s when I started liking you!"'],
    'scn00_21_0175': ["I even felt as if %i1she'd%id deceived me.", "I even felt as if she'd deceived me."],
    'scn00_23_0198': ['"The Jabberwock? You think %i1that\'s%id it?"', '"The Jabberwock? You think that\'s it?"'],
    'scn00_23_0404': ['Maybe the attack is a kind of %i1fa jin%id—sending explosive vibrations through its body by dealing a blow to its hard outer shell?', 'Maybe the attack is a kind of fa jin—sending explosive vibrations through its body by dealing a blow to its hard outer shell?'],
    'scn00_28_0281': ['And more importantly, what is it doing %i1here?', 'And more importantly, what is it doing here?'],
    'scn00_28_0306': ['Why would it be %i1here?', 'Why would it be here?'],
    'scn00_29_0044': ["Cocoro cried as she said that. I just can't believe that she %i1doesn't%id have emotions.", "Cocoro cried as she said that. I just can't believe that she doesn't have emotions."],
    'scn00_30_0119': ['"I want... I %i1don\'t%id want... you to dispose... Dispose of me..."', '"I want... I don\'t want... you to dispose... Dispose of me..."'],
    'scn00_30_0270': ['"It\'s coming %i1here!?%id"', '"It\'s coming here!?"'],
    'scn00_32_0066': ["(It's as if %i1I'm%id the adult and %i1he's%id the kid!)", "(It's as if I'm the adult and he's the kid!)"],
    'scn00_36_0038': ['(I see... So %i1that\'s%id what "death" is...)', '(I see... So that\'s what "death" is...)'],
    'scn00_36_0202': ['\\n\\n\\n\\n\\n\\n\\n\\n...'],
    'scn00_36_0206': ['\\n\\n\\n\\n\\n\\n\\n\\n...'],
    'scn00_36_0214': ['%n;%i1was tasty.', '%n;was tasty.', 'was tasty.'],
    'scn00_38_0099': ['"I see, so %i1that\'s%id what you meant. My apologies. Umm, it\'s a long story, so I recommend that you all sit..."', '"I see, so that\'s what you meant. My apologies. Umm, it\'s a long story, so I recommend that you all sit..."'],
    'scn00_38_0153': ['"So %i1that\'s%id what Kazane looks like... Just as I\'d imagined. Daichi... reminds me of my omelet attempts. And the dog\'s fluffiness exceeds my expectations."', '"So that\'s what Kazane looks like... Just as I\'d imagined. Daichi... reminds me of my omelet attempts. And the dog\'s fluffiness exceeds my expectations."'],
    'scn00_38_0278': ['"...Honestly, I wasn\'t planning to reveal myself until the end, but I suppose this counts as %i1force majeure.%id"', '"...Honestly, I wasn\'t planning to reveal myself until the end, but I suppose this counts as force majeure."'],
    'scn00_40_0022': ['"Now %i1you\'re%id being rude, Kotaro. How would you feel if somebody said to you, \'I can\'t believe you\'re actually a human\'?"', '"Now you\'re being rude, Kotaro. How would you feel if somebody said to you, \'I can\'t believe you\'re actually a human\'?"'],
}

def strip_tags_keep(s: str) -> str:
    s = re.sub(r"%(?:i1|id|time|trans|wait|fuser|k7k|[a-z])\b|%(?:i1|id)", "", s)
    return re.sub(r"[\s\u3000]+", " ", s).strip()

def strip_tags_drop(s: str) -> str:
    s = re.sub(r"%i1.*?%id", " ", s)
    s = re.sub(r"%(?:i1|id|time|trans|wait|fuser|k7k|[a-z])\b|%(?:i1|id)", "", s)
    return re.sub(r"[\s\u3000]+", " ", s).strip()

def strip_tags_empty(s: str) -> str:
    s = re.sub(r"%i1.*?%id", "", s)
    s = re.sub(r"%(?:i1|id|time|trans|wait|fuser|k7k|[a-z])\b|%(?:i1|id)", "", s)
    return re.sub(r"[\s\u3000]+", " ", s).strip()

def norm_space(s: str) -> str:
    return re.sub(r"[\s\u3000]+", " ", s).strip()

def main():
    print("======================================================================")
    print("      COCORO - ĐÓNG GÓI BẢN VIỆT HÓA TOÀN DIỆN (THOẠI 50 + UI 15)     ")
    print("======================================================================")

    assert EXCEL_PATH.exists(), f"Không tìm thấy {EXCEL_PATH}!"
    assert BAK_PATH.exists(), f"Không tìm thấy {BAK_PATH}!"
    assert DRIP_PATH.exists(), f"Không tìm thấy {DRIP_PATH}!"
    assert TLG_MSGTOOL_DIR.exists(), f"Không tìm thấy {TLG_MSGTOOL_DIR}!"

    # 1. Load Excel
    print(f"\n[1/6] Nạp dữ liệu thoại từ {EXCEL_PATH.name}...")
    wb = openpyxl.load_workbook(EXCEL_PATH, data_only=True)

    with open(GLOSSARY_PATH, "r", encoding="utf-8") as f:
        glossary = json.load(f)
    spk_map = glossary["speakers"]["map"]

    scene_titles = {}
    if SCENE_TITLES_PATH.exists():
        with open(SCENE_TITLES_PATH, "r", encoding="utf-8") as f:
            scene_titles = json.load(f)

    scenes = [f"scn00_{i:02d}" for i in range(49)] + ["scn01_01"]
    scenes_data = {}

    for scn in scenes:
        assert scn in wb.sheetnames, f"Sheet {scn} không tồn tại!"
        ws = wb[scn]
        scenes_data[scn] = {"dialogues": [], "speakers": {}}
        for row in ws.iter_rows(min_row=2, values_only=True):
            if not row or not row[0]: continue
            code, spk_en, spk_jp, txt_en, txt_vi = row[0], row[4], row[3], row[8], row[9]
            if txt_en is not None:
                en_str = str(txt_en)
                vi_str = str(txt_vi) if txt_vi is not None else en_str
                scenes_data[scn]["dialogues"].append((str(code).strip(), en_str, vi_str))
            if spk_en is not None and str(spk_en).strip():
                spk_en_clean = str(spk_en).strip()
                if spk_en_clean in spk_map:
                    scenes_data[scn]["speakers"][spk_en_clean] = spk_map[spk_en_clean]
                elif spk_jp and str(spk_jp).strip() in spk_map:
                    scenes_data[scn]["speakers"][spk_en_clean] = spk_map[str(spk_jp).strip()]

    total_dialogues = sum(len(d["dialogues"]) for d in scenes_data.values())
    print(f"   + Đã nạp thành công {total_dialogues:,} câu thoại từ 50 sheet!")

    # 2. Map extracted_data files
    extracted_files = {}
    for f in os.listdir(EXTRACTED_DIR):
        if f.startswith("entry_"):
            idx = int(f.split("_")[1])
            extracted_files[idx] = f

    # 3. Compile 50 scenario files
    print("\n[2/6] Biên dịch 50 kịch bản PSB tiếng Việt...")
    scenario_plain_blobs = {}

    for i, scn_name in enumerate(scenes):
        entry_idx = 784 + i
        orig_fname = extracted_files[entry_idx]
        orig_bytes = (EXTRACTED_DIR / orig_fname).read_bytes()
        hdr, strings = parse_psb_strings(orig_bytes)

        scn_dict = scenes_data[scn_name]
        d_map = {}
        for code, en, vi in scn_dict["dialogues"]:
            c1 = strip_tags_keep(en)
            c2 = strip_tags_drop(en)
            c3 = strip_tags_empty(en)
            c4 = norm_space(en)
            for k in (c1, c2, c3, c4):
                if k not in d_map: d_map[k] = vi
            if code in special_manual_fallbacks:
                for cand in special_manual_fallbacks[code]:
                    for k in (strip_tags_keep(cand), strip_tags_drop(cand), strip_tags_empty(cand), norm_space(cand)):
                        if k not in d_map: d_map[k] = vi

        new_strings = list(strings)
        d_count = 0
        s_count = 0
        t_count = 0

        # Replace scene titles if defined
        if scn_name in scene_titles:
            t_en = scene_titles[scn_name]["en"]
            t_vi = scene_titles[scn_name]["vi"]
            for s_idx, s in enumerate(strings):
                if s == t_en:
                    new_strings[s_idx] = t_vi
                    t_count += 1

        for s_idx, s in enumerate(strings):
            s_clean = norm_space(s)
            matched_vi = None
            for key in (strip_tags_keep(s), strip_tags_drop(s), strip_tags_empty(s), s_clean):
                if key in d_map:
                    matched_vi = d_map[key]
                    break

            if matched_vi is not None:
                indent_prefix = ""
                m = re.match(r"^([\s\u3000]+)", s)
                if m: indent_prefix = m.group(1).replace('\u3000', ' ')

                leading_newlines = ""
                m2 = re.match(r"^((?:\\n|\n)+)", s)
                if m2: leading_newlines = m2.group(1)

                clean_vi = matched_vi.replace('\u3000', ' ').replace('\\n', '\n')
                if clean_vi.startswith('\n') and leading_newlines:
                    final_text = clean_vi
                else:
                    final_text = leading_newlines + indent_prefix + clean_vi
                new_strings[s_idx] = final_text
                d_count += 1
            elif s_clean in scn_dict["speakers"]:
                new_strings[s_idx] = scn_dict["speakers"][s_clean]
                s_count += 1

        rebuilt_psb = rebuild_psb_strings(orig_bytes, new_strings)
        scenario_plain_blobs[entry_idx] = rebuilt_psb
        (PATCH_DATA_DIR / f"{scn_name}.bin").write_bytes(rebuilt_psb)
        t_info = f", {t_count} title" if t_count > 0 else ""
        print(f"   + [{i+1:02d}/50] {scn_name}: {d_count} thoại, {s_count} speaker{t_info} ({len(rebuilt_psb):,} bytes)")

    # 4. Load official TLG5 files from patch_data/ui
    print("\n[3/6] Nạp các file ảnh UI TLG5 chuẩn và file PBD layout...")
    ui_plain_blobs = {}
    if PATCH_DATA_UI_DIR.exists():
        for f in sorted(PATCH_DATA_UI_DIR.iterdir()):
            if f.name.startswith("entry_") and f.name.endswith(".bin"):
                try:
                    parts = f.stem.split("_")
                    if len(parts) >= 2 and parts[1].isdigit():
                        idx = int(parts[1])
                        tlg_data = f.read_bytes()
                        ui_plain_blobs[idx] = tlg_data
                        print(f"   + [UI] Entry {idx:05d} <- {f.name} ({len(tlg_data):,} bytes)")
                except Exception as e:
                    print(f"   ! Lỗi nạp UI {f.name}: {e}")

    # 4b. Load PBD coordinate/layout files from patch_data/pbd
    pbd_plain_blobs = {}
    if PATCH_DATA_PBD_DIR.exists():
        for f in sorted(PATCH_DATA_PBD_DIR.iterdir()):
            if f.name.startswith("entry_") and f.name.endswith(".bin"):
                try:
                    parts = f.stem.split("_")
                    if len(parts) >= 2 and parts[1].isdigit():
                        idx = int(parts[1])
                        pbd_plain_blobs[idx] = f.read_bytes()
                        print(f"   + [PBD] Entry {idx:05d} <- {f.name} ({len(pbd_plain_blobs[idx]):,} bytes)")
                except Exception as e:
                    print(f"   ! Lỗi nạp PBD {f.name}: {e}")

    # 4c. Load config / text files from patch_data/conf
    conf_plain_blobs = {}
    if PATCH_DATA_CONF_DIR.exists():
        for f in sorted(PATCH_DATA_CONF_DIR.iterdir()):
            if f.name.startswith("entry_") and f.name.endswith(".bin"):
                try:
                    parts = f.stem.split("_")
                    if len(parts) >= 2 and parts[1].isdigit():
                        idx = int(parts[1])
                        conf_plain_blobs[idx] = f.read_bytes()
                        print(f"   + [CONF] Entry {idx:05d} <- {f.name} ({len(conf_plain_blobs[idx]):,} bytes)")
                except Exception as e:
                    print(f"   ! Lỗi nạp CONF {f.name}: {e}")

    # 5. Build official filter states from DripProgram
    print("\n[4/6] Đọc chỉ mục data.xp3 và tính toán Filter State chuẩn HXV4...")
    drip = DripProgram.load(DRIP_PATH)
    info, entries, blob = read_archive(BAK_PATH)
    _, _, _, index = load_index(blob)

    descriptor, records = parse_hxv4_table(blob, index, entries, drip)
    open_flag = descriptor.flags & 1

    entry_seed_states = {}
    states = {}
    for r in records:
        if r.xp3_entry_index is not None:
            seed_state = drip.build_filter_state(r.key, open_flag)
            entry_seed_states[r.xp3_entry_index] = seed_state
            states[r.xp3_entry_index] = FilterRuntimeState(seed_state)

    # 6. Encrypt all blobs (50 scenarios + 15 UI + PBD)
    print("\n[5/6] Mã hóa đối xứng luồng nhị phân với khóa chuẩn...")
    all_patch_entries = {}
    all_patch_entries.update(scenario_plain_blobs)
    all_patch_entries.update(ui_plain_blobs)
    all_patch_entries.update(pbd_plain_blobs)
    all_patch_entries.update(conf_plain_blobs)

    old_file_size = BAK_PATH.stat().st_size
    encrypted_blobs = {}
    current_offset = old_file_size
    blobs_stream = bytearray()

    for idx in sorted(all_patch_entries.keys()):
        plain_data = all_patch_entries[idx]
        adler = calc_adler32(plain_data)

        assert idx in states, f"Entry {idx} không có FilterRuntimeState!"
        fs = states[idx]

        cipher_data = bytearray(plain_data)
        fs.apply(cipher_data, 0)

        encrypted_blobs[idx] = {
            'offset': current_offset,
            'size': len(cipher_data),
            'adler32': adler
        }
        blobs_stream.extend(cipher_data)
        current_offset += len(cipher_data)

    print(f"   + Tổng số entry cần vá: {len(encrypted_blobs)} entry (50 kịch bản + {len(ui_plain_blobs)} ảnh UI + {len(pbd_plain_blobs)} PBD + {len(conf_plain_blobs)} CONF)")
    print(f"   + Tổng dung lượng dữ liệu vá đã mã hóa: {len(blobs_stream):,} bytes")

    # Save manifest for standalone installer
    patch_manifest_entries = []
    for e_idx in sorted(scenario_plain_blobs.keys()):
        scn = scenes[e_idx - 784]
        patch_manifest_entries.append({
            "entry_id": e_idx,
            "type": "scenario",
            "file": f"{scn}.bin"
        })
    for e_idx in sorted(ui_plain_blobs.keys()):
        patch_manifest_entries.append({
            "entry_id": e_idx,
            "type": "ui",
            "file": f"ui/entry_{e_idx:05d}.bin"
        })
    for e_idx in sorted(pbd_plain_blobs.keys()):
        patch_manifest_entries.append({
            "entry_id": e_idx,
            "type": "pbd",
            "file": f"pbd/entry_{e_idx:05d}.bin"
        })
    for e_idx in sorted(conf_plain_blobs.keys()):
        patch_manifest_entries.append({
            "entry_id": e_idx,
            "type": "conf",
            "file": f"conf/entry_{e_idx:05d}.bin"
        })

    manifest_content = {
        "entries": patch_manifest_entries,
        "filter_states": {str(k): entry_seed_states[k].hex() for k in sorted(all_patch_entries.keys())}
    }
    with open(PATCH_DATA_DIR / "patch_manifest.json", "w", encoding="utf-8") as f:
        json.dump(manifest_content, f, indent=2)
    print(f"   + Đã đồng bộ cấu hình cài đặt vào {PATCH_DATA_DIR / 'patch_manifest.json'}")

    # 7. Write to data.xp3
    print(f"\n[6/6] Ghi bản vá toàn diện vào game: {XP3_PATH}...")
    shutil.copy2(BAK_PATH, XP3_PATH)

    index_buf = bytearray(index)
    cursor = 0
    entry_idx = 0
    while cursor + 12 <= len(index_buf):
        tag = index_buf[cursor:cursor+4]
        sz = int.from_bytes(index_buf[cursor+4:cursor+12], 'little')
        chunk_end = cursor + 12 + sz
        if tag == b'File':
            if entry_idx in encrypted_blobs:
                info = encrypted_blobs[entry_idx]
                sub = cursor + 12
                while sub + 12 <= chunk_end:
                    sub_tag = index_buf[sub:sub+4]
                    sub_sz = int.from_bytes(index_buf[sub+4:sub+12], 'little')
                    b_start = sub + 12
                    sub += 12 + sub_sz
                    if sub_tag == b'adlr':
                        struct.pack_into('<I', index_buf, b_start, info['adler32'])
                    elif sub_tag == b'segm':
                        struct.pack_into('<IQQQ', index_buf, b_start, 0, info['offset'], info['size'], info['size'])
                    elif sub_tag in (b'Info', b'info'):
                        struct.pack_into('<QQ', index_buf, b_start + 4, info['size'], info['size'])
            entry_idx += 1
        cursor = chunk_end

    comp_new_index = zlib.compress(bytes(index_buf), level=9)
    new_index_offset = current_offset
    index_block = bytearray()
    index_block.append(0x01)
    index_block.extend(len(comp_new_index).to_bytes(8, 'little'))
    index_block.extend(len(index_buf).to_bytes(8, 'little'))
    index_block.extend(comp_new_index)

    with open(XP3_PATH, "r+b") as f:
        f.seek(old_file_size)
        f.write(blobs_stream)
        f.write(index_block)
        f.seek(0x20)
        f.write(new_index_offset.to_bytes(8, 'little'))
        f.flush()

    print(f"   + Đã ghi thành công! Dung lượng data.xp3 mới: {XP3_PATH.stat().st_size:,} bytes")
    print("======================================================================")
    print("     HOÀN TẤT ĐÓNG GÓI 100% THOẠI VIỆT HÓA + 15 UI TLG5 VÀO GAME!     ")
    print("======================================================================")

if __name__ == "__main__":
    main()
