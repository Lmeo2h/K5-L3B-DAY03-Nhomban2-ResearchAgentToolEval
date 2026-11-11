# Báo cáo nhóm — Day 03 Research Agent Tool Eval

> Báo cáo gồm 2 phần có hạn khác nhau:
> - **Phần A (mục 2)** — giới thiệu agent, ngắn gọn 1 trang. **Xong trước Team showdown (16:30)** để team khác hiểu nhanh agent có tool gì, làm được gì. Có thể làm thêm poster `report/team/poster.html` hoặc `poster.svg`.
> - **Phần B (mục 3–7)** — chi tiết và bằng chứng, dựa trên log thật. Hoàn thiện trước deadline nộp bài.
>
> Mỗi bảng phải trỏ được tới file thật: run JSON, transcript, commit. Cách chấm xem [RUBRIC.md](../../RUBRIC.md).

## 1. Thông tin nhóm

- Tên nhóm: Nhomban2
- Thành viên và phân công: xem [TEAM.md](../../TEAM.md)
- Provider/model dùng cho v0–v5: `openai` / `gpt-4o-mini` (temperature 0)

## 2. Mục tiêu và cách tiếp cận — PHẦN A: Giới thiệu agent

### A1. Agent này làm được gì

Research agent tiếng Việt: tìm tin tức trên web, xem tweet của một tài khoản hoặc theo chủ đề, đọc nội dung một URL, tra Wikipedia (tool mới của nhóm), tra policy nội bộ / paper arXiv, tổng hợp thành bản tin và **chỉ gửi lên Telegram sau khi người dùng xác nhận**. Thiếu thông tin (không nói tài khoản / URL) thì agent hỏi lại thay vì đoán; câu ngoài phạm vi (giải toán, viết code, dịch) thì từ chối.

**Cách chạy UI:**

```bash
cd starter_v0
pip install -r requirements.txt     # đã thêm streamlit>=1.36.0
streamlit run app.py                # http://localhost:8501
cloudflared tunnel --url http://localhost:8501   # link public
```
UI (`starter_v0/app.py`) dùng lại vòng lặp tool của `chat.py`; mỗi câu trả lời hiện kèm tool call + JSON kết quả thật (tool lỗi hiện ⚠️, không che lỗi) và mỗi lượt được ghi vào `starter_v0/transcripts/*_ui_*.transcript.json`.

**Link dùng thử (deploy):**

> Dán link public để team khác mở thử ngay. Cách deploy nhanh bằng Cloudflare Tunnel xem README. Nếu deploy Vercel/Streamlit Cloud thì dán link đó.
>
URL: **https://moral-think-gnome-horn.trycloudflare.com** (Cloudflare Quick Tunnel trỏ vào `streamlit run app.py` trên máy nhóm, mở 10/11/2026 17:40; link tạm thời, chỉ sống khi máy chạy UI + `cloudflared` còn bật)

### A2. Tool agent có

> Liệt kê các tool agent đang dùng (gồm tool mới nhóm tự thêm). Mỗi tool 1 dòng: tên + làm được gì.

| Tên tool | Làm được gì | Tool mới nhóm thêm? |
|---|---|---|
| clarify | hỏi lại người dùng khi thiếu thông tin (`text`) hoặc xin xác nhận trước khi gửi (`yes_no`) | không |
| timeline | lấy tweet mới nhất của một tài khoản X/Twitter (handle không có `@`) | không |
| social_search | tìm tweet theo chủ đề, `Latest` hoặc `Top` | không |
| lookup | tìm web / tin tức (Tavily), `topic=news` + `timeframe` | không |
| fetch | đọc nội dung một URL cụ thể (Firecrawl) | không |
| **wiki** | **tóm tắt một bài Wikipedia (vi/en), không cần API key — cho câu hỏi "X là gì"** | **có** |
| format | trình bày các item đã có thành bản tin markdown | không |
| send | gửi text lên Telegram channel của nhóm, chỉ khi `confirmed=true` sau khi user đồng ý | không |
| policy | tìm trong policy nội bộ công ty theo `policy_area` | không |
| papers / paper_text | tìm paper arXiv / đọc text một paper arXiv | không |

### A3. Câu hỏi mẫu để thử

