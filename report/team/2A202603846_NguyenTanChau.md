## 1. Thông tin thành viên

- Họ tên: Nguyễn Tấn Châu
- MSSV: 2A202603846
- Email: 26ai.chaunt@vinuni.edu.vn

## 2. Phần việc phụ trách

Prompt engineer

## 3. Đóng góp cụ thể

- Bỏ chỉ dẫn xấu của starter trong `system_prompt.md` (v1)
- Thêm rule routing / phạm vi / luồng xác nhận gửi (v3, v5)
- Mỗi version một giả thuyết, chạy base eval, ghi metric trước/sau
- Bảng B1 và phần Reflection về prompt

> Tự viết thêm: mình đã làm cụ thể gì, quyết định nào là của mình, vì sao.

## 4. Bằng chứng

- `starter_v0/artifacts/system_prompt.md`
- `starter_v0/runs/v1_*, v3_*, v5_*`
- `version_log.csv` (dòng v1, v3, v5)
- group report B1, B6
- File/commit/PR: (điền hash commit)
- AI/công cụ đã dùng và cách tự kiểm tra kết quả: (tự điền — ví dụ dùng Claude để nháp X, tự kiểm tra bằng chạy `pytest` / đối chiếu run JSON)

## 5. Tự đánh giá

- **Điều học được:** Nắm vững quy trình tối ưu hóa prompt theo docs có trước: đọc log để bắt đúng lỗi, sau đó mới đặt giả thuyết sửa từng điểm một thay vì sửa theo cảm tính. Hiểu rõ sự phối hợp chặt chẽ giữa quy tắc điều hướng trong `system_prompt.md` và định nghĩa tham số trong `tools.yaml`.
- **Điều làm tốt:** Giữ đúng tiêu chí mỗi phiên bản một giả thuyết qua các vòng `v1`, `v3`, `v5`; loại bỏ triệt để các chỉ dẫn xấu ở bản gốc và ghi nhận đầy đủ mã hash, điểm số trước/sau vào `version_log.csv`.
- **Điều sẽ làm khác:** Setup môi trường và hướng dẫn các thành viên đồng đều để đảm bảo quy trình trơn tru. Sẽ phối hợp sớm hơn với thành viên làm Tool và viết Eval của nhóm ngay từ đầu để thống nhất biên giới (boundary) giữa các công cụ dễ gây nhầm lẫn (như `lookup` vs `social_search`, `timeline` và `social_search`), cũng như thử nghiệm thêm việc rút gọn prompt cho các mô hình local kích thước nhỏ (Small Local Model).
