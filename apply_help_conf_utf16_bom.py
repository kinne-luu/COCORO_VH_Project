import subprocess
import shutil
from pathlib import Path

ROOT_DIR = Path(r"D:\Software\Antigravity\Project\Cocoro")
CONF_PATCH_DIR = ROOT_DIR / "COCORO_Patch_VietHoa" / "patch_data" / "conf"
CONF_PATCH_DIR.mkdir(parents=True, exist_ok=True)

# 1. Đọc temp_help_conf.txt gốc
txt_path = ROOT_DIR / "temp_help_conf.txt"
if not txt_path.exists():
    cmd = [
        str(ROOT_DIR / "tools" / "msg-tool" / "msg_tool.exe"),
        "export", "-t", "kirikiri-simple-crypt",
        str(ROOT_DIR / "extracted_data" / "data" / "entry_00606_525d.bin"),
        str(txt_path)
    ]
    subprocess.run(cmd, check=True)

raw_text = txt_path.read_text(encoding="utf-16le")
if raw_text.startswith("\ufeff"):
    raw_text = raw_text[1:]

TRANSLATIONS = [
    # 6 mục điều chỉnh mới
    (["autospeed"], "Cài đặt tốc độ chuyển câu khi ở chế độ Tự động"),
    (["readskip_on", "readskip_off", "readskip_help"], 'Chọn "On" để chỉ tự động tua nhanh qua các câu thoại đã đọc.'),
    (["bgmvolume", "bgmvolume_mute"], "Điều chỉnh âm lượng nhạc nền"),
    (["sevolume", "sevolume_mute"], "Điều chỉnh âm lượng hiệu ứng âm thanh"),
    (["cf_qsave_help"], "Hiển thị hộp thoại xác nhận trước khi Lưu nhanh"),
    (["cf_qload_help"], "Hiển thị hộp thoại xác nhận trước khi Tải nhanh"),

    # A. Tab Văn bản
    (["textspeed"], "Cài đặt tốc độ hiển thị chữ."),
    (["autovwait_help"], "Bật để chế độ Tự động chờ đọc hết giọng lồng tiếng mới chuyển sang câu tiếp theo."),
    (["automode_n", "autovwait_0"], "Bật để chế độ Tự động chờ đọc hết giọng lồng tiếng mới chuyển sang câu tiếp theo."),
    (["automode_v", "autovwait_1"], "Bật để chế độ Tự động chờ đọc hết giọng lồng tiếng mới chuyển sang câu tiếp theo (chỉ khi câu tiếp theo có lồng tiếng)."),
    (["automode_s", "autovwait_2"], "Chế độ Tự động sẽ chuyển câu theo tốc độ cài đặt mà không cần chờ hết giọng lồng tiếng."),
    (["ctrlskip_help"], "Bật/Tắt tính năng tua nhanh văn bản bằng phím Ctrl."),
    (["skipall", "skipread", "skipall_help"], "Bật/Tắt việc tiếp tục tua nhanh sau khi xuất hiện lựa chọn."),
    (["winopac"], "Điều chỉnh độ đậm / mờ của khung thoại trong game."),
    (["rtextcol_on", "rtextcol_off", "rtextcol_help"], "Đổi màu các câu thoại đã đọc để dễ nhận biết."),
    (["skipspeed"], "Điều chỉnh tốc độ tua văn bản trong chế độ Skip."),
    (["speedsample"], "Khung hiển thị mẫu văn bản. Nhấp vào đây để đổi phông chữ."),

    # B. Tab Hiển thị & Hệ thống
    (["window", "fullscreen"], "Chuyển đổi giữa chế độ toàn màn hình và cửa sổ."),
    (["gamespeed", "drawspeed_help"], "Cài đặt tốc độ hoạt họa hình ảnh trong game."),
    (["vspeedsync"], "Đồng bộ tốc độ hiển thị chữ theo giọng nói nhân vật."),
    (["voicespeed", "voicespeed_help"], "Điều chỉnh tốc độ phát âm thanh giọng nói nhân vật."),
    (["touchmode"], "Bật/Tắt chế độ điều khiển cảm ứng cho màn hình cảm ứng."),
    (["lang_ui", "uilang_prev", "uilang_next", "uilang"], "Thay đổi ngôn ngữ hiển thị giao diện."),
    (["lang_text", "textlang_prev", "textlang_next", "textlang"], "Thay đổi ngôn ngữ văn bản trong game."),
    (["lang_sub"], "Thay đổi ngôn ngữ phụ đề hiển thị kèm theo."),

    # C. Tab Âm thanh
    (["wavevolume", "wavevolume_mute"], "Điều chỉnh âm lượng tổng thể của trò chơi."),
    (["voicevolume", "voicevolume_mute"], "Điều chỉnh âm lượng giọng nói của nhân vật."),
    (["movievolume", "movievolume_mute"], "Điều chỉnh âm lượng phim và video cắt cảnh."),
    (["sysvovolume", "sysvo_help"], "Điều chỉnh âm lượng giọng đọc hệ thống."),
    (["sysvo", "sysvosel_help"], "Chọn nhân vật lồng tiếng hướng dẫn trong menu hệ thống."),
    (["voicecut_help"], "Bật/Tắt tự động ngắt giọng nói khi chuyển sang câu tiếp theo."),
    (["voicecut_on"], "Bật/Tắt tự động ngắt giọng nói khi chuyển sang câu tiếp theo.\tGiọng lồng tiếng sẽ bị ngắt ngay khi chuyển sang câu thoại tiếp theo."),
    (["voicecut_off"], "Bật/Tắt tự động ngắt giọng nói khi chuyển sang câu tiếp theo.\tGiọng lồng tiếng sẽ phát hết trước khi chuyển sang câu thoại tiếp theo."),
    (["downvolume"], "Tự động hạ nhỏ nhạc nền khi nhân vật đang nói chuyện."),
    (["bgmdown"], "Tự động hạ nhỏ nhạc nền khi nhân vật đang nói chuyện."),
    (["bgmdown_on", "bgmdown_off"], "Tự động hạ nhỏ nhạc nền khi nhân vật đang nói chuyện."),
    (["charea", "help_chvoice"], "Điều chỉnh âm lượng giọng nói riêng cho từng nhân vật."),

    # D. Tab Hộp thoại xác nhận
    (["cf_title_help"], "Hiển thị hộp thoại xác nhận trước khi quay về màn hình chính."),
    (["cf_exit_help"], "Hiển thị hộp thoại xác nhận trước khi thoát trò chơi."),
    (["cf_load_help"], "Hiển thị hộp thoại xác nhận trước khi tải tệp lưu (Load)."),
    (["cf_overwrite_help"], "Hiển thị hộp thoại xác nhận trước khi ghi đè tệp lưu."),
    (["cf_delete_help"], "Hiển thị hộp thoại xác nhận trước khi xóa tệp lưu."),
    (["cf_jump_help"], "Hiển thị hộp thoại xác nhận trước khi chuyển đến câu trong lịch sử."),
    (["cf_next_help"], "Hiển thị hộp thoại xác nhận trước khi nhảy tới lựa chọn tiếp theo."),
    (["cf_init_help"], "Hiển thị hộp thoại xác nhận trước khi khôi phục cài đặt gốc."),
    (["cf_allremove1_help"], "Hiển thị hộp thoại xác nhận trước khi xóa toàn bộ dữ liệu lưu."),

    # E. Các nút điều khiển chung
    (["init"], "Đưa tất cả các cài đặt trên trang này về giá trị mặc định."),
    (["back"], "Đóng menu Cài đặt và quay trở lại màn hình trước."),
    (["page0"], "Điều chỉnh cài đặt Hiển thị."),
    (["page1"], "Điều chỉnh cài đặt Văn bản."),
    (["page2"], "Điều chỉnh cài đặt Hộp thoại."),
    (["page3"], "Điều chỉnh cài đặt Âm thanh."),
    (["page4"], "Điều chỉnh cài đặt Giọng nói."),
    (["page5"], "Điều chỉnh cài đặt Cảm ứng."),
    (["page6"], "Hiển thị danh sách phím tắt."),
    (["reset"], "Khôi phục trang này về cài đặt mặc định."),
    (["title"], "Quay về màn hình chính."),
    (["exit"], "Thoát trò chơi."),

    # F. Các mục bổ sung (tránh sót tiếng Anh trên mọi tab/nút)
    (["LANGFIXED"], "(Không thể thay đổi trong phiên bản này.)"),
    (["sqr_on", "sqr_off"], "Chuyển đổi tỷ lệ khung hình 4:3 hoặc 16:9."),
    (["noeffect_off", "noeffect_on"], "Bật/Tắt hiệu ứng hình ảnh."),
    (["bganim_on", "bganim_off"], "Bật hoạt ảnh trong các cảnh 18+."),
    (["mushide_none", "mushide_0", "mushide_3", "mushide_5", "mushide_10"], "Chọn thời gian hiển thị tên bài hát trên màn hình khi chơi."),
    (["stayontop_on", "stayontop_off"], "Khi bật, cửa sổ game sẽ luôn hiển thị ở trên cùng."),
    (["showvreplay"], "Hiển thị nút phát lại câu thoại lồng tiếng hiện tại."),
    (["showvsave"], "Hiển thị nút lưu lại các câu thoại yêu thích."),
    (["curmove_on", "curmove_off"], "Bật/Tắt tự động di chuyển con trỏ chuột trên màn hình xác nhận."),
    (["curmoveto_yes"], 'Con trỏ sẽ tự động đặt ở nút "Có" trên màn hình xác nhận.'),
    (["curmoveto_no"], 'Con trỏ sẽ tự động đặt ở nút "Không" trên màn hình xác nhận. (Khi xác nhận Lưu nhanh/Tải nhanh, con trỏ luôn đặt ở "Có".)'),
    (["curhide_none", "curhide_5", "curhide_10", "curhide_20"], "Cài đặt thời gian chờ trước khi con trỏ chuột tự ẩn đi khi không thao tác."),
    (["savequit"], 'Chọn "On" để tự động quay lại màn hình game ngay sau khi lưu.'),
    (["emotescale"], "Điều chỉnh mức độ chuyển động của nhân vật."),
    (["drama_on"], "Bật/Tắt Chế độ Rạp hát\tKhung thoại sẽ bị ẩn trong các cảnh có lồng tiếng khi bật chế độ Tự động."),
    (["drama_off"], "Bật/Tắt Chế độ Rạp hát\tKhung thoại vẫn hiển thị trong các cảnh có lồng tiếng khi bật chế độ Tự động."),
    (["use_speech"], "Liên kết với phần mềm đọc văn bản ngoài (TTS) để đọc các đoạn chưa lồng tiếng."),
    (["stopdeact_on"], "Cài đặt tạm dừng game khi ẩn cửa sổ.\tGame sẽ tạm dừng và tắt âm thanh."),
    (["stopdeact_off"], "Cài đặt tạm dừng game khi ẩn cửa sổ.\tGame vẫn tiếp tục chạy ngay cả khi ẩn cửa sổ."),
    (["icpreview_off", "icpreview_on"], "Bật/Tắt xem trước hình ảnh trên thanh tác vụ (Taskbar)."),
    (["ctrl_read", "ctrl_force"], 'Chọn "Tất cả" để bật tính năng tua nhanh toàn bộ chữ khi giữ phím Ctrl.'),
    (["afterskip_on", "afterskip_off"], 'Chọn "Có" để tiếp tục tua nhanh sau khi chọn một lựa chọn.'),
    (["afterauto_on", "afterauto_off"], 'Chọn "Có" để tiếp tục chế độ Tự động sau khi chọn một lựa chọn.'),
    (["skipstyle_n"], "Điều chỉnh cách tua nhanh cảnh/văn bản.\tTiếp tục hiển thị hình ảnh game bình thường khi đang tua."),
    (["skipstyle_t"], "Điều chỉnh cách tua nhanh cảnh/văn bản.\tẨn các yếu tố hình ảnh trong game khi đang tua."),
    (["bgv2volume", "bgv2volume_mute"], "Điều chỉnh âm lượng giọng nền."),
    (["voicetrans_off"], "Đặt ngôn ngữ lồng tiếng là tiếng Nhật."),
    (["voicetrans_on"], "Đặt ngôn ngữ lồng tiếng là tiếng Anh (lồng tiếng AI)."),
    (["sysvovolume_mute"], "Tắt giọng đọc hệ thống."),
    (["sysvotest"], "Nghe thử mẫu giọng đọc."),
    (["voicetest", "ch0_test"], "Nghe thử mẫu giọng nói nhân vật."),
    (["cf_backto_help"], "Hiển thị hộp thoại xác nhận trước khi quay lại lựa chọn trước đó."),
    (["prevjump_on", "prevjump_off"], 'Chọn điểm đến cho nút "PREV".'),
    (["cf_allremove2_help"], "Hiển thị hộp thoại xác nhận HAI LẦN trước khi xóa toàn bộ dữ liệu lưu."),
    (["cf_move_help"], "Hiển thị hộp thoại xác nhận trước khi di chuyển dữ liệu lưu."),
    (["cf_copy_help"], "Hiển thị hộp thoại xác nhận trước khi sao chép dữ liệu lưu."),
    (["touchimg_conf"], "Chạm bằng ba ngón tay để mở màn hình Cài đặt hệ thống."),
    (["touchimg_qmlock"], "Chạm bằng hai ngón tay để hiển thị các nút thao tác phóng to trên màn hình."),
    (["touchimg_backlog"], "Vuốt lên hoặc xuống để mở nhật ký thoại (Lịch sử)."),
]