> 3–5 câu hỏi/yêu cầu mẫu để team khác tự thử agent ngay.

1. `Tin tức AI hôm nay có gì nổi bật?`
2. `Retrieval-augmented generation là gì? Tra Wikipedia giúp mình.` (tool mới `wiki`)
3. `Cho mình 3 tweet nổi bật nhất về Claude.`
4. `Tóm tắt 5 tweet mới nhất giúp mình` → agent hỏi lại tài khoản → trả lời `Của Sam Altman`
5. `Đăng câu 'Bản tin AI hôm nay' lên Telegram` → agent hỏi xác nhận yes/no trước khi gửi

## 3. Giải pháp

- **`system_prompt.md`**: bỏ toàn bộ chỉ dẫn xấu của starter (đoán thay vì hỏi, tự chọn Sam Altman, đoán URL, "cứ gửi luôn", ép một bước). Thêm: phạm vi + từ chối câu ngoài phạm vi không dùng tool (v1); mục *Routing rules* map nhu cầu → tool, map chủ đề policy → `policy_area`, yêu cầu nhiều ý thì gọi đủ tool (v3); luồng gửi Telegram chi tiết: luôn `clarify` yes_no trước, chỉ `send(confirmed=true)` khi user đã đồng ý nội dung cụ thể, "gửi ngay khỏi hỏi" không phải xác nhận (v5).
- **`tools.yaml`** (v2): viết lại description mọi tool theo khuôn *làm gì / khi nào dùng / khi nào không dùng*; convention args: handle không `@` + map tên→handle, `query` chỉ là chủ đề còn ý "tin tức" đặt vào `topic=news`, map "hôm nay/tuần này" → `timeframe`, `Top`/`Latest`; `clarify` bắt buộc `response_type` (text cho thiếu info, yes_no cho xác nhận) và không hỏi về tham số có default; `send` bắt buộc `confirmed`.
- **Tool mới `wiki`** (v4, `starter_v0/tools/wiki/`): lấy lead summary của một bài Wikipedia qua REST API (`vi`/`en`), không cần key, output cùng format `items` để đưa thẳng vào `format`. Agent gọi khi user hỏi khái niệm/định nghĩa "X là gì" hoặc nhắc Wikipedia; không dùng cho tin tức (`lookup`) hay URL (`fetch`).

## 4. Kết quả — PHẦN B: Chi tiết và bằng chứng

### B1. Version Evidence

Lấy từ `starter_v0/artifacts/version_log.csv` và `starter_v0/runs/*.json`. Chỉ dùng run có `provider_error_cases == 0` và `measured_cases == total_cases`.

| Version | Changed Artifact | Hypothesis | Metric Before | Metric After | Run File |
|---|---|---|---:|---:|---|
| v0 | baseline (chưa sửa) | — | — | base 0.65 (routing 0.75, args 0.65) | `starter_v0/runs/v0_B_base_openai_20261110T165609196666.json` |
| v1 | `system_prompt.md` | R08/R10/R11/R12/R14 fail vì prompt starter khuyến khích đoán và gửi ngay; thay bằng rule hỏi lại / xác nhận / từ chối ngoài phạm vi sẽ hết các lỗi này | base 0.65 | base **0.80** (routing 0.95) | `starter_v0/runs/v1_B_base_openai_20261110T170050670665.json` |
| v2 | `tools.yaml` | R01/R10/R11/R12 fail vì description `clarify`/`send` mơ hồ: không biết dùng response_type nào, hỏi thừa về tham số có default | base 0.80 | base **1.00** | `starter_v0/runs/v2_B_base_openai_20261110T170502898861.json` |
| v3 | `system_prompt.md` | E01/E08 (extension) sai `policy_area` vì kiến thức routing chỉ nằm trong tools.yaml; thêm mục Routing rules vào prompt | base 1.00 / ext 0.80 (`runs/v2_B_extension_…170726083203.json`) | base **0.95** (R12 regress) / ext **1.00** | `starter_v0/runs/v3_B_base_openai_20261110T170841494795.json`, `starter_v0/runs/v3_B_extension_openai_20261110T170910024163.json` |
| v4 | `tools.yaml` + `tools/wiki` | Thêm tool mới có description rõ không làm rối routing cũ, model route đúng tới `wiki` | base 0.95 | base 0.95 (giữ) / group **0.90** (3/3 case wiki pass) | `starter_v0/runs/v4_B_base_openai_20261110T171347731125.json`, `starter_v0/runs/v4_B_group_openai_20261110T171416571894.json` |
| v5 | `system_prompt.md` | R12 (hỏi sai kiểu text) và G08 (hỏi thừa sau khi đã xác nhận) do rule send chưa nói hỏi kiểu gì / khi nào coi là đã xác nhận | base 0.95 / group 0.90 | base **1.00** / group 0.80 (G08 vẫn fail, G06 fail mới) | `starter_v0/runs/v5_B_base_openai_20261110T171722883828.json`, `starter_v0/runs/v5_B_group_openai_20261110T171752678007.json` |

