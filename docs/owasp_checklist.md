# OWASP Checklist Theo Từng Lab

## A. SQL Injection

- OWASP: Injection
- CWE: CWE-89
- Endpoint demo lỗi:
  - `/api/login`
  - `/api/search_product`
  - `/api/blind_check`
- Dấu hiệu code lỗi:
  - Nối chuỗi trực tiếp vào SQL query
- Cách vá:
  - Parameterized query (`?` placeholders)
- Cách xác nhận:
  - Payload SQLi không còn bypass/exfiltrate/delay bất thường khi bật secure mode

## B. Stored XSS

- OWASP: Cross-Site Scripting
- CWE: CWE-79
- Endpoint demo lỗi:
  - `/api/post_comment` + `/api/get_comments`
- Dấu hiệu code lỗi:
  - Render dữ liệu user nhập mà không escape
- Cách vá:
  - Escape output cho HTML body
- Cách xác nhận:
  - Payload script hiển thị dạng text, không thực thi trong secure mode

## C. Reflected XSS

- OWASP: Cross-Site Scripting
- CWE: CWE-79
- Endpoint demo lỗi:
  - `/api/search_reflect`
- Dấu hiệu code lỗi:
  - Trả tham số input thẳng về giao diện
- Cách vá:
  - Escape output trước khi render
- Cách xác nhận:
  - Chuỗi `<script>` bị encode thành `&lt;script&gt;` trong secure mode

## D. DOM XSS

- OWASP: XSS (client-side)
- CWE: CWE-79
- Điểm sink demo:
  - `templates/index.html` (hash -> render)
  - `/api/claim_dom_xss` (đánh dấu khai thác)
- Dấu hiệu code lỗi:
  - Gán payload vào `innerHTML`
- Cách vá:
  - Dùng `textContent` hoặc sanitizer phù hợp
- Cách xác nhận:
  - Khi secure mode bật, payload hash chỉ hiển thị text

## E. Context Encoding

- Mục tiêu:
  - Không dùng 1 hàm escape cho mọi ngữ cảnh
- Endpoint:
  - `/api/xss_context_demo`
- Ngữ cảnh:
  - HTML body
  - HTML attribute
  - JavaScript string
  - URL query
- Cách vá:
  - HTML: `html.escape`
  - JS string: `json.dumps`
  - URL: `urllib.parse.quote`

## F. Monitoring & Verification

- Log sự kiện:
  - `/api/security_events`
  - `/api/clear_security_events`
- CTF kiểm chứng khai thác:
  - `/api/ctf_flags`
- Test tự động:
  - `tests/test_security_lab.py`
