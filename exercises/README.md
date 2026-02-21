# Bài Tập Bắt Buộc (Fix-Me)

## Mục tiêu
- Sinh viên không chỉ khai thác, mà phải tự vá lỗi.
- Giữ nguyên hành vi nghiệp vụ, chỉ thay đổi cách xử lý bảo mật.

## Danh sách bài tập
1. `fix_me_sqli.py`
- Sửa `login_vulnerable()` để chống SQL Injection bằng parameterized query.

2. `fix_me_xss.py`
- Sửa `render_comment_vulnerable()` để chống Stored/Reflected XSS.
- Sửa `build_js_snippet_vulnerable()` để encode an toàn cho JS string.

## Tiêu chí đạt
- Payload SQLi không còn bypass đăng nhập.
- Payload XSS hiển thị dạng text, không thực thi script.
- Không dùng blacklist regex thay thế encode/query binding.
