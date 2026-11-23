# HƯỚNG DẪN VẬN HÀNH WORKFLOW TỰ ĐỘNG HÓA HOÀN TOÀN (AUTORUN WORKFLOW)
> **Dành cho Antigravity (AGY):** Bất cứ khi nào người dùng nhắc tới file này hoặc yêu cầu "bắt đầu chạy tự động theo workflow", hãy thực hiện ngay lập tức chu trình khép kín dưới đây cho toàn bộ các scene còn lại cho tới khi kết thúc game.

---

## 1. CÂU LỆNH KÍCH HOẠT TỪ NGƯỜI DÙNG
Người dùng chỉ cần nhắn một trong các câu sau:
* `"Bắt đầu chạy tự động theo AUTORUN_WORKFLOW"`
* `"Chạy tự động từ Scene hiện tại đến hết game"`
* `"Kích hoạt workflow tự động"`

---

## 2. NGUYÊN TẮC DỊCH THUẬT & KIỂM DUYỆT BẮT BUỘC
Mọi dòng dịch do AGY tạo ra PHẢI TUÂN THỦ NGHIÊM NGẶT 5 chốt chặn sau:
1. **100% Tiếng Việt thuần túy:** Tuyệt đối không để lọt bất kỳ chữ Hán/Kanji/Hanzi (ví dụ: `受`, `的`, `了`...), chữ Kana Nhật, chữ Thái hay ký tự ngoại lai nào.
2. **Quy tắc Ngoặc:**
   - Lời thoại nói ra miệng (gốc có `「...」`): Dùng ngoặc kép `"..."`.
   - Giọng qua loa, bộ đàm, flycam, hồi tưởng: Dùng `<...>`.
   - Suy nghĩ, độc thoại nội tâm, lời dẫn chuyện: **TUYỆT ĐỐI KHÔNG DÙNG NGOẶC KÉP `"..."` VÀ KHÔNG DÙNG NGOẶC ĐƠN `(...)`**. Bỏ toàn bộ ngoặc, dịch thành câu văn xuôi bình thường.
3. **Mã Engine Game:** Bắt buộc giữ nguyên vẹn `%n;`, `\n`, `%R`, `%L`, `%C`, `⏎` đúng vị trí. Bỏ sạch furigana `[よみ]漢字`.
4. **Bảng Xưng Hô & Thuật Ngữ Chuẩn:**
   - Hinata x Dì Kirika: cháu - dì (gọi "dì Kirika", "Chủ nhiệm Kizuki").
   - Hinata x Cocoro: tôi - cậu (hoặc tôi - em). Cocoro xưng 'tôi' (ワタシ), gọi Hinata là 'ngài Hinata' / 'cậu Hinata' (ひなたさん) hoặc 'quý khách' (お客様).
   - Hinata x Kazane: tôi - cậu (gọi 'Ryuzaki', 'Mitsumine').
   - Hinata x Kosame: anh - em (gọi 'anh Hinata', 'Kosame' / 'bé Kosame').
   - Hinata x Daichi: tôi - cậu (Daichi xưng: tao - mày / thằng kia).
   - Hinata x Kotaro: cháu / tôi - chú Kotaro.
   - Thuật ngữ: hoa "Tuyết Trắng Mùa Hạ" (ナツノシラユキ), "Ách Tai" (厄災), "Phân khu 99" (エリア９９), "Đội Tiêu Trừ" (駆除隊), "Dự án Utopia" (ユートピア構想), "Jabberwock" (ジャバウォック), "Mutant Drone" (ミュータントドローン).

---

## 3. CHU TRÌNH TỰ ĐỘNG LẶP CHO TỪNG SCENE (SCENE-BY-SCENE LOOP)
Bắt đầu từ scene chưa hoàn thành đầu tiên (hiện tại là `scn00_24`) và chạy liên tục đến scene cuối cùng (`scn01_01`):

### Bước 1: Đọc dữ liệu Prompt đóng gói sẵn
* Đọc các file batch của scene đó từ thư mục `prompts_for_argon/{scene_id}/` (ví dụ `prompts_for_argon/scn00_24/scn00_24_b01.txt`).
* Nắm bắt tóm tắt bối cảnh và các nhân vật xuất hiện trong batch.

### Bước 2: Dịch thuật trực tiếp
* AGY trực tiếp dịch từng batch sang tiếng Việt giàu cảm xúc, tự nhiên, đúng ngữ cảnh và tuân thủ 100% quy tắc ở Mục 2.
* Ghi bản dịch vào file tương ứng: `out/{scene_id}_b{batch_num}.txt` (định dạng: `ID | Bản dịch`).

### Bước 3: Tự động chạy Kiểm tra (Auto-QA)
* Chạy lệnh kiểm tra từng batch:
  `python cocoro_tools.py check {scene_id} {batch_num}`
* Quét tự động bằng regex để đảm bảo: 0 chữ Hán, 0 lỗi ngoặc, đủ 100% số dòng.
* Nếu phát hiện lỗi: AGY tự động sửa lại ngay lập tức cho đến khi đạt `PASS (0 lỗi)`.

### Bước 4: Tự động Hợp nhất vào Excel (Auto-Merge)
* Chạy lệnh hợp nhất:
  `python cocoro_tools.py merge {scene_id}`
* Đồng bộ ngay sang file Excel ở thư mục gốc:
  `Copy-Item "COCORO_Translate\COCORO_Dialogue.xlsx" "..\COCORO_Dialogue.xlsx" -Force`

### Bước 5: Cập nhật Nhật ký & Trạng thái Dự án
* Tự động tạo tóm tắt diễn biến cốt truyện vào `notes/{scene_id}.md` (theo mẫu các file trước).
* Cập nhật số dòng hoàn thành vào `PROJECT_STATUS.md`.

### Bước 6: Tiếp tục Scene tiếp theo
* Chuyển tiếp ngay lập tức sang scene kế tiếp và lặp lại từ Bước 1 đến Bước 5 cho đến khi hoàn tất Scene `scn01_01`.
* Báo cáo tiến độ và bảng tổng kết cho người dùng sau mỗi cụm 3-5 scene hoặc khi toàn bộ game hoàn tất.
