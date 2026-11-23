# COCORO: Bộ công cụ dịch Nhật → Việt (dành cho AI/agent đọc)

Đọc file này TRƯỚC khi làm bất cứ việc gì. Mục tiêu: dịch `COCORO_Dialogue.xlsx` (12.867 dòng, 50 scene) sang tiếng Việt, nhất quán từ đầu đến cuối.

## Nguyên tắc cốt lõi
- Bạn KHÔNG có trí nhớ giữa các lượt. Mọi thứ cần nhớ nằm trong file; luôn đọc lại từ đĩa trước mỗi batch.
- Mỗi phiên làm MỘT scene, mỗi lần MỘT batch (khoảng 50-80 dòng), tối đa 5 batch/phiên.
- Tiếng Nhật là chuẩn. Tiếng Trung và Anh chỉ để tham khảo.

## Các file và vai trò
| File | Dùng để | Được sửa? |
|---|---|---|
| `config/rules.md` | Quy tắc dịch, xưng hô, văn phong, mã điều khiển, furigana | KHÔNG |
| `config/address_table.json` | Xưng hô theo cặp nhân vật và theo giai đoạn | KHÔNG |
| `config/glossary.json` | Tên riêng, thuật ngữ, tên người nói, mục `da_chot_mac_dinh` | KHÔNG |
| `prompts/scene_task.md` | Quy trình dịch một scene (làm theo từng bước) | KHÔNG |
| `prompts/note_task.md` | Cách viết ghi chú sau mỗi batch | KHÔNG |
| `notes/<scene>.md` | Ghi chú cốt truyện từng batch, tóm tắt scene | Chỉ thêm vào cuối |
| `notes/_review_queue.md` | Tên/cách gọi mới chờ người dùng duyệt | Chỉ thêm vào cuối |
| `cocoro_tools.py` | Công cụ: status, extract, check, merge | KHÔNG |
| `COCORO_Dialogue.xlsx` | File dữ liệu chính (sheet `All_Dialogues`) | Chỉ qua lệnh `merge` |
| `work/` | File nguồn từng batch (do `extract` tạo) | Tự sinh |
| `out/` | Bản dịch từng batch `out/<scene>_bNN.txt` | Bạn ghi |
| `backup/`, `logs/` | Sao lưu xlsx và nhật ký chạy | Tự sinh |

## Quy trình mỗi batch
1. `python cocoro_tools.py status <scene>`: xem batch nào chưa xong.
2. `python cocoro_tools.py extract <scene> N`: tạo `work/<scene>_bNN_src.txt` (có 5 dòng ngữ cảnh ở đầu, không dịch lại).
3. Đọc `config/*`, `notes/<scene>.md` (tóm tắt scene trước + ghi chú 1-2 batch gần nhất).
4. Dịch, ghi `out/<scene>_bNN.txt`, mỗi dòng đúng `ID | bản dịch`, đủ dòng, đúng thứ tự.
5. `python cocoro_tools.py check <scene> N`: phải PASS (lỗi thì sửa file out, tối đa 2 lần, vẫn lỗi thì dừng và báo).
6. `python cocoro_tools.py merge <scene> N`: ghi vào cột Vietnamese (cả `All_Dialogues` lẫn sheet scene).
7. Viết ghi chú theo `prompts/note_task.md`, rồi sang batch kế tiếp.

## Bắt buộc nhớ
- GIỮ NGUYÊN mã: `\n`, `%n;`, `%n;#00ff0000;`, `%130;`, `%80;`, `%R`, `%L`, `%C`, `⏎` (số lượng, thứ tự, vị trí).
- BỎ furigana dạng `[よみ]漢字` khỏi bản dịch.
- Chỉ dùng xưng hô theo `address_table.json` và `rules.md`. Gặp trường hợp chưa có thì dịch tạm và ghi vào `notes/_review_queue.md`, không tự đặt quy ước mới.
- Không tóm tắt, gộp, bỏ, thêm hay tách dòng. Không sửa file Excel trực tiếp. Không ghi đè ô Vietnamese đã có chữ.
- Báo cáo cuối phiên ngắn gọn: batch đã xong, số dòng, lỗi còn lại.

## Cho người dùng
1. Đặt `COCORO_Dialogue.xlsx` vào thư mục này (cạnh `cocoro_tools.py`), cài `pip install openpyxl`.
2. Mở agent ở thư mục này, dán `prompts/scene_task.md` với `{SCENE}` đã điền (ví dụ `scn00_01`). Chạy thử scene ngắn trước.
3. Đóng Excel khi chạy `merge`. Tên scene xem bằng `python cocoro_tools.py status`.
