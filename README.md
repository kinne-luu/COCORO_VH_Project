# COCORO — Technical Documentation & Vietnamese Localization Project

Engine: Kirikiri Z 32-bit `COCORO.exe`, KAG Framework, Frontwing HXV4 / CxdecV2

[Tiếng Việt](#tieng-viet) | [English](#english)

---

<a name="tieng-viet"></a>
## Tiếng Việt

### 1. Ghi chú về AI và hiện trạng dự án

- **Về việc dùng AI:** Dự án này sử dụng AI như một công cụ hỗ trợ trong quá trình nghiên cứu kỹ thuật, viết script và dịch thô, không phải thứ thay thế hoàn toàn hay dùng để làm màu.
- **Về mã nguồn các tool:** Vì phần lớn quá trình dịch ngược engine được thực hiện cùng AI và kết hợp thêm một số công cụ từ cộng đồng như `msg_tool`, `cxdec-hxv4` hay `DripProgram`, nên code Python trong đây có thể hơi rối và không được đẹp mắt. Mình đã cố gắng dọn dẹp lại gọn nhất có thể để một người bình thường hoặc AI khác nhìn vào vẫn đọc hiểu và dùng lại được.
- **Về file dịch `COCORO_Dialogue-chinh-sua.xlsx`:** Đây mới chỉ là bản dịch thô bằng AI chạy theo workflow riêng. Hiện tại bản dịch vẫn đang trong quá trình biên tập và hiệu đính kỹ càng, không có giá trị để sử dụng làm bản dịch chính thức.
- **Về file nén `COCORO_prj_archive.zip`:** Gói này chứa toàn bộ đống script thử nghiệm cũ, ảnh cắt ghép thô bằng AI để căn tọa độ UI và dữ liệu trung gian. Bạn có thể tải về vọc thử cho biết rồi vứt sọt rác cũng được, vì nó không có giá trị bằng phần tài liệu và bộ tool chính đã trình bày gọn bên trên.

---

### 2. Kiến trúc engine và 4 lỗi cần tránh khi build

Mỗi entry bên trong `data.xp3` và `video.xp3` được mã hóa XOR vi phân theo chuẩn Frontwing HXV4 bằng khóa Filter Runtime State 48-byte sinh từ máy ảo `DripProgram`.

#### A. Lỗi khối màu tím `#FF00FF` trên nút bấm UI
- **Nguyên nhân:** Plugin `PackinOne.dll` cắt ảnh UI theo tọa độ trong `.pbd` và bắt buộc ảnh phải ở định dạng TLG5 thuần nén LZSS với `mark = 0` cùng bảng `blocksize[]`. Nếu nạp PNG thô hoặc nén TLG5 sai chuẩn, game sẽ hiện ô vuông tím `#FF00FF`.
- **Cách xử lý:** Xuất ảnh PNG 32-bit RGBA rồi dùng `tools/msg-tool/msg_tool.exe` để chuyển sang TLG5 chuẩn. Toàn bộ ảnh TLG5 đã biên dịch sẵn nằm trong `tlg_msgtool/`.

#### B. Lỗi sai khóa Filter State HXV4
- **Nguyên nhân:** Một số script cũ đảo sai thứ tự byte trong cấu trúc 48-byte `FilterRuntimeState`, khiến game văng lỗi `TLG Read Error` khi đọc ảnh UI hoặc PBD.
- **Cách xử lý:** Dùng đúng cấu trúc chuẩn HXV4 sinh từ `DripProgram` gồm `boundary0` ở byte 0..8, `boundary1` ở byte 8..16, `split_offset` ở byte 16..24, `bulk_key` ở byte 24..40, `has_bulk` ở byte 44 và `null_mode` ở byte 45. Phần này đã được đồng bộ sẵn trong `repack_viet_hoa_full.py` và `COCORO_Patch_VietHoa/patcher_gui.py`.

#### C. Lỗi khi Load Game `Member "scenes" does not exist`
- **Nguyên nhân:** Trong header PSB dài 40 byte, con trỏ `offset_entries` tại byte 36 nằm trước bảng chuỗi `offset_strings`. Khi chèn thoại tiếng Việt dài hơn làm bảng chuỗi nở ra thêm `delta_data_end`, nếu cộng nhầm `delta_data_end` vào `offset_entries` thì root object sẽ bị lệch và crash lúc Load Game.
- **Cách xử lý:** Không bao giờ cộng `delta_data_end` vào `offset_entries`, chỉ cộng cho các trường chunk nằm sau bảng chuỗi ở vị trí index 6, 7 và 8.

#### D. Lỗi `Read error: option` tại `helptextman.tjs`
- **Nguyên nhân:** Các tệp cấu hình văn bản gốc như `help_conf.txt` hay `ConfigPreviewText` được đánh dấu nén ZLIB với `segm.flags = 1` trong chỉ mục XP3. Khi ghi đè dữ liệu thô chưa nén mà quên đặt lại `segm.flags = 0`, engine sẽ gọi `zlib inflate` lên dữ liệu raw và báo lỗi đọc. Ngoài ra, sửa tay mã hóa `SimpleCrypt Mode 1` rất dễ bị lệch căn chỉnh 2 byte.
- **Cách xử lý:** Đặt `segm.flags = 0` trong `repack_viet_hoa_full.py` và chạy `apply_help_conf_utf16_bom.py` để xuất thẳng các tệp cấu hình sang dạng Plain Text UTF-16LE có BOM `\xFF\xFE` với ngắt dòng CRLF.

---

### 3. Cấu trúc thư mục

```text
COCORO_VH_Project/
├── README.md                              Tài liệu kỹ thuật song ngữ
├── repack_viet_hoa_full.py                Script chính đóng gói 50 kịch bản, UI, PBD và Config vào data.xp3
├── pack_video.py                          Script chính đóng gói video WMV vào video.xp3
├── apply_help_conf_utf16_bom.py           Script xuất tooltip và text hệ thống UTF-16LE BOM rồi repack
├── formats/                               Module đọc ghi định dạng XP3, PSB và HXV4
├── tools/msg-tool/                        Công cụ dòng lệnh convert TLG5, PBD và SimpleCrypt
├── orig_fresh/                            File gốc sạch làm template cho msg_tool
├── tlg_msgtool/                           Các ảnh UI định dạng TLG5 đã chuyển đổi chuẩn
├── COCORO_Patch_VietHoa/                  Bộ cài đặt Patch GUI độc lập gồm patch_data và patcher_gui.py
├── translation_workflow/                  Workflow dịch thô bằng AI gồm prompts, config, notes và sổ tay xưng hô
├── UI_VietHoa_Preview/                    15 ảnh giao diện UI đã Việt hóa để xem trực tiếp
├── COCORO_Dialogue-chinh-sua.xlsx         Bản dịch thô bằng AI đang trong quá trình biên tập
└── COCORO_prj_archive.zip                 Kho lưu trữ script cũ, ảnh cắt ghép thử và dữ liệu trung gian
```

---

### 4. Lệnh build nhanh

```powershell
# Đóng gói toàn bộ kịch bản, UI, PBD và cấu hình vào data.xp3
python repack_viet_hoa_full.py

# Cập nhật lại tooltip, text hệ thống UTF-16LE BOM và đóng gói lại
python apply_help_conf_utf16_bom.py

# Đóng gói video WMV vào video.xp3
python pack_video.py
```

---

<a name="english"></a>
## English

### 1. AI Disclosure and Project Status

- **AI Usage:** AI was used strictly as an assistive tool for reverse engineering the engine, writing analysis and repacking scripts, and generating a rough initial translation. It is not meant as a full replacement or a gimmick.
- **Tool Code Quality:** Because most of the reverse engineering and Python tooling were written with AI alongside community tools such as `msg_tool`, `cxdec-hxv4`, and `DripProgram`, the code can be rough and unpolished. Everything has been cleaned up as much as possible so that both humans and other AI tools can read and reuse it without too much friction.
- **About `COCORO_Dialogue-chinh-sua.xlsx`:** This spreadsheet only holds a rough AI translation generated through a custom workflow. It is currently undergoing thorough human editing and proofreading, and should not be used as an official or final translation.
- **About `COCORO_prj_archive.zip`:** This zip holds all legacy experimental files, including 65 auxiliary Python scripts, rough AI-cropped UI assets used for pixel alignment, and intermediate workflow logs. Feel free to inspect or discard it, as it carries much less value than the clean tools and documentation in the main directory.

---

### 2. Engine Notes and 4 Core Pitfalls

Every entry inside `data.xp3` and `video.xp3` uses Frontwing HXV4 differential XOR encryption driven by a 48-byte Filter Runtime State generated from the `DripProgram` VM.

#### A. Purple `#FF00FF` Blocks on UI Buttons
- **Cause:** `PackinOne.dll` slices UI atlases using `.pbd` coordinates and strictly requires pure LZSS-compressed TLG5 with `mark = 0` and a valid `blocksize[]` table. Feeding raw PNGs or malformed TLG5 headers falls back to solid `#FF00FF`.
- **Fix:** Export 32-bit RGBA PNGs and convert them with `tools/msg-tool/msg_tool.exe`. Validated TLG5 atlases are stored in `tlg_msgtool/`.

#### B. HXV4 Filter State Mismatch
- **Cause:** Earlier scripts swapped byte offsets inside the 48-byte `FilterRuntimeState`, triggering `TLG Read Error`.
- **Fix:** Follow the exact `DripProgram` layout with `boundary0` at 0..8, `boundary1` at 8..16, `split_offset` at 16..24, `bulk_key` at 24..40, `has_bulk` at 44, and `null_mode` at 45. This is already synced in `repack_viet_hoa_full.py` and `COCORO_Patch_VietHoa/patcher_gui.py`.

#### C. `Member "scenes" does not exist` on Save Load
- **Cause:** In the 40-byte PSB header, `offset_entries` at byte 36 sits before the string table `offset_strings`. Expanding the string table shifts downstream chunks by `delta_data_end`, not `offset_entries`.
- **Fix:** Never add `delta_data_end` to `offset_entries`; only update chunk indices 6, 7, and 8.

#### D. `Read error: option` in `helptextman.tjs`
- **Cause:** Original text configs such as `help_conf.txt` and `ConfigPreviewText` have `segm.flags = 1` for ZLIB compression in the XP3 index. Overwriting them with uncompressed data while keeping `segm.flags = 1` makes the engine run `zlib inflate` on raw text. Manual `SimpleCrypt Mode 1` edits can also break 2-byte UTF-16 alignment.
- **Fix:** Set `segm.flags = 0` in `repack_viet_hoa_full.py` and use `apply_help_conf_utf16_bom.py` to write Plain Text UTF-16LE with BOM `\xFF\xFE` and CRLF line endings.

---

### 3. Directory Layout

```text
COCORO_VH_Project/
├── README.md                              Bilingual technical documentation
├── repack_viet_hoa_full.py                Main script to pack 50 scenarios, UI, PBD, and Config into data.xp3
├── pack_video.py                          Main script to pack WMV videos into video.xp3
├── apply_help_conf_utf16_bom.py           Exports UTF-16LE BOM tooltips and system text, then repacks
├── formats/                               XP3, PSB, and HXV4 format handlers
├── tools/msg-tool/                        CLI tool for TLG5, PBD, and SimpleCrypt conversion
├── orig_fresh/                            Clean original templates for msg_tool compilation
├── tlg_msgtool/                           Validated TLG5 UI atlases
├── COCORO_Patch_VietHoa/                  Standalone GUI Patcher folder containing patch_data and patcher_gui.py
├── translation_workflow/                  AI translation workflow with prompts, config, notes, and pronoun guide
├── UI_VietHoa_Preview/                    15 completed Vietnamese UI PNGs for direct preview
├── COCORO_Dialogue-chinh-sua.xlsx         Rough AI translation spreadsheet under active proofreading
└── COCORO_prj_archive.zip                 Legacy archive with old scripts, rough AI crops, and raw workflow
```

---

### 4. Quick Build Commands

```powershell
# Pack scenarios, UI, PBD, and config into data.xp3
python repack_viet_hoa_full.py

# Rebuild UTF-16LE BOM tooltips/system text and repack
python apply_help_conf_utf16_bom.py

# Pack WMV videos into video.xp3
python pack_video.py
```