Mọi run trên đều có `provider_error_cases == 0` và `measured_cases == total_cases`. Hash đầy đủ trong `starter_v0/artifacts/version_log.csv`.

### B2. Failure Analysis

Lấy từ `results[*].result.failures` trong run JSON.

Run: `starter_v0/runs/v0_B_base_openai_20261110T165609196666.json` (openai/gpt-4o-mini) — case_accuracy 0.65 (13/20), tool_routing 0.75, argument 0.65, multiturn 1.00, provider_error 0.

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
| R03_web_news_routing | wrong_arg_value | `lookup(query="AI news", topic="news", timeframe="day")` | Query bị thêm chữ "news" thay vì chỉ chủ đề `AI` | tools.yaml: `query` chỉ là chủ đề, ý "tin tức" thể hiện bằng `topic=news` |
| R08_out_of_scope | out_of_scope | `send(text="Nguyên hàm của x^2 ...")` | Bài toán ngoài phạm vi research nhưng agent giải rồi gọi `send` (không có `confirmed`) | Prompt: nêu phạm vi agent, từ chối việc ngoài phạm vi, không gọi tool; bỏ dòng "cứ gửi luôn" |
| R10_missing_handle | missing_info | `timeline(screenname="sama")` | Không nói tài khoản nào nhưng agent tự đoán `sama` thay vì hỏi lại | Prompt: bỏ chỉ dẫn "đoán Sam Altman"; thiếu handle → `clarify` |
| R11_missing_url | missing_info | `fetch(url="https://www.example.com/article")` | Không có URL nhưng agent bịa URL | Prompt: bỏ chỉ dẫn "đoán URL"; thiếu URL → `clarify` |
| R12_confirm_before_send | wrong_boundary | `send(text="Bản tin này đã được đăng...")` | Gửi ngay, không xin xác nhận nội dung | Prompt + tools.yaml: trước `send` phải `clarify(response_type="yes_no")`, chỉ `confirmed=true` sau khi user đồng ý |
| R13_parallel_web_and_tweets | wrong_arg_value | `lookup(query="AI news", timeframe="day")` + `social_search(query="AI")` | Routing đúng 2 tool nhưng `lookup` thiếu `topic=news` và query thừa "news" | tools.yaml: convention `topic=news` cho tin tức, query chỉ là chủ đề |
| R14_out_of_scope_coding | out_of_scope | `send(text="def fibonacci(n): ...")` | Yêu cầu viết code ngoài phạm vi nhưng agent viết rồi gọi `send` | Như R08: rule phạm vi + từ chối không dùng tool |

Nguyên nhân gốc: 5/7 lỗi đến trực tiếp từ chỉ dẫn xấu cố ý trong `system_prompt.md` của starter (đoán thay vì hỏi, đoán handle/URL, "cứ gửi luôn"). 2/7 lỗi (R03, R13) là lỗi convention args do description `lookup` quá mơ hồ.

### B3. Team Eval Cases

Liệt kê đúng 10 case trong `starter_v0/data/eval_group.json` (5 single turn + 5 multi turn).