lines = raw_text.splitlines()
out_lines = []
i = 0
modified_count = 0

while i < len(lines):
    line = lines[i]
    stripped = line.strip()
    
    if not line.startswith("\t") and stripped and not stripped.startswith("#"):
        keys_on_line = [k.strip() for k in stripped.split("\t") if k.strip()]
        
        matched_trans = None
        for rule_keys, new_vn in TRANSLATIONS:
            if any(rk in keys_on_line for rk in rule_keys):
                matched_trans = new_vn
                break
        
        out_lines.append(line)
        i += 1
        
        if i < len(lines) and lines[i].startswith("\t"):
            if matched_trans:
                out_lines.append(f"\t{matched_trans}")
                modified_count += 1
            else:
                out_lines.append(lines[i])
            i += 1
    else:
        out_lines.append(line)
        i += 1

print(f"[1/4] Đã thay thế thành công {modified_count} mục giải thích tiếng Việt!")

# Ghép bằng \r\n (CRLF)
final_text = "\r\n".join(out_lines) + "\r\n"

# Đóng gói định dạng UTF-16LE with BOM (0xFF, 0xFE) theo đúng lời khuyên của chuyên gia
# BOM + payload UTF-16LE
utf16_bom_bytes = b"\xff\xfe" + final_text.encode("utf-16le")

