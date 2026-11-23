# LỆNH GIAO VIỆC CHO AGENT: DỊCH 1 SCENE
(Mỗi phiên agent chỉ làm MỘT scene. Điền {SCENE} và {PHASE} rồi dán vào agent.)

## Thông tin
- Scene: {SCENE}   (ví dụ: scn00_02)
- Giai đoạn xưng hô: {PHASE}   (early / late / after; present / flashback). Nếu để trống: tự suy từ nội dung scene và notes/ của scene trước theo guide (Cocoro cứng nhắc, tôi–cậu → mềm dần, anh–em ở cuối/AFTER; hồi ức thì Hinata–Kazane gọi tên, hiện tại gọi họ), rồi GHI giai đoạn đã chọn vào đầu notes/{SCENE}.md để người dùng soát.
- Làm việc ở thư mục dự án (có cocoro_tools.py, COCORO_Dialogue.xlsx, config/, notes/)

## Bước 0: xem tiến độ
Chạy `python cocoro_tools.py status {SCENE}`.
Scene được chia sẵn thành các batch (khoảng 50-80 dòng, cắt ở chỗ đổi người nói). Làm các batch CHƯA "merged" theo thứ tự, mỗi lần MỘT batch.

## Với mỗi batch N, làm đúng thứ tự
1. Chạy `python cocoro_tools.py extract {SCENE} N` → tạo `work/{SCENE}_bNN_src.txt` (có sẵn 5 dòng ngữ cảnh ở đầu và các dòng cần dịch).
2. ĐỌC từ đĩa: config/rules.md, config/glossary.json, config/address_table.json (các cặp nhân vật có trong batch), và notes/{SCENE}.md (tóm tắt scene trước + ghi chú 1-2 batch gần nhất). Không dựa vào trí nhớ của phiên chat.
3. DỊCH các dòng sau "# --- CẦN DỊCH" theo rules.md. Tiếng Nhật là chuẩn; tiếng Trung và tiếng Anh chỉ để tham khảo.
4. GHI kết quả vào `out/{SCENE}_bNN.txt`: mỗi dòng đúng `ID | bản dịch`, đủ số dòng, đúng thứ tự, KHÔNG ghi lại các dòng ngữ cảnh.
5. Chạy `python cocoro_tools.py check {SCENE} N`.
   - Nếu FAIL: sửa đúng chỗ báo lỗi trong file out rồi chạy lại, tối đa 2 lần. Vẫn FAIL thì DỪNG, báo rõ lỗi.
   - Cảnh báo (CẢNH BÁO) thì đọc lại các dòng đó, sửa nếu thực sự sai.
6. Khi PASS, chạy `python cocoro_tools.py merge {SCENE} N` để ghi vào cột Vietnamese của file Excel.
7. Làm theo prompts/note_task.md để ghi chú batch này, rồi mới sang batch kế tiếp.

## Giới hạn mỗi phiên
- Làm tối đa 5 batch trong một phiên. Hết 5 batch mà scene chưa xong thì dừng, báo "còn dở ở batch N" để người dùng mở phiên mới.
- Khi batch cuối của scene xong: viết "Tóm tắt scene" (xem note_task.md) và báo hoàn thành.

## Điều cấm
- Không sửa config/, không sửa file Excel trực tiếp (chỉ qua lệnh merge), không sửa out/ của batch khác.
- Không tóm tắt, gộp, bỏ, thêm hay tách dòng.
- Không tự quyết tên riêng/xưng hô mới. Chưa có trong glossary/address_table thì dịch tạm theo ngữ cảnh và ghi vào mục "Tên/cách gọi mới" của ghi chú.
- Không ghi đè ô Vietnamese đã có nội dung (nếu merge báo xung đột thì DỪNG và báo lại).
- Báo cáo cuối ngắn gọn: các batch đã xong, số dòng, lỗi còn lại (nếu có).