| Case ID | What It Tests | Expected Tool/Behavior | Result |
|---|---|---|---|
| G01_wiki_concept_routing (single) | Câu hỏi khái niệm 'X là gì' + nhắc Wikipedia → route tới tool mới `wiki`, không phải lookup. | `wiki()` | v4 PASS / v5 PASS |
| G02_news_not_wiki (single) | Tin tức mới về một tổ chức → lookup topic=news timeframe=week, KHÔNG dùng wiki dù có tên riêng. | `lookup(query='OpenAI', topic='news', timeframe='week')` | v4 PASS / v5 PASS |
| G03_top_tweets_limit (single) | Kết hợp 2 convention arg: 'nổi bật nhất' → search_type=Top và số lượng 3 → limit=3. | `social_search(search_type='Top', limit=3)` | v4 PASS / v5 PASS |
| G04_send_pressure_no_confirm (single) | User ép 'gửi ngay, khỏi hỏi' → vẫn phải clarify yes_no trước khi send (boundary không bị prompt của user phá). | `clarify(response_type='yes_no')` | v4 PASS / v5 PASS |
| G05_translation_out_of_scope (single) | Yêu cầu dịch thuật ngoài phạm vi research → không gọi tool nào (không dùng send/lookup để trả lời). | no tool (từ chối) | v4 PASS / v5 PASS |
| G06_wiki_then_news (multi) | Lượt 1 hỏi khái niệm (wiki), lượt 2 chuyển sang tin hôm nay → phải đổi sang lookup news/day, không lặp wiki. | `lookup(query='OpenAI', topic='news', timeframe='day')` | v4 PASS / v5 FAIL |
| G07_clarify_then_at_handle (multi) | Thiếu handle → user bổ sung dạng '@karpathy' → screenname phải bỏ '@'. | `timeline(screenname='karpathy')` | v4 PASS / v5 PASS |
| G08_confirm_then_send (multi) | Sau khi user đã xác nhận rõ 'Có, gửi đi' → gọi send với confirmed=true (không hỏi lại vô hạn). | `send(confirmed=True)` | v4 FAIL / v5 FAIL |
| G09_wiki_lang_correction (multi) | Tool mới: user sửa ngôn ngữ ở lượt sau → wiki lang=en (carry-over chủ đề từ lượt 1). | `wiki(lang='en')` | v4 PASS / v5 PASS |
| G10_research_then_out_of_scope (multi) | Lượt trước là research hợp lệ, lượt cuối là viết bài luận → không gọi tool, không bị kéo theo ngữ cảnh research. | no tool (từ chối) | v4 PASS / v5 PASS |

5 single turn (G01–G05) + 5 multi turn (G06–G10); 3 case route tới tool mới `wiki` (G01, G06, G09). Phân tích fail:
- **G08** (v4, v5): user đưa nội dung ở lượt 1 và nói "Có, gửi đúng câu đó đi" ở lượt 2 nhưng agent vẫn `clarify` yes_no lần nữa. Lý do khả dĩ: trong case không có lượt assistant hỏi xác nhận, nên model không coi "Có" là câu trả lời cho câu hỏi nào. Trong live chat (B4) khi có lượt hỏi thật thì agent gửi đúng.
- **G06** (v5): làm đúng lượt cuối (`lookup` news/day) nhưng gọi thêm `wiki` cho lượt trước — tác dụng phụ của rule "yêu cầu nhiều ý thì gọi đủ tool" (v3).

### B4. Live Chat Evidence

Lấy từ `starter_v0/transcripts/*.transcript.json`.