print(f"[2/4] Đã tạo tệp Plain Text UTF-16LE có BOM: {len(utf16_bom_bytes):,} bytes")
assert utf16_bom_bytes[:2] == b"\xff\xfe"

p606 = CONF_PATCH_DIR / "entry_00606.bin"
p608 = CONF_PATCH_DIR / "entry_00608.bin"

p606.write_bytes(utf16_bom_bytes)
p608.write_bytes(utf16_bom_bytes)
print(f"   + [CONF] Đã ghi {p606.name} ({len(utf16_bom_bytes):,} bytes)")
print(f"   + [CONF] Đã ghi {p608.name} ({len(utf16_bom_bytes):,} bytes)")

# 2b. Xử lý System Screen Language Text (entry_00636 EN & entry_00637 JP)
print("\n[2b/4] Việt hóa ConfigPreviewText & văn bản hệ thống (entry_00636/00637)...")
sys_txt_path = ROOT_DIR / "temp_sys_lang_636.txt"
subprocess.run([
    str(ROOT_DIR / "tools" / "msg-tool" / "msg_tool.exe"),
    "export", "-t", "kirikiri-simple-crypt",
    str(ROOT_DIR / "extracted_data" / "data" / "entry_00636_527b.bin"),
    str(sys_txt_path)
], check=True)

