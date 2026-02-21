# 🔐 OWASP Top 10 Lab - SQL Injection & XSS

Đây là ứng dụng web giáo dục minh họa có chủ đích các lỗ hổng **SQL Injection** và **Cross-Site Scripting (XSS)**, kèm chế độ an toàn để so sánh cách phòng chống.

## 📋 Mục đích

Dự án giúp sinh viên hiểu rõ hơn về:
- SQLi: bypass login, UNION exfiltration, Blind SQLi (time-based)
- XSS: Stored, Reflected, DOM-based, và encode theo ngữ cảnh
- Theo dõi tấn công qua log bảo mật
- Mô phỏng tác động thực tế (token exfiltration trong lab)
- Cách vá lỗi chuẩn bằng Parameterized Query + Output Encoding
- Cách tự kiểm chứng bằng test tự động

## 🚀 Cách chạy trên máy tính cá nhân

### Yêu cầu
- Python 3.8+
- pip (trình quản lý gói Python)

### Bước 1: Cài đặt thư viện
```bash
pip install -r requirements.txt
```

### Bước 1.1 (khuyến nghị): Cài bộ kiểm thử
```bash
pip install -r requirements-dev.txt
```

### Bước 2: Chạy ứng dụng
```bash
python app.py
```

### Bước 3: Truy cập trên trình duyệt
Mở trình duyệt và truy cập: `http://127.0.0.1:5000`

## 🧪 Nội dung lab mở rộng

- SQLi:
  - Đăng nhập bypass
  - UNION SELECT trích xuất dữ liệu
  - Blind SQLi time-based với `sleep()`
- XSS:
  - Stored XSS
  - Reflected XSS
  - DOM XSS qua hash sink
  - Context encoding demo (HTML body, attribute, JS string, URL)
- CTF mini:
  - Mỗi khai thác thành công nhận 1 flag trong session
- Monitoring:
  - Nhật ký payload nghi vấn theo endpoint
- Bài tập Fix-Me:
  - `exercises/fix_me_sqli.py`
  - `exercises/fix_me_xss.py`

## 🌐 Deploy lên Render (Miễn phí)

### Bước 1: Tạo tài khoản GitHub
1. Truy cập [GitHub.com](https://github.com)
2. Tạo tài khoản mới hoặc đăng nhập

### Bước 2: Tạo Repository mới
1. Nhấp vào dấu `+` ở góc trên phải
2. Chọn "New repository"
3. Đặt tên: `sqli-demo`
4. Chọn "Public"
5. Nhấp "Create repository"

### Bước 3: Đẩy mã nguồn lên GitHub
Mở Terminal/Command Prompt tại thư mục dự án và chạy:

```bash
git init
git add .
git commit -m "Initial commit: SQL Injection Demo"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/sqli-demo.git
git push -u origin main
```

*Thay `YOUR_USERNAME` bằng tên GitHub của bạn*

### Bước 4: Deploy trên Render
1. Truy cập [Render.com](https://render.com)
2. Đăng nhập bằng tài khoản GitHub
3. Nhấp "New +" → "Web Service"
4. Chọn repository `sqli-demo`
5. Đặt tên service: `sqli-demo`
6. Chọn "Free" plan
7. Nhấp "Create Web Service"

Render sẽ tự động deploy ứng dụng của bạn. Sau 2-3 phút, bạn sẽ có một URL công khai như:
```
https://sqli-demo.onrender.com
```

## 📝 Hướng dẫn sử dụng

### Phiên bản LỖI (Có lỗ hổng)
Thử nhập:
- **Username**: `admin' OR '1'='1`
- **Password**: `anything`

Bạn sẽ đăng nhập thành công mà không cần mật khẩu chính xác!

### Phiên bản AN TOÀN (An toàn)
Cùng payload trên sẽ không hoạt động. Hãy thử:
- **Username**: `admin`
- **Password**: `admin123`

## 🔍 Giải thích kỹ thuật

### Lỗ hổng SQL Injection
```python
# ❌ LỖI - Sử dụng f-string
query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
```

Khi nhập `admin' OR '1'='1`, câu lệnh SQL trở thành:
```sql
SELECT * FROM users WHERE username = 'admin' OR '1'='1' AND password = 'anything'
```

Vì `'1'='1'` luôn đúng, điều kiện `OR` sẽ làm cho toàn bộ WHERE clause trả về True.

### Cách phòng chống
```python
# ✅ ĐÚNG - Sử dụng Parameterized Queries
query = "SELECT * FROM users WHERE username = ? AND password = ?"
cursor.execute(query, (username, password))
```

Các tham số được truyền riêng biệt, nên các ký tự đặc biệt được coi là dữ liệu, không phải mã lệnh.

## ✅ Chạy kiểm thử

```bash
python -m pytest -q
```

Kỳ vọng: toàn bộ test pass cho cả kịch bản vulnerable và secure.

## 📎 Tài liệu kiểm chứng & tài liệu nguồn

- Tài liệu kiểm chứng: `docs/verification_report.md`
- Checklist OWASP theo lab: `docs/owasp_checklist.md`
- Tài liệu nguồn tham chiếu: `docs/source_references.md`
- Ví dụ nâng cao DevTools Console: `docs/devtools_console_examples.md`
- Câu hỏi thảo luận theo demo: `docs/discussion_questions.md`
- Lời giải + dẫn chứng thực tế: `docs/discussion_answers.md`

## 📚 Tài liệu tham khảo

- [OWASP SQL Injection](https://owasp.org/www-community/attacks/SQL_Injection)
- [OWASP Cross-Site Scripting (XSS)](https://owasp.org/www-community/attacks/xss/)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [CWE-89: SQL Injection](https://cwe.mitre.org/data/definitions/89.html)
- [CWE-79: Cross-Site Scripting](https://cwe.mitre.org/data/definitions/79.html)
- [SQLite Parameterized Queries](https://www.sqlite.org/appfunc.html)

## ⚠️ Lưu ý quan trọng

**Dự án này chỉ dành cho mục đích giáo dục.** Việc thực hiện tấn công vào các hệ thống mà không có sự cho phép là hành vi vi phạm pháp luật.

## 📄 Giấy phép

MIT License - Tự do sử dụng cho mục đích học tập và nghiên cứu.

---

**Tác giả**: Nguyen Doan Quynh Nhu  
**Ngày tạo**: 2026-02-21  
**Phiên bản**: 1.0.0
# sqli-demo