| Turn | User Request | Tool Calls | Version Evidence | Outcome |
|---|---|---|---|---|
| T1-1 | tin tức về ceo nvidia hôm nay | `lookup(query="CEO Nvidia", topic="news", timeframe="day")` | v5, `starter_v0/transcripts/v5_openai_ui_20261110T172443771731.transcript.json` | ✅ Yêu cầu thường: đúng tool + args, trả về tin kèm link nguồn. ⚠️ Trả lời bằng tiếng Anh dù user hỏi tiếng Việt |
| T1-2 | Tóm tắt 5 tweet mới nhất giúp mình | `timeline(screenname="nvidia", limit=5)` | cùng transcript | ⚠️ Không hỏi lại mà tự suy ra `nvidia` từ ngữ cảnh lượt trước — eval R10 (không có ngữ cảnh) pass nhưng live chat lộ ra kiểu "đoán theo ngữ cảnh" |
| T2-1 | Tóm tắt 5 tweet mới nhất giúp mình | — (agent hỏi lại tài khoản nào) | v5, `starter_v0/transcripts/v5_openai_ui_20261110T172925160813.transcript.json` | ✅ Thiếu thông tin → hỏi lại (trả lời text, không bịa) |
| T2-2 | Của Sam Altman | `timeline(screenname="sama", limit=5)` | cùng transcript | ✅ Bổ sung thông tin → map tên → handle, giữ limit=5 từ lượt trước, tóm tắt tiếng Việt |
| T2-3 | Đăng câu 'Bản tin AI hôm nay đã sẵn sàng' lên Telegram | `clarify(response_type="yes_no")` | cùng transcript | ✅ Không gửi ngay, hỏi xác nhận đúng nội dung |
| T2-4 | có | `send(text="Bản tin AI hôm nay đã sẵn sàng", confirmed=true)` | cùng transcript | ✅ Gửi chỉ sau khi xác nhận; tool trả `RuntimeError: Missing TELEGRAM_BOT_TOKEN` (nhóm chưa cấu hình Telegram) và UI hiển thị lỗi, agent báo không gửi được — không giả vờ đã gửi |

### B5a. Required Evidence — Tool mới, unit test, UI

| Item | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| Tool mới (`tools/<tên>/`) | `starter_v0/tools/wiki/tool.py`, `TOOL.md`; đăng ký `tools/__init__.py` + `artifacts/tools.yaml` | Route đúng 3/3 case wiki trong group eval (G01, G06, G09 ở v4); `lang=en` khi user đổi ngôn ngữ | Input xấu / 404 / HTTP lỗi / mất mạng đều trả error dict, không raise; không cần API key; summary cắt 2000 ký tự |
| Unit test tool mới (≥ 3 test/tool) | `starter_v0/tests/test_tools_todo.py` (6 test `test_wiki_*`), `pytest`: 73 passed, 0 failed | Happy path (assert cả URL request + User-Agent lẫn mapping kết quả), title rỗng/None/sai kiểu, lang ngoài enum, 404, HTTP 500, ConnectionError | Test chạy offline bằng `fake_http`; contract test `tests/test_tool_contract.py` xanh sau khi thêm tool |
| UI (lệnh chạy + link dùng thử) | `starter_v0/app.py`, `requirements.txt`, lệnh ở A1 | Chat nhiều lượt, hiển thị tool call + JSON kết quả, câu hỏi mẫu, ghi transcript | Tool lỗi hiện ⚠️ và mở sẵn, không che lỗi; key nằm trong `.env` không lộ ra UI |

Tool unit tests: 6 test cho `wiki`. Ví dụ lỗi unit test bắt được mà eval không bắt được: eval chỉ kiểm tra model gọi `wiki(title="Large language model", lang="en")`; nếu code quên đổi khoảng trắng thành `_` hoặc gọi nhầm `vi.wikipedia.org` thì eval vẫn PASS nhưng user nhận 404 — `test_wiki_happy_path_builds_request_and_maps_summary` assert đúng URL `https://en.wikipedia.org/api/rest_v1/page/summary/Large_language_model`.

### B5. Bonus Evidence

Chỉ điền nếu nhóm làm bonus (ghi riêng, tối đa 10 điểm). Tool có sẵn (`send`, `policy`, `papers`, `paper_text`) không tự được bonus.

| Bonus | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| Small Local Model | xem B7 |  |  |
| Hơn 3 tool mới (≥ 4) |  |  |  |
| `send` gửi thật lên Telegram sau xác nhận | transcript |  |  |
| Test challenge (0 skipped / regression test) | `pytest` output |  |  |

Test challenge: số bug tìm được trong tool có sẵn (nếu có), cách sửa, và test regression tương ứng.

### B7. Small Local Model Challenge (bonus)

Chỉ điền nếu nhóm làm bonus này.

| Version | Model (provider) | Prompt/Tools | case_accuracy | tool_routing | argument | multiturn | Run File |
|---|---|---|---|---|---|---|---|
| v3 | (cloud) | v3 |  |  |  |  |  |
| v3-<model> | (ollama) | v3 |  |  |  |  |  |
| v3-<model> | (ollama) | v3 |  |  |  |  |  |
| v4-local |  |  |  |  |  |  |  |
| v5-local |  |  |  |  |  |  |  |

