# Báo cáo cá nhân — Đỗ Thị Thu Hằng-2A202603840

## 1. Thông tin thành viên

- Họ tên: Đỗ Thị Thu Hằng
- MSSV: 2A202603840
- Email: 26ai.hangdtt@vinuni.edu.vn

## 2. Phần việc phụ trách

Kỹ sư Công cụ & Kiểm thử (Tool Developer & QA).

- File làm chủ: `tools/wiki/` (`tool.py`, `TOOL.md`), `tools/__init__.py`, `tests/test_tools_todo.py`.
- Giai đoạn 1: viết tool mới `wiki`, đăng ký vào `TOOL_FUNCTIONS`, gửi cấu hình YAML cho Thành viên 1.
- Giai đoạn 2: viết unit test cho tool `wiki` (happy path, input sai, lỗi mạng/API).
- Giai đoạn 3 (Challenge Step 4b): điền các test đang `pytest.skip(TODO)` cho các tool có sẵn bằng fixture `fake_http`.

## 3. Đóng góp cụ thể

### 3.1. Tool mới `wiki`

- `tools/wiki/tool.py`: hàm `wiki_summary(title, lang)` gọi Wikipedia REST API (`/api/rest_v1/page/summary/<title>`), không cần API key.
- Chỉ nhận `lang` là `vi` hoặc `en`, mặc định `vi`.
- Chuẩn hoá tiêu đề (thay khoảng trắng bằng `_`, mã hoá URL) và thêm `User-Agent` theo yêu cầu của Wikipedia.
- Cắt `extract` tối đa 2000 ký tự.
- Mọi trường hợp lỗi đều trả error dict, không raise exception: input rỗng hoặc sai kiểu, `lang` ngoài enum, 404 (`NotFound`), lỗi HTTP, lỗi mạng.
- Output `items` dùng cùng format (title, url, source, summary) với các tool khác, nên đưa thẳng vào `format` được.
- `tools/wiki/TOOL.md`: mô tả theo đúng chuẩn frontmatter (name, track, kind, provider, inputs, outputs, side_effect), nêu rõ khi nào nên và không nên dùng.

### 3.2. Đăng ký và khai báo tool

- Thêm `wiki` vào `TOOL_FUNCTIONS` trong `tools/__init__.py`.
- Viết khai báo `wiki` trong `tools.yaml` (mô tả, enum `lang`, hướng dẫn phân biệt với `lookup`, `timeline`, `social_search`, `fetch`).
- Giữ tên tool đồng bộ giữa 3 nơi: `tools.yaml`, `__init__.py`, `data/eval_*.json`.
- Tinh chỉnh mô tả các tool khác trong `tools.yaml` (v2): ép `clarify` luôn set `response_type`, ràng buộc `send` phải qua `yes_no` trước khi gửi, làm rõ ranh giới giữa `lookup`, `timeline`, `social_search`.

### 3.3. Kiểm thử (`tests/test_tools_todo.py`)

Tool `wiki` có 6 test:

- Happy path: kiểm tra URL, header, mapping kết quả.
- `title` rỗng, `None` hoặc sai kiểu: trả lỗi `ValueError`, không gọi mạng.
- `lang` ngoài enum: trả lỗi, không gọi mạng.
- 404: trả `NotFound`, `items` rỗng.
- Lỗi HTTP 500: trả `HTTPError`.
- Lỗi mạng: trả `ConnectionError`.

### 3.4. Chạy đánh giá

Chạy bộ eval `base` (`data/eval_base.json`, 20 case: routing đúng tool, đúng tham số, hỏi lại khi thiếu thông tin, xác nhận trước khi gửi, câu ngoài phạm vi, hội thoại nhiều lượt) với model `gpt-4o-mini` trên hai phiên bản artifact:

- `v2_B_base_openai_20261110T170502898861.json` (artifact `v2+pcb7d99988f19+t830c7b51fb53`)
- `v4_B_base_openai_20261110T171347731125.json` (artifact `v4+p7a8b41e2a916+tbe9873182296`)

