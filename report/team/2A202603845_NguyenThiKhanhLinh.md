# Báo cáo cá nhân — Nguyễn Thị Khánh Linh — 2A202603845

## 1. Thông tin thành viên

- Họ tên: Nguyễn Thị Khánh Linh
- MSSV: 2A202603845
- Email: 26ai.linhntk@vinuni.edu.vn

## 2. Phần việc phụ trách

- Nghiên cứu cấu trúc bộ kiểm thử `data/eval_base.json`.
- Xây dựng 10 tình huống kiểm thử cho AI Agent, gồm 5 single-turn và 5 multi-turn.
- Thiết kế các tình huống kiểm tra khả năng lựa chọn Tool, xử lý thông tin thiếu và duy trì ngữ cảnh.
- Chạy đánh giá Agent bằng bộ kiểm thử của nhóm.

## 3. Đóng góp cụ thể

### 3.1. Kiểm tra môi trường và chạy thử agent

Tôi bắt đầu từ việc đối chiếu yêu cầu bài lab với cấu trúc dự án, sau đó kiểm
tra môi trường và chạy thử agent trong thư mục `starter_v0/`.

- Tôi kiểm tra bộ test có sẵn bằng `python -m pytest -q`, nhận kết quả
  **62 passed, 17 skipped, 0 failed**. Kết quả này xác nhận trạng thái của
  starter; các test TODO vẫn cần được hoàn thiện theo phạm vi bài làm.
- Tôi thử kết nối Gemini qua bước preflight. Khi gặp lỗi API `v1` không hỗ trợ
  function calling, tôi chuyển phiên chạy sang `GOOGLE_GENAI_API_VERSION=v1beta`.
  Preflight sau đó thành công với model `gemini-2.5-flash`.
- Tôi thực hiện hai lần chạy base eval v0, giữ nguyên prompt, tool declaration
  và bộ case. Ở lần thứ hai, tôi thử giãn các yêu cầu 15 giây để xử lý giới hạn
  số lần gọi API/phút.
- Khi kiểm tra log, tôi ghi nhận cả hai run đều có `total_cases=20`,
  `measured_cases=9`, `provider_error_cases=11`. Vì vậy, tôi chưa sử dụng các
  run này làm baseline hoặc dùng accuracy của phần case đã đo để so sánh v1–v3.
- Tôi xác định các trở ngại cần xử lý tiếp: quota Gemini 20 yêu cầu/ngày đã hết;
  các tool research báo thiếu `TAVILY_API_KEY`, `FIRECRAWL_API_KEY`,
  `RAPIDAPI_KEY`.

### 3.2. Phần việc cần tiếp tục hoàn thiện

Phần việc chính của tôi là xây dựng và đánh giá bộ kiểm thử của nhóm. Hiện
`starter_v0/data/eval_group.json` trong repo vẫn có `cases: []`, nên tôi chưa
có kết quả chạy suite group để đưa vào báo cáo. Tôi cần tiếp tục:

- Xây dựng 10 case theo schema: 5 single-turn và 5 multi-turn.
- Thiết kế tình huống lựa chọn tool, xử lý thông tin thiếu và duy trì ngữ cảnh.
- Bổ sung ít nhất 1 tình huống kiểm tra routing tới tool mới của nhóm.
- Kiểm tra JSON, chạy suite group bằng provider thật khi đủ quota, rồi phân
  tích PASS/FAIL từ run hợp lệ.

## 4. Bằng chứng

Tôi lưu các kết quả chạy và tài liệu liên quan để đối chiếu:

| Bằng chứng | Kết quả và phạm vi sử dụng |
|---|---|
| [Run v0 lần 1](../../starter_v0/runs/v0_B_base_gemini_20261110T190010047557.json) | 9/20 case được đo; 11 lỗi provider do quota yêu cầu/phút. Chỉ dùng chứng minh lỗi kỹ thuật. |
| [Run v0 lần 2](../../starter_v0/runs/v0_B_base_gemini_20261110T190608129312.json) | 9/20 case được đo; 9 lỗi `429` và 2 lỗi `503`. Log xác nhận hết quota ngày; chưa hợp lệ làm baseline. |
| [Ghi chú chạy Gemini](../../starter_v0/analysis/gemini_setup_notes.md) | Lệnh chạy, kết quả preflight, test và cách giãn thời điểm gọi API. |
| [Eval nhóm hiện tại](../../starter_v0/data/eval_group.json) | Chưa có case trong repo; cần bổ sung file hoàn chỉnh và run group. |

Commit/PR kỹ thuật cá nhân: tôi sẽ bổ sung khi hoàn thiện và commit phần việc.

AI/công cụ đã dùng: tôi sử dụng ChatGPT/Codex hỗ trợ đọc tài liệu, thực thi
lệnh, phân tích lỗi provider và biên tập báo cáo.

Cách kiểm tra kết quả: tôi đối chiếu số liệu với các trường `summary`,
`results[*].result.failures` và `tool_results` trong run JSON. Một run chỉ được
dùng làm bằng chứng đánh giá khi `provider_error_cases == 0` và
`measured_cases == total_cases`.

## 5. Tự đánh giá

- Tôi đã thực hiện bước kiểm tra môi trường, preflight và chạy thử eval.
  Phần xây dựng 10 case và đánh giá bằng suite group vẫn cần hoàn thiện.
- Qua các lần chạy, tôi nhận thấy cần phân biệt lỗi quota/provider với lỗi
  lựa chọn tool hoặc arguments. Một case PASS routing vẫn có thể có tool trả
  lỗi do thiếu API key.
- Tôi cần đối chiếu tên tool và tham số với các thành viên, hoàn thiện bộ
  kiểm thử, bổ sung commit/PR và thu kết quả chạy hợp lệ.
- Tôi sẽ tập trung cải thiện cách thiết kế tình huống multi-turn và phân tích
  log. Khi chưa có baseline hợp lệ, tôi chưa kết luận agent đã được cải thiện.