sys_raw = sys_txt_path.read_text(encoding="utf-16le")
if sys_raw.startswith("\ufeff"):
    sys_raw = sys_raw[1:]

SYS_REPLACEMENTS = {
    "SaveCommentInput": "Nhấp vào đây để nhập ghi chú.",
    "SaveCommentDialog": "Chỉnh sửa ghi chú cho ô ${num}.",
    "BacklogChoiceTextFormat": "LỰA CHỌN: ${text}",
    "ConfigPreviewText": "COCORO >>>>>>>>>>,Văn bản mẫu kiểm tra tốc độ hiển thị.",
    "DialogCancel": "Hủy",
    "DialogClose": "Đóng",
    "DialogInit": "Mặc định",
    "DialogDetail": "Chi tiết",
    "VersionInfo": "Thông tin phiên bản",
    "FontDialogCaption": "Chọn Phông Chữ",
    "FontDialogDoSelect": "Vui lòng chọn một phông chữ",
    "FontDialogLicenseHead": 'Thông tin bản quyền cho "${name}"',
    "FontDialogLicenseInfo": 'Nhấp "Chi tiết" để xem thông tin bản quyền phông chữ.',
    "FontDialogInfoFormat": "Chi tiết ${name}",
    "WarnChangeUserFont": "Lưu ý: Một số văn bản trong game có thể hiển thị không đúng nếu thay đổi phông chữ.",
}