| Chỉ số | v2 | v4 |
|---|---|---|
| Số case đo được | 20/20 | 20/20 |
| Case đạt | 20 | 19 |
| Case accuracy | 100% | 95% |
| Tool routing accuracy | 100% | 100% |
| Argument accuracy | 100% | 95% |
| Multi-turn accuracy | 100% | 100% |
| Lỗi provider | 0 | 0 |

**Nhận xét**

- Cả hai phiên bản đều chọn đúng tool ở 20/20 case, kể cả các case khó như tách `timeline` và `social_search`, gọi song song `lookup` + `social_search`, và các case hội thoại nhiều lượt (mang timeframe sang lượt sau, sửa handle, sửa limit, đổi tool).
- v4 có 1 case thất bại: `R12_confirm_before_send` (input "Đăng bản tin này lên Telegram giúp mình"). Model gọi đúng tool `clarify` nhưng đặt `response_type="text"` (hỏi nội dung cần đăng) thay vì `"yes_no"` (xác nhận trước khi gửi). Loại lỗi: `wrong_boundary`, kiểu sai lệch: `wrong_arg_value`. Ở v2, cùng case này đạt với `response_type="yes_no"`.
- Vì vậy v4 không cải thiện so với v2 trên bộ base mà còn kém hơn 1 case (95% so với 100%). Do v2 đã đạt 100% nên bộ base không còn chỗ để cải thiện, và khác biệt chủ yếu nằm ở độ ổn định của việc chọn `response_type` ở tình huống có thể hiểu theo hai cách (thiếu nội dung hay cần xác nhận).
- Bộ base không có case nào kiểm tra tool `wiki`, nên kết quả này chưa phản ánh trực tiếp tác động của tool mới; việc kiểm tra `wiki` dựa vào 6 unit test ở mục 3.3.


## 4. Bằng chứng

- File/commit/PR (ngày 11/11/2026, tài khoản ThuHang2604):
  - `b153794`: Add Wikipedia summary lookup tool
  - `f90607e`: Document Wikipedia summary tool
  - `2228ba8`: Register Wikipedia summary tool
  - `6b3e0ac`: Implement tool behavior tests and Wikipedia coverage
  - `e59161d`: Add v2 and v4 baseline OpenAI evaluation runs
  - `27ce197`: Refine tool declarations and add Wikipedia tool
- File liên quan:
  - `starter_v0/tools/wiki/tool.py`
  - `starter_v0/tools/wiki/TOOL.md`
  - `starter_v0/tools/__init__.py`
  - `starter_v0/artifacts/tools.yaml`
  - `starter_v0/tests/test_tools_todo.py`
  - `starter_v0/runs/v2_B_base_openai_20261110T170502898861.json`
  - `starter_v0/runs/v4_B_base_openai_20261110T171347731125.json`
- AI/công cụ đã dùng và cách tự kiểm tra kết quả:
  - AI gợi ý viết TOOL.md
  - Chạy `pytest tests/ -v` để xác nhận 0 failed, 0 skipped.
  - Chạy `pytest tests/test_tool_contract.py` để kiểm tra tên tool đồng bộ giữa YAML, code và dữ liệu eval.
  - Mock HTTP bằng `fake_http` để test offline, không phụ thuộc mạng.
  - Đối chiếu kết quả eval v2 với v4 để xem thay đổi khai báo tool có cải thiện hay không.

## 5. Tự đánh giá

- Đã hoàn thành tool `wiki` đầy đủ, giữ tên tool đồng bộ giữa YAML, code và dữ liệu eval.
- Qua bài lab này nhận thấy mô tả tool trong YAML ảnh hưởng trực tiếp đến việc model chọn đúng tool và đúng tham số; Mock HTTP giúp test ổn định, nhanh và không tốn API key.
