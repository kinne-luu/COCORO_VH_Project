# COCORO — Technical Documentation & Vietnamese Localization Project
# COCORO — Tài liệu Kỹ thuật & Dự án Việt hóa

> **Repository:** `https://github.com/kinne-luu/COCORO_VH_Project`  
> **Engine:** Kirikiri Z (32-bit `COCORO.exe`, KAG Framework) + Frontwing HXV4 / CxdecV2

[English](#english-version) | [Tiếng Việt](#tiếng-việt)

---

<a name="tiếng-việt"></a>
## 🇻🇳 TIẾNG VIỆT

### 1. Tuyên bố minh bạch về AI & Trạng thái Dự án (ĐỌC KỸ)

- **Về việc sử dụng AI:** Dự án này sử dụng AI làm **công cụ hỗ trợ kỹ thuật** (Reverse Engineering cấu trúc engine, viết script phân tích/đóng gói, hỗ trợ dịch thô), **không phải** công cụ thay thế hoàn toàn hay dùng để làm màu.
- **Về chất lượng mã nguồn các Tool:** Do quá trình Reverse Engineering (RE) và đóng gói được thực hiện với sự hỗ trợ của AI, kết hợp cùng một số công cụ/mã nguồn tham khảo từ cộng đồng (`msg_tool`, `cxdec-hxv4` / `DripProgram`...), nên cấu trúc code trong các script `.py` có thể hơi rối rắm, chưa tối ưu hay đẹp mắt như phần mềm thương mại. Tác giả đã cố gắng dọn dẹp và sắp xếp lại gọn nhất có thể để **một người bình thường (và cả AI)** đều có thể đọc hiểu và sử dụng lại được.
- **Cảnh báo về file dịch `.xlsx` (`COCORO_Dialogue-chinh-sua.xlsx`):**
  > ⚠️ **LƯU Ý QUAN TRỌNG:** File Excel này mới chỉ là **bản dịch thô bằng AI** được tạo ra theo một workflow riêng. Hiện tại bản dịch **vẫn đang trong quá trình biên tập và hiệu đính kỹ càng**, **KHÔNG có giá trị để sử dụng làm bản dịch hoàn chỉnh/chính thức**.
- **Về file nén `COCORO_prj_archive.zip`:**
  > 📦 File zip này chứa toàn bộ đống lịch sử thử nghiệm cũ (65 script `.py` phụ trợ, ảnh cắt ghép thô bằng AI để dò tọa độ khớp với UI game, và toàn bộ workflow dịch thô). Bạn có thể tải về để vọc vạch, tham khảo cách làm rồi vứt sọt rác — nó **không có giá trị kỹ thuật cao** bằng bộ tài liệu và các script chính được trình bày gọn gàng ở thư mục gốc.

---

### 2. Kiến trúc Engine & 4 Bài học Kỹ thuật Cốt lõi (Tránh lỗi khi Build)

- **Cơ chế mã hóa:** Frontwing **HXV4 / CxdecV2**. Mỗi entry trong `data.xp3` và `video.xp3` được mã hóa XOR vi phân bằng khóa **Filter Runtime State 48-byte** sinh từ máy ảo `DripProgram`.

#### A. Lỗi khối màu tím (`#FF00FF`) trên nút bấm UI
- **Nguyên nhân:** Plugin `PackinOne.dll` (`tlgSliceLoader.dll`) cắt ảnh UI theo tọa độ trong `.pbd` và **bắt buộc ảnh phải là TLG5 thuần nén LZSS (`mark = 0`)** có bảng `blocksize[]`. Nếu nạp PNG thô hoặc nén TLG5 sai chuẩn, game sẽ hiện khối tím `#FF00FF`.
- **Giải pháp:** Xuất PNG 32-bit RGBA và dùng `tools/msg-tool/msg_tool.exe` (tích hợp `libtlg-rs`) để convert sang TLG5 chuẩn (đã biên dịch sẵn trong `tlg_msgtool/`).

#### B. Lỗi sai khóa Filter State HXV4 (`TLG Read Error`)
- **Nguyên nhân:** Thứ tự byte của cấu trúc 48-byte `FilterRuntimeState` trong bản cũ bị đảo sai cho UI/PBD.
- **Giải pháp:** Dùng đúng cấu trúc chuẩn HXV4 sinh từ `DripProgram` (`0..8: boundary0`, `8..16: boundary1`, `16..24: split_offset`, `24..40: bulk_key`, `44: has_bulk`, `45: null_mode`) — đã đồng bộ trong `repack_viet_hoa_full.py` và `COCORO_Patch_VietHoa/patcher_gui.py`.

#### C. Lỗi khi Load Game (`Member "scenes" does not exist`)
- **Nguyên nhân:** Trong header PSB (40 bytes), con trỏ `offset_entries` (byte 36) nằm **trước** bảng chuỗi (`offset_strings`). Khi chèn thoại tiếng Việt dài hơn làm bảng chuỗi nở ra một lượng `delta_data_end`, việc cộng nhầm `delta_data_end` vào `offset_entries` làm gãy root object.
- **Quy tắc vàng:** **Tuyệt đối không cộng `delta_data_end` vào `offset_entries`**, chỉ cộng cho các chunk nằm sau bảng chuỗi (indices 6, 7, 8).

#### D. Lỗi `Read error: option` tại `helptextman.tjs`
- **Nguyên nhân:** Các file text cấu hình gốc (`help_conf.txt`, `ConfigPreviewText`) có `segm.flags = 1` (nén ZLIB) trong chỉ mục XP3. Khi ghi đè dữ liệu thô chưa nén mà quên đặt `segm.flags = 0`, engine gọi `zlib inflate` lên dữ liệu raw gây crash. Ngoài ra mã hóa `SimpleCrypt Mode 1` dễ lệch byte khi sửa thủ công.
- **Giải pháp:** Đặt `segm.flags = 0` trong `repack_viet_hoa_full.py` và dùng `apply_help_conf_utf16_bom.py` để xuất các tệp cấu hình dạng **Plain Text UTF-16LE có BOM (`\xFF\xFE`)**, ngắt dòng CRLF (`\r\n`).

---

### 3. Cấu trúc Thư mục Dự án (Bản gọn)

```text
COCORO_VH_Project/
├── README.md                              # Tài liệu kỹ thuật song ngữ (file này)
├── repack_viet_hoa_full.py                # SCRIPT CHÍNH: Đóng gói 50 kịch bản + UI + PBD + Config vào data.xp3
├── pack_video.py                          # SCRIPT CHÍNH: Đóng gói video WMV vào video.xp3
├── apply_help_conf_utf16_bom.py           # SCRIPT CHÍNH: Xuất tooltip & text hệ thống UTF-16LE BOM rồi đóng gói
├── formats/                               # Module xử lý định dạng (XP3, PSB, HXV4...)
├── tools/msg-tool/                        # Công cụ convert TLG5 / PBD / SimpleCrypt
├── orig_fresh/                            # Mẫu gốc sạch để msg_tool làm template biên dịch
├── tlg_msgtool/                           # Các file ảnh UI định dạng TLG5 chuẩn
├── COCORO_Patch_VietHoa/                  # Bộ cài đặt Patch GUI độc lập (chứa patch_data/ & patcher_gui.py)
├── translation_workflow/                  # Workflow dịch thuật AI (prompts, config, notes, sổ tay xưng hô)
├── UI_VietHoa_Preview/                    # 15 ảnh giao diện UI đã Việt hóa hoàn chỉnh (xem trực tiếp)
├── COCORO_Dialogue-chinh-sua.xlsx         # Bản dịch thô bằng AI (ĐANG BIÊN TẬP, chưa phải bản chính thức)
└── COCORO_prj_archive.zip                 # Kho lưu trữ toàn bộ script cũ, ảnh cắt ghép AI & workflow thô (có thể bỏ)
```

---

### 4. Hướng dẫn Build nhanh (Dành cho người dùng & AI)

1. **Đóng gói toàn bộ vào `data.xp3`** (cần có game gốc tại đường dẫn cấu hình trong script):
   ```powershell
   python repack_viet_hoa_full.py
   ```
2. **Cập nhật lại Tooltip / Text hệ thống (UTF-16LE BOM) và tự động repack:**
   ```powershell
   python apply_help_conf_utf16_bom.py
   ```
3. **Đóng gói Video (WMV) vào `video.xp3`:**
   ```powershell
   python pack_video.py
   ```

---
---

<a name="english-version"></a>
## 🇬🇧 ENGLISH VERSION

### 1. AI Usage Disclosure & Project Status (PLEASE READ)

- **About AI Usage:** AI was used strictly as a **technical assistant** (Reverse Engineering the game engine, writing analysis/repacking scripts, and assisting with rough draft translation) — **not** as a replacement for human work or for show.
- **About Tool Code Quality:** Because Reverse Engineering (RE) and tooling were largely written with AI assistance alongside community-sourced tools/crates (`msg_tool`, `cxdec-hxv4` / `DripProgram`, etc.), the Python scripts may look messy or unpolished compared to commercial software. Everything has been cleaned up and organized as neatly as possible so that **a normal human (as well as AI)** can read, understand, and reuse it.
- **Warning about the `.xlsx` file (`COCORO_Dialogue-chinh-sua.xlsx`):**
  > ⚠️ **IMPORTANT:** This Excel file is strictly a **rough AI-generated translation** produced via a custom workflow. It is **currently undergoing thorough human editing/proofreading** and is **NOT suitable for use as an official/final translation**.
- **About `COCORO_prj_archive.zip`:**
  > 📦 This archive contains all legacy experimental artifacts (65 auxiliary `.py` scripts, rough AI-cropped/stitched images used to align UI coordinates, and the raw translation workflow). Feel free to download it, experiment with it, and throw it in the trash — it holds **far less technical value** than the clean structure and core documentation presented above.

---

### 2. Engine Architecture & 4 Core Technical Lessons (Error Prevention)

- **Encryption:** Frontwing **HXV4 / CxdecV2**. Every entry in `data.xp3` and `video.xp3` is XOR-encrypted using a **48-byte Filter Runtime State** generated by the `DripProgram` VM.

#### A. Purple Blocks (`#FF00FF`) on UI Buttons
- **Root Cause:** `PackinOne.dll` (`tlgSliceLoader.dll`) slices UI atlases via `.pbd` coordinates and **strictly requires pure LZSS-compressed TLG5 (`mark = 0`)** with a valid `blocksize[]` table. Raw PNGs or malformed TLG5 headers cause Kirikiri to fall back to solid `#FF00FF`.
- **Solution:** Export 32-bit RGBA PNGs and convert them using `tools/msg-tool/msg_tool.exe` (`libtlg-rs`). Pre-built valid TLG5 files are stored in `tlg_msgtool/`.

#### B. HXV4 Filter State Mismatch (`TLG Read Error`)
- **Root Cause:** An earlier `FilterRuntimeState` implementation had swapped byte offsets.
- **Solution:** Use the exact 48-byte HXV4 layout from `DripProgram` (`0..8: boundary0`, `8..16: boundary1`, `16..24: split_offset`, `24..40: bulk_key`, `44: has_bulk`, `45: null_mode`), already unified in `repack_viet_hoa_full.py` and `COCORO_Patch_VietHoa/patcher_gui.py`.

#### C. Crash on Load Game (`Member "scenes" does not exist`)
- **Root Cause:** In the 40-byte PSB header, `offset_entries` (byte 36) points to the root object **before** the string table (`offset_strings`). Expanding the string table shifts subsequent chunk offsets by `delta_data_end`, **NOT** `offset_entries`.
- **Golden Rule:** **Never add `delta_data_end` to `offset_entries`** — only update chunk indices 6, 7, and 8.

#### D. `Read error: option` Crash in `helptextman.tjs`
- **Root Cause:** Original config text files (`help_conf.txt`, `ConfigPreviewText`) have `segm.flags = 1` (ZLIB compressed) in the XP3 index. Overwriting them with uncompressed data without resetting `segm.flags = 0` causes `zlib inflate` to fail at stream level. Manual `SimpleCrypt Mode 1` edits can also break 2-byte UTF-16 alignment.
- **Solution:** Force `segm.flags = 0` in `repack_viet_hoa_full.py` and use `apply_help_conf_utf16_bom.py` to output **Plain Text UTF-16LE with BOM (`\xFF\xFE`)** and CRLF (`\r\n`), which Kirikiri Z's `TVPCreateTextStreamForRead` reads natively without issues.

---

### 3. Repository Structure

```text
COCORO_VH_Project/
├── README.md                              # Bilingual technical documentation (this file)
├── repack_viet_hoa_full.py                # MASTER: Packs 50 scenarios + UI + PBD + Config into data.xp3
├── pack_video.py                          # MASTER: Packs WMV videos into video.xp3
├── apply_help_conf_utf16_bom.py           # MASTER: Exports UTF-16LE BOM tooltips/system text & repacks
├── formats/                               # Format parsers/builders (XP3, PSB, HXV4...)
├── tools/msg-tool/                        # CLI converter for TLG5 / PBD / SimpleCrypt
├── orig_fresh/                            # Clean original templates for msg_tool compilation
├── tlg_msgtool/                           # Validated TLG5 UI atlases
├── COCORO_Patch_VietHoa/                  # Standalone GUI Patcher release folder (patch_data/ & patcher_gui.py)
├── translation_workflow/                  # AI translation workflow (prompts, config, notes, pronoun guide)
├── UI_VietHoa_Preview/                    # 15 completed Vietnamese UI PNG atlases (direct preview)
├── COCORO_Dialogue-chinh-sua.xlsx         # Rough AI-translated script (WIP proofreading, NOT final)
└── COCORO_prj_archive.zip                 # Legacy archive (auxiliary scripts, AI-cropped UI, raw workflow - disposable)
```

---

### 4. Quick Build Commands

```powershell
# Pack full localization (scenarios, UI, PBD, config) into data.xp3
python repack_viet_hoa_full.py

# Rebuild UTF-16LE BOM tooltips/system texts & repack
python apply_help_conf_utf16_bom.py

# Pack WMV videos into video.xp3
python pack_video.py
```
