# 🔐 SQL Injection Demo - Học về Bảo Mật Web

Đây là một ứng dụng web giáo dục minh họa lỗ hổng **SQL Injection** và cách phòng chống.

## 📋 Mục đích

Dự án này giúp lập trình viên và học viên hiểu rõ hơn về:
- Cách lỗ hổng SQL Injection xảy ra
- Tại sao nó nguy hiểm
- Cách phòng chống bằng **Parameterized Queries**

## 🚀 Cách chạy trên máy tính cá nhân

### Yêu cầu
- Python 3.8+
- pip (trình quản lý gói Python)

### Bước 1: Cài đặt thư viện
```bash
pip install -r requirements.txt
```

### Bước 2: Chạy ứng dụng
```bash
python app.py
```

### Bước 3: Truy cập trên trình duyệt
Mở trình duyệt và truy cập: `http://127.0.0.1:5000`

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

## 📚 Tài liệu tham khảo

- [OWASP SQL Injection](https://owasp.org/www-community/attacks/SQL_Injection)
- [CWE-89: SQL Injection](https://cwe.mitre.org/data/definitions/89.html)
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