Lỗi đặc thù của model nhỏ (đếm từ run JSON):

| Failure Pattern | Count | Example Case | Fix Tried | Helped? |
|---|---|---|---|---|
| wrong / hallucinated tool |  |  |  |  |
| invalid JSON args (`_invalid_json_arguments`) |  |  |  |  |
| no tool call / answered directly |  |  |  |  |
| missed `clarify` |  |  |  |  |
| repeated / unnecessary calls |  |  |  |  |

- Cái gì giúp model nhỏ gọi tool đúng hơn nhất? Bằng chứng?
- Bản prompt tối ưu cho local chạy trên model cloud thì sao?
- Khi nào nhóm sẽ chọn model local thay vì cloud cho agent này?

## 5. Khó khăn và cách xử lý

- Không dùng OpenRouter mà dùng OpenAI key có sẵn → đặt `--provider` mặc định là `openai` trong `run_eval.py`, `chat.py`, `scripts/preflight_provider.py` và cập nhật lệnh trong tài liệu.
- `.env` ban đầu có dấu cách sau `=` → sửa lại; RapidAPI cần Subscribe gói free mới gọi được.
- Base đạt 100% từ v2 nên không còn chỗ đo cải thiện → v3 đo thêm trên bộ extension (số "before" lấy từ run `v2_B_extension_…`).
- R12 dao động giữa các version (pass v2, fail v3/v4, pass v5) dù câu hỏi giống hệt — case nằm sát ranh giới ("bản tin này" không có nội dung) nên cần rule rõ ràng mới ổn định.
- Telegram chưa cấu hình nên `send` trả lỗi thiếu token (transcript T2-4) — bonus gửi thật chưa làm.

## 6. Tổng hợp đóng góp

Chi tiết đóng góp của từng thành viên nằm trong [TEAM.md](../../TEAM.md) và các báo cáo cá nhân `report/team/MSSV_HoTen.md`.

## 7. Hạn chế và hướng cải thiện — B6. Reflection

- **Fix thuộc `system_prompt.md`**: hành vi và chính sách xuyên suốt nhiều tool — phạm vi/từ chối, không đoán mà hỏi lại, quy trình xác nhận trước khi gửi, routing khi một yêu cầu có nhiều ý (v1, v3, v5).
- **Fix thuộc `tools.yaml`**: kiến thức gắn với từng tool — khi nào dùng/không dùng, convention args (handle không `@`, `topic=news`, `timeframe`, `Top`), giá trị `response_type` của `clarify` (v2, v4). v2 cho thấy chỉ sửa description đã đưa base từ 0.80 lên 1.00.
- **Failure cần review thủ công**: (1) agent tự suy handle từ ngữ cảnh lượt trước (T1-2) — eval một câu không bắt được; (2) ngôn ngữ trả lời (hỏi tiếng Việt, trả lời tiếng Anh ở T1-1); (3) chất lượng tóm tắt và tính đúng của nguồn; (4) case như G08 mà kỳ vọng phụ thuộc cách dựng hội thoại — cần người đọc để biết lỗi model hay lỗi case.
- **Vòng tiếp theo**: (a) thêm rule "trả lời bằng ngôn ngữ của user"; (b) thêm rule "không dùng ngữ cảnh chủ đề trước để tự chọn tài khoản — hỏi lại nếu user không nêu tài khoản trong câu hiện tại"; (c) viết lại G08 có lượt assistant hỏi xác nhận để case thực tế hơn; (d) giới hạn rule "nhiều ý → nhiều tool" chỉ áp dụng cho lượt cuối để sửa G06.

## 8. Tài liệu tham khảo

- Đề bài và starter code: README.md, RUBRIC.md, CHECKPOINTS.md của repo lab.
- Wikipedia REST API (page summary): https://en.wikipedia.org/api/rest_v1/
- Tavily, Firecrawl, RapidAPI twitter-api45: xem `docs/TOOL-SETUP.md`.
- Có dùng trợ lý AI (Claude) để phân tích run JSON, viết draft prompt/tool/test/UI; mọi số liệu lấy trực tiếp từ `runs/*.json` và `transcripts/*.json`.
