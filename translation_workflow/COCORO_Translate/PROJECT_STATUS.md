# COCORO@FUNCTION - HỒ SƠ DỰ ÁN & BỘ NHỚ TRẠNG THÁI (PROJECT MEMORY)
> **Dành cho mọi phiên chat của Antigravity:** Bất cứ khi nào bắt đầu một cuộc trò chuyện mới, hãy đọc file này để nắm bắt 100% bối cảnh, quy chuẩn và tiến độ mà không cần hỏi lại người dùng.

---

## 1. MÔ HÌNH PHỐI HỢP DỰ ÁN (WORKFLOW)
* **Người dùng + Gemini 4 Argon / Hydrogen (AI Studio):** Đóng vai trò **Dịch giả chính (Translator)**.
  - Sử dụng prompt đóng gói sẵn trong thư mục `prompts_for_argon/`.
  - Kết quả dịch được lưu vào thư mục `out/` (ví dụ `out/scn00_05_b01.txt`).
* **Antigravity (AGY):** Đóng vai trò **Biên tập viên & Quản lý Pipeline (Editor & QA)**.
  - Đọc file từ `out/`, rà soát văn phong thuần Việt, kiểm tra xưng hô và dấu câu.
  - Đảm bảo các câu dẫn chuyện / suy nghĩ / độc thoại nội tâm **KHÔNG CÓ NGOẶC KÉP**.
  - Kiểm tra các mã engine (`%n;`, `\n`, `%R`, `%L`) nguyên vẹn.
  - Chạy `python cocoro_tools.py check <scene> <batch>`.
  - Chạy `python cocoro_tools.py merge <scene> <batch>`.
  - Cập nhật nhật ký vào `notes/<scene>.md`.
  - Đồng bộ file Excel: `Copy-Item "COCORO_Translate\COCORO_Dialogue.xlsx" "..\COCORO_Dialogue.xlsx" -Force`.

---

## 2. QUY CHUẨN DỊCH THUẬT CỐT LÕI
1. **Ngoặc & Dấu câu:**
   - Thoại nói ra miệng: dùng dấu ngoặc kép `"..."`.
   - Giọng qua loa / bộ đàm / flycam / hồi tưởng ký ức: dùng `<...>`.
   - Dẫn chuyện, suy nghĩ, độc thoại nội tâm: **TUYỆT ĐỐI KHÔNG DÙNG NGOẶC KÉP**.
   - Dấu ngắt quãng, suy tư: dùng `...` thay cho dấu gạch ngang dài `――`.
2. **Văn phong:**
   - Thuần Việt, tự nhiên, hiện đại. Tránh từ Hán-Việt sáo rỗng hoặc quá văn vẻ cổ phong (dùng "âm thanh", không dùng "thanh âm").
3. **Mã Engine:**
   - Bắt buộc giữ nguyên vẹn `%n;`, `\n`, `%R`, `%L`, `%C`, `⏎`. Bỏ sạch furigana `[よみ]漢字`.
4. **Xưng hô chuẩn xác (theo `config/address_table.json`):**
   - **Hinata - Kazane:** tôi – cậu. Hinata gọi "Ryuzaki" (họ), Kazane gọi "Mitsumine" (họ).
   - **Hinata - dì Kirika:** cháu – dì (gọi "dì Kirika", "Chủ nhiệm Kizuki").
   - **Hinata - Kosame:** anh – em (gọi "anh Hinata", "Kosame" / "bé Kosame").
   - **Kazane - Kosame:** chị – em (gọi "chị Kazane", "Kosame").
   - **Daichi x Hinata:** mày - tao / thằng kia (hung hăng, thù hận); Hinata x Daichi: tôi - cậu.
   - **Hinata x Đội Tiêu Trừ / Kotaro:** cháu / tôi - các chú / chú Kotaro.
   - **Hinata - Cocoro:** 
     + Giai đoạn đầu (early/hiện tại): tôi – cậu / tôi - em (lịch sự, khách sáo; Cocoro xưng tôi, gọi quý khách / ngài).
     + Hồi tưởng thuở nhỏ: Hinata gọi "người chị xinh đẹp / chị ấy", xưng em.
   - **Hinata - bà Tanaka:** cháu – bác Tanaka / bác.
   - **Thuật ngữ:** hoa "Tuyết Trắng Mùa Hạ" (Natsu no Shirayuki), "Tai ương" (厄災), "Phân khu 99" (エリア９９), "Đội Tiêu Trừ" (駆除隊), "Đội Điều Tra" (調査隊), "Dự án Utopia" (ユートピア構想), "Mutant Drone" (ミュータントドローン), "Thung lũng kỳ ảo" (不気味の谷 - Uncanny Valley).

---