sys_out_lines = []
sys_mod_count = 0
for line in sys_raw.splitlines():
    s = line.strip()
    if s and not s.startswith("#") and not s.startswith("!") and ("\t" in line):
        # Tách key (phần không khoảng trắng đầu tiên) và giữ phần tab ngăn cách
        parts = line.split("\t", 1)
        key = parts[0].strip()
        if key in SYS_REPLACEMENTS:
            sys_out_lines.append(f"{key}\t{SYS_REPLACEMENTS[key]}")
            sys_mod_count += 1
            continue
    sys_out_lines.append(line)

sys_final_text = "\r\n".join(sys_out_lines) + "\r\n"
sys_utf16_bytes = b"\xff\xfe" + sys_final_text.encode("utf-16le")

p636 = CONF_PATCH_DIR / "entry_00636.bin"
p637 = CONF_PATCH_DIR / "entry_00637.bin"
p636.write_bytes(sys_utf16_bytes)
p637.write_bytes(sys_utf16_bytes)
print(f"   + Đã cập nhật {sys_mod_count} mục trong System Screen Language Text!")
print(f"   + [CONF] Đã ghi {p636.name} ({len(sys_utf16_bytes):,} bytes)")
print(f"   + [CONF] Đã ghi {p637.name} ({len(sys_utf16_bytes):,} bytes)")

# 3. Chạy repack_viet_hoa_full.py (với segm flags = 0 uncompressed)
print("\n[3/4] Chạy repack_viet_hoa_full.py đóng gói vào data.xp3...")
subprocess.run(["C:\\Users\\ADMIN\\AppData\\Local\\Python\\bin\\python.exe", "repack_viet_hoa_full.py"], check=True)

# 4. Sao lưu
print("\n[4/4] Đồng bộ bản sao lưu data.xp3.viet_hoa.bak...")
game_xp3 = Path(r"E:\Games\COCORO.FIXED\game\data.xp3")
bak_xp3 = Path(r"E:\Games\COCORO.FIXED\game\data.xp3.viet_hoa.bak")
shutil.copy2(game_xp3, bak_xp3)
print(f"   + Đã sao lưu thành công sang {bak_xp3.name} ({bak_xp3.stat().st_size:,} bytes)!")

print("\n" + "=" * 70)
print("   HOÀN TẤT 100%! BẢN VÁ UTF-16LE WITH BOM ĐÃ SẴN SÀNG!   ")
print("=" * 70)
