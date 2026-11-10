# Team

## Thông tin nhóm

- Tên nhóm: Nhomban2
- Lớp: L3B
- Repo nhóm: `K5-L3B-DAY03-Nhomban2-ResearchAgentToolEval` (xem [SUBMISSION.md](SUBMISSION.md))
- URL repo, nhánh nộp, commit chốt: (điền)
- Provider/model: `openai` / `gpt-4o-mini`

## Thành viên

| STT | Họ tên | MSSV | Email | GitHub | Vai trò |
| --: | ------ | ---- | ----- | ------ | ------- |
| 1 | Lê Quân Bảo | 2A202603888 | 26ai.baolq2@vinuni.edu.vn | LeBao403 | Nhóm trưởng — Setup + Baseline |
| 2 | Nguyễn Tấn Châu | 2A202603846 | 26ai.chaunt@vinuni.edu.vn |  | Prompt engineer |
| 3 | Đỗ Thị Thu Hằng | 2A202603840 | 26ai.hangdtt@vinuni.edu.vn | ThuHang2604 | Tool declaration + Tool mới |
| 4 | Nguyễn Thị Khánh Linh | 2A202603845 | 26ai.linhntk@vinuni.edu.vn | Xrkhanhlinh | Eval designer |
| 5 | Nguyễn Văn Quốc | 2A202603864 | 26ai.quocnv@vinuni.edu.vn | missher03 | UI + Demo |

## Cá nhân

Mỗi thành viên có báo cáo riêng trong `report/team/` theo dạng `MSSV_HoTen.md` (hiện đặt tên tạm `MSSV<i>_ThanhVien<i>.md`, đổi lại theo MSSV và họ tên thật).

## Lê Quân Bảo-2A202603888

### Phần việc phụ trách

- Nhóm trưởng — Setup + Baseline

### Đóng góp cụ thể

- Tạo repo nhóm, add thành viên, cấu hình `.env`, preflight + `pytest`
- Chạy baseline v0, ghi dòng v0 trong `starter_v0/artifacts/version_log.csv`
- Phân loại lỗi các case FAIL của v0 (bảng B2), mục 1 và mục 5 của group report
- Chốt commit cuối, kiểm tra không lộ secret, nộp bài

### Bằng chứng

- `TEAM.md`
- `starter_v0/runs/v0_*.json`
- `starter_v0/artifacts/version_log.csv` (dòng v0)
- `report/team/group_report.md` (B2)

## Nguyễn Tấn Châu-2A202603846

### Phần việc phụ trách

- Prompt engineer

### Đóng góp cụ thể

- Bỏ chỉ dẫn xấu của starter trong `system_prompt.md` (v1)
- Thêm rule routing / phạm vi / luồng xác nhận gửi (v3, v5)
- Mỗi version một giả thuyết, chạy base eval, ghi metric trước/sau
- Bảng B1 và phần Reflection về prompt

### Bằng chứng

- `starter_v0/artifacts/system_prompt.md`
- `starter_v0/runs/v1_*, v3_*, v5_*`
- `version_log.csv` (dòng v1, v3, v5)
- group report B1, B6

## Đỗ Thị Thu Hằng-2A202603840

### Phần việc phụ trách

- Tool declaration + Tool mới

### Đóng góp cụ thể

- Viết lại description mọi tool trong `tools.yaml`: khi nào dùng / không dùng, convention args, boundary `send` (v2)
- Viết tool mới `wiki` + `TOOL.md`, đăng ký `tools/__init__.py` + `tools.yaml` (v4)
- Viết ≥ 3 unit test cho tool mới, giữ `pytest` 0 failed
- Bonus: test challenge (điền hết stub, 0 skipped)

### Bằng chứng

- `starter_v0/artifacts/tools.yaml`
- `starter_v0/tools/wiki/`
- `starter_v0/tools/__init__.py`
- `starter_v0/tests/test_tools_todo.py`
- `starter_v0/runs/v2_*, v4_*`
- group report B5a, mục 3

## Nguyễn Thị Khánh Linh-2A202603845

### Phần việc phụ trách

- Eval designer

### Đóng góp cụ thể

- Viết 10 case `eval_group.json` (5 single + 5 multi, ≥ 1 case route tới tool mới)
- Chạy `--suite group` và `--suite extension`, phân tích case fail
- Bảng B3; bonus Small Local Model (B7) nếu máy đủ mạnh

### Bằng chứng

- `starter_v0/data/eval_group.json`
- `starter_v0/runs/*_group_*`, `*_extension_*`
- group report B3, B7

## Nguyễn Văn Quốc-2A202603864

### Phần việc phụ trách

- UI + Demo

### Đóng góp cụ thể

- Làm UI Streamlit `app.py`, thêm dependency vào `requirements.txt`
- Mở link Cloudflare Tunnel cho showdown
- Chat live ≥ 3 lượt (thường / thiếu info rồi bổ sung / yêu cầu gửi Telegram), lưu transcript
- Phần A (A1–A3) trước showdown, bảng B4; bonus gửi Telegram thật

### Bằng chứng

- `starter_v0/app.py`
- `starter_v0/requirements.txt`
- `starter_v0/transcripts/*.transcript.json`
- group report Phần A, B4