## 3. TIẾN ĐỘ HIỆN TẠI (CẬP NHẬT ĐẾN NAY)
- `scn00_00.ks`: 11/11 dòng (100% - ĐÃ XONG)
- `scn00_01.ks`: 86/86 dòng (100% - ĐÃ XONG)
- `scn00_02.ks`: 290/290 dòng (100% - ĐÃ XONG)
- `scn00_03.ks`: 219/219 dòng (100% - ĐÃ XONG - Kết thúc Chương Mở Đầu / Prologue)
- `scn00_04.ks`: 327/327 dòng (100% - ĐÃ XONG - Kết thúc Chương 1)
- `scn00_05.ks`: 199/199 dòng (100% - ĐÃ XONG - Chuốt mới nhất & Re-merged)
- `scn00_06.ks`: 371/371 dòng (100% - ĐÃ XONG - Kết thúc Chương 2)
- `scn00_07.ks`: 132/132 dòng (100% - ĐÃ XONG - Đã merge vào Excel)
- `scn00_08.ks`: 190/190 dòng (100% - ĐÃ XONG - Đã merge vào Excel)
- `scn00_09.ks`: 347/347 dòng (100% - ĐÃ XONG - Kết thúc Chương 3)
- `scn00_10.ks`: 267/267 dòng (100% - ĐÃ XONG - Đã merge vào Excel)
- `scn00_11.ks`: 168/168 dòng (100% - ĐÃ XONG - Đã merge vào Excel)
- `scn00_12.ks`: 295/295 dòng (100% - ĐÃ XONG - Đã merge vào Excel)
- `scn00_13.ks`: 167/167 dòng (100% - ĐÃ XONG - Đã merge vào Excel)
- `scn00_14.ks`: 287/287 dòng (100% - ĐÃ XONG - Kết thúc Chương 4)
- `scn00_15.ks`: 416/416 dòng (100% - ĐÃ XONG - Kết thúc Chương 5)
- `scn00_16.ks`: 216/216 dòng (100% - ĐÃ XONG - Đã merge vào Excel)
- `scn00_17.ks`: 269/269 dòng (100% - ĐÃ XONG - Đã merge vào Excel)
- `scn00_18.ks`: 259/259 dòng (100% - ĐÃ XONG - Đã merge vào Excel)
- `scn00_19.ks`: 237/237 dòng (100% - ĐÃ XONG - Đã merge vào Excel)
- `scn00_20.ks`: 319/319 dòng (100% - ĐÃ XONG - Kết thúc Chương 6)
- `scn00_21.ks`: 356/356 dòng (100% - ĐÃ XONG - Kết thúc Chương 7)
- `scn00_22.ks`: 321/321 dòng (100% - ĐÃ XONG - Kết thúc Chương 8)
- `scn00_23.ks`: 473/473 dòng (100% - ĐÃ XONG - Kết thúc Chương 9)
- `scn00_24.ks`: 259/259 dòng (100% - ĐÃ XONG - Đã merge vào Excel)
- `scn00_25.ks`: 249/249 dòng (100% - ĐÃ XONG - Đã merge vào Excel)
- `scn00_26.ks`: 211/211 dòng (100% - ĐÃ XONG - Đã merge vào Excel)
- `scn00_27.ks`: 205/205 dòng (100% - ĐÃ XONG - Đã merge vào Excel)
- `scn00_28.ks`: 354/354 dòng (100% - ĐÃ XONG - Đã merge vào Excel)
- `scn00_29.ks`: 164/164 dòng (100% - ĐÃ XONG - Đã merge vào Excel)
- `scn00_30.ks`: 384/384 dòng (100% - ĐÃ XONG - Đã merge vào Excel)
- `scn00_31.ks`: 205/205 dòng (100% - ĐÃ XONG - Đã merge vào Excel)
- `scn00_32.ks`: 175/175 dòng (100% - ĐÃ XONG - Đã merge vào Excel)
- `scn00_33.ks`: 428/428 dòng (100% - ĐÃ XONG - Đã merge vào Excel)
- `scn00_34.ks`: 284/284 dòng (100% - ĐÃ XONG - Đã merge vào Excel)
- `scn00_35.ks`: 276/276 dòng (100% - ĐÃ XONG - Đã merge vào Excel)
- `scn00_36.ks`: 241/241 dòng (100% - ĐÃ XONG - Đã merge vào Excel)
- `scn00_37.ks`: 261/261 dòng (100% - ĐÃ XONG - Đã merge vào Excel)
- `scn00_38.ks`: 326/326 dòng (100% - ĐÃ XONG - Đã merge vào Excel)
- `scn00_39.ks`: 321/321 dòng (100% - ĐÃ XONG - Đã merge vào Excel)
- `scn00_40.ks`: 394/394 dòng (100% - ĐÃ XONG - Đã merge vào Excel)
- `scn00_41.ks`: 314/314 dòng (100% - ĐÃ XONG - Đã merge vào Excel)
- `scn00_42.ks`: 428/428 dòng (100% - ĐÃ XONG - Đã merge vào Excel)
- `scn00_43.ks`: 224/224 dòng (100% - ĐÃ XONG - Đã merge vào Excel)
- `scn00_44.ks`: 215/215 dòng (100% - ĐÃ XONG - Đã merge vào Excel)
- `scn00_45.ks`: 114/114 dòng (100% - ĐÃ XONG - Đã merge vào Excel)
- `scn00_46.ks`: 161/161 dòng (100% - ĐÃ XONG - Đã merge vào Excel)
- `scn00_47.ks`: 220/220 dòng (100% - ĐÃ XONG - Đã merge vào Excel)
- `scn00_48.ks`: 223/223 dòng (100% - ĐÃ XONG - Kết thúc Grand Epilogue, Đã merge vào Excel)
- `scn01_01.ks`: 9/9 dòng (100% - ĐÃ XONG - Kết thúc Bad Ending, Đã merge vào Excel)
- **TỔNG KẾT TOÀN BỘ DỰ ÁN:** **100% HOÀN TẤT (TẤT CẢ SCENE ĐÃ PASS 0 LỖI, MERGE THÀNH CÔNG VÀO EXCEL & ĐỒNG BỘ GỐC)**

---

## 4. CÂU LỆNH KHI BẮT ĐẦU CHAT MỚI
Chỉ cần nhắn cho Antigravity một trong các câu sau:
* `"Bắt đầu chạy tự động theo AUTORUN_WORKFLOW"` (AGY sẽ tự động dịch, kiểm duyệt và merge liên tục đến hết game).
* `"Đọc file PROJECT_STATUS.md và kiểm tra batch <scene> <batch> trong thư mục out/"`
* `"Đọc file PROJECT_STATUS.md và tiếp tục duyệt dịch"`
