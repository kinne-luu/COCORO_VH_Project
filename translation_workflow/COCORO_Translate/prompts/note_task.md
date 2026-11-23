# LỆNH GIAO VIỆC CHO AGENT: VIẾT GHI CHÚ BATCH
(Chạy ngay sau khi batch đã qua kiểm tra.)

## Nguyên tắc
- Viết dựa trên BẢN GỐC JP của batch vừa dịch, KHÔNG dựa trên ghi chú cũ (để lỗi không lan sang batch sau).
- CHỈ ghi sự kiện và trạng thái cốt truyện. KHÔNG nhận xét về cách dịch hay văn phong.
- Tối đa 80 từ.

## Việc cần làm
Thêm vào CUỐI file notes/{SCENE}.md đúng khuôn mẫu sau:

## Batch {BATCH_NO} | dòng {START}-{END}
- Sự kiện: (1-2 câu chuyện vừa xảy ra)
- Tâm trạng: (từng nhân vật có mặt, mỗi người một vế ngắn)
- Đã lộ/đã hứa/bỏ ngỏ: (điều vừa tiết lộ, lời hứa, câu hỏi còn treo)
- Tên/cách gọi mới: (tên, thuật ngữ, cách xưng hô chưa có trong glossary/address_table; nếu không có ghi "(không)")

Nếu mục "Tên/cách gọi mới" có nội dung, thêm mỗi mục một dòng vào notes/_review_queue.md theo dạng:
- [{SCENE}, batch {BATCH_NO}] "tên" - gốc: JP - gợi ý: ...

## Khi batch là batch CUỐI của scene
Viết thêm mục "## Tóm tắt scene" 3-5 câu (chỉ cốt truyện, không nhận xét dịch thuật) ở cuối file notes/{SCENE}.md.

## Điều cấm
- Không sửa các ghi chú cũ.
- Không sửa config/.
