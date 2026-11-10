---
name: wiki
track: core
kind: live_api
provider: Wikipedia REST API
requires_env: []
inputs: [title, lang]
outputs: [items]
side_effect: false
---
# wiki

Tool mới do nhóm viết. Lấy đoạn tóm tắt (lead summary) của MỘT bài Wikipedia qua
`https://<lang>.wikipedia.org/api/rest_v1/page/summary/<title>`. Không cần API key.

- Khi nào agent nên dùng: user hỏi khái niệm / định nghĩa / thông tin nền ("X là gì", "Wikipedia nói gì về X").
- Không dùng cho tin tức mới (dùng `lookup`) hay bài đăng mạng xã hội.
- Input xấu (`title` rỗng/sai kiểu, `lang` ngoài `vi|en`), HTTP lỗi, hoặc không có bài (404) đều trả error dict, không raise.
- Output `items` cùng format với các tool khác (title, url, source, summary) nên đưa thẳng vào `format` được.
