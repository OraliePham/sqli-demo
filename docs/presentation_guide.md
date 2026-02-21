# Hướng Dẫn Thuyết Trình & Thực Hành: OWASP Top 10 - SQL Injection & XSS

**Tác giả**: Nguyen Doan Quynh Nhu  
**Ngày tạo**: 21/02/2026

## 1. Giới Thiệu

Bài thuyết trình này tập trung vào hai trong số các lỗ hổng bảo mật ứng dụng web phổ biến và nguy hiểm nhất theo danh sách **OWASP Top 10**: **SQL Injection (SQLi)** và **Cross-Site Scripting (XSS)**. Chúng ta sẽ khám phá cách các lỗ hổng này hoạt động, cách khai thác chúng trên một môi trường Lab thực tế, và quan trọng nhất là các biện pháp phòng chống hiệu quả.

### 1.1. OWASP Top 10 là gì?

OWASP (Open Web Application Security Project) là một tổ chức phi lợi nhuận hoạt động để cải thiện bảo mật phần mềm. OWASP Top 10 là một tài liệu tiêu chuẩn, cung cấp danh sách 10 rủi ro bảo mật quan trọng nhất đối với các ứng dụng web, giúp các nhà phát triển và chuyên gia bảo mật ưu tiên các nỗ lực phòng thủ [1].

### 1.2. SQL Injection (SQLi)

SQL Injection là một kỹ thuật tấn công cho phép kẻ tấn công chèn các câu lệnh SQL độc hại vào các trường nhập liệu của ứng dụng. Nếu ứng dụng không xử lý đúng cách dữ liệu đầu vào, các câu lệnh này có thể được thực thi bởi cơ sở dữ liệu, dẫn đến việc truy cập, sửa đổi hoặc xóa dữ liệu trái phép [2].

### 1.3. Cross-Site Scripting (XSS)

Cross-Site Scripting là một lỗ hổng bảo mật web cho phép kẻ tấn công chèn các mã script (thường là JavaScript) độc hại vào các trang web hợp pháp. Khi người dùng truy cập trang web bị nhiễm, mã độc sẽ được thực thi trong trình duyệt của họ, cho phép kẻ tấn công đánh cắp thông tin phiên, chuyển hướng người dùng, hoặc thực hiện các hành động khác dưới danh nghĩa người dùng [3].

## 2. Môi Trường Lab Thực Hành

Chúng ta sẽ sử dụng một ứng dụng web Flask đơn giản được thiết kế để minh họa các lỗ hổng SQLi và XSS. Ứng dụng này có một tính năng đặc biệt là **Công tắc Bảo mật** (Security Toggle), cho phép chuyển đổi giữa chế độ "Có lỗ hổng" và "An toàn" để dễ dàng so sánh và demo.

### 2.1. Cấu trúc ứng dụng

Ứng dụng bao gồm các phần chính:

*   **Trang chủ (`/`)**: Giao diện chính để tương tác với các bài Lab.
*   **API Đăng nhập (`/api/login`)**: Minh họa SQL Injection qua chức năng đăng nhập.
*   **API Tìm kiếm Sản phẩm (`/api/search_product`)**: Minh họa SQL Injection qua chức năng tìm kiếm.
*   **API Bình luận (`/api/post_comment`, `/api/get_comments`)**: Minh họa XSS lưu trữ (Stored XSS).
*   **API Tìm kiếm Phản ánh (`/api/search_reflect`)**: Minh họa XSS phản chiếu (Reflected XSS).
*   **API Điều khiển Bảo mật (`/api/set_security_mode`, `/api/get_security_mode`)**: Điều khiển chế độ bảo mật của Lab.

### 2.2. Cách khởi chạy Lab

Để chạy ứng dụng Lab trên máy tính cá nhân, bạn cần cài đặt Python 3.8+ và `pip`.

1.  **Cài đặt thư viện**: Mở terminal/command prompt, điều hướng đến thư mục dự án và chạy:
    ```bash
    pip install -r requirements.txt
    ```
2.  **Khởi chạy ứng dụng**: Chạy lệnh sau:
    ```bash
    python app.py
    ```
3.  **Truy cập Lab**: Mở trình duyệt và truy cập `http://127.0.0.1:5000`.

## 3. Khai Thác SQL Injection (SQLi)

### 3.1. Kịch bản 1: Đăng nhập bỏ qua xác thực (Authentication Bypass)

**Mục tiêu**: Đăng nhập vào tài khoản `admin` mà không cần biết mật khẩu.

**Quy trình khai thác (PoC)**:

1.  **Đảm bảo chế độ LỖI**: Trên giao diện Lab, đảm bảo "Chế độ Bảo mật" đang ở trạng thái **TẮT ✗ (Có lỗ hổng)**.
2.  **Truy cập form Đăng Nhập**: Trong phần "SQL Injection", tìm mục "1️⃣ Đăng Nhập".
3.  **Nhập payload**: 
    *   **Tên đăng nhập**: `admin' OR '1'='1`
    *   **Mật khẩu**: `anything` (hoặc bất kỳ chuỗi nào)
4.  **Nhấn "Đăng Nhập"**: Quan sát kết quả. Bạn sẽ thấy thông báo "✓ Chào mừng admin!" và câu lệnh SQL được thực thi.

**Giải thích**: Khi chế độ bảo mật TẮT, ứng dụng xây dựng câu truy vấn SQL bằng cách nối chuỗi trực tiếp. Payload `admin' OR '1'='1` sẽ biến câu truy vấn gốc thành:

```sql
SELECT * FROM users WHERE username = 'admin' OR '1'='1' AND password = 'anything'
```

Vì `'1'='1'` luôn đúng, điều kiện `OR` sẽ làm cho toàn bộ mệnh đề `WHERE` trở thành `TRUE`, cho phép đăng nhập thành công vào tài khoản `admin`.

### 3.2. Kịch bản 2: Trích xuất dữ liệu (Data Exfiltration) qua tìm kiếm sản phẩm

**Mục tiêu**: Lấy thông tin `username`, `password`, `email` từ bảng `users` thông qua chức năng tìm kiếm sản phẩm.

**Quy trình khai thác (PoC)**:

1.  **Đảm bảo chế độ LỖI**: "Chế độ Bảo mật" đang ở trạng thái **TẮT ✗ (Có lỗ hổng)**.
2.  **Truy cập form Tìm kiếm Sản phẩm**: Trong phần "SQL Injection", tìm mục "2️⃣ Tìm Kiếm Sản Phẩm".
3.  **Nhập payload**: 
    *   **Tìm kiếm**: `%' UNION SELECT 1, username, password, email FROM users --`
4.  **Nhấn "Tìm Kiếm"**: Quan sát kết quả. Bạn sẽ thấy danh sách các sản phẩm, nhưng kèm theo đó là thông tin `username` và `password` của người dùng từ bảng `users`.

**Giải thích**: Payload này sử dụng toán tử `UNION` để kết hợp kết quả của hai câu truy vấn. Câu truy vấn gốc tìm kiếm sản phẩm, và câu truy vấn thứ hai (được chèn vào) sẽ chọn `username`, `password` từ bảng `users`. Dấu `--` ở cuối dùng để comment phần còn lại của câu truy vấn gốc, tránh lỗi cú pháp.

## 4. Khai Thác Cross-Site Scripting (XSS)

### 4.1. Kịch bản 1: XSS lưu trữ (Stored XSS) qua chức năng bình luận

**Mục tiêu**: Chèn mã JavaScript độc hại vào một bình luận, và mã này sẽ được thực thi mỗi khi người khác xem bình luận đó.

**Quy trình khai thác (PoC)**:

1.  **Đảm bảo chế độ LỖI**: Trên giao diện Lab, đảm bảo "Chế độ Bảo mật" đang ở trạng thái **TẮT ✗ (Có lỗ hổng)**.
2.  **Truy cập form Bình luận**: Trong phần "Cross-Site Scripting", tìm mục "1️⃣ XSS Lưu Trữ (Stored XSS) - Bình Luận".
3.  **Nhập payload**: 
    *   **Tên người dùng**: `Hacker`
    *   **Bình luận**: `<script>alert('XSS Lưu Trữ bởi Hacker!');</script>`
4.  **Nhấn "Đăng Bình Luận"**: Bình luận sẽ xuất hiện trong danh sách. Ngay lập tức, một hộp thoại `alert` sẽ bật lên với thông báo "XSS Lưu Trữ bởi Hacker!". Điều này chứng tỏ mã JavaScript đã được thực thi.

**Giải thích**: Khi chế độ bảo mật TẮT, ứng dụng không thực hiện mã hóa (escaping) HTML cho nội dung bình luận trước khi lưu vào cơ sở dữ liệu và hiển thị ra trình duyệt. Do đó, trình duyệt sẽ hiểu `<script>alert('XSS Lưu Trữ bởi Hacker!');</script>` là một đoạn mã JavaScript hợp lệ và thực thi nó.

### 4.2. Kịch bản 2: XSS phản chiếu (Reflected XSS) qua chức năng tìm kiếm

**Mục tiêu**: Chèn mã JavaScript độc hại vào tham số tìm kiếm, và mã này sẽ được phản ánh và thực thi ngay lập tức trên trang kết quả.

**Quy trình khai thác (PoC)**:

1.  **Đảm bảo chế độ LỖI**: "Chế độ Bảo mật" đang ở trạng thái **TẮT ✗ (Có lỗ hổng)**.
2.  **Truy cập form Tìm kiếm Phản ánh**: Trong phần "Cross-Site Scripting", tìm mục "2️⃣ XSS Phản Chiếu (Reflected XSS) - Tìm Kiếm".
3.  **Nhập payload**: 
    *   **Tìm kiếm**: `<script>alert('XSS Phản Chiếu!');</script>`
4.  **Nhấn "Tìm Kiếm"**: Ngay lập tức, một hộp thoại `alert` sẽ bật lên với thông báo "XSS Phản Chiếu!".

**Giải thích**: Tương tự như XSS lưu trữ, khi chế độ bảo mật TẮT, ứng dụng không mã hóa tham số tìm kiếm trước khi hiển thị nó trở lại trên trang. Mã JavaScript được chèn vào sẽ được trình duyệt thực thi ngay lập tức.

## 5. Phòng Chống Lỗ Hổng

### 5.1. Phòng chống SQL Injection

Biện pháp hiệu quả nhất để phòng chống SQL Injection là sử dụng **Parameterized Queries** (còn gọi là Prepared Statements). Thay vì nối chuỗi trực tiếp, các tham số sẽ được truyền riêng biệt vào câu truy vấn SQL. Cơ sở dữ liệu sẽ phân biệt rõ ràng giữa mã lệnh SQL và dữ liệu đầu vào, đảm bảo rằng dữ liệu không bao giờ bị hiểu nhầm là mã lệnh.

**Ví dụ mã nguồn an toàn (từ `app.py`):**

```python
# ✅ CÁCH AN TOÀN - Parameterized Queries
query = "SELECT * FROM users WHERE username = ? AND password = ?"
cursor.execute(query, (username, password))
```

Khi "Chế độ Bảo mật" được BẬT, bạn có thể thử lại các payload tấn công SQLi. Bạn sẽ thấy chúng không còn hoạt động, vì `admin' OR '1'='1` sẽ được coi là một chuỗi ký tự username thông thường, không phải là một phần của câu lệnh SQL.

### 5.2. Phòng chống Cross-Site Scripting (XSS)

Biện pháp chính để phòng chống XSS là **Output Encoding/Escaping** (Mã hóa/Thoát đầu ra). Điều này có nghĩa là mọi dữ liệu do người dùng nhập vào phải được mã hóa phù hợp với ngữ cảnh hiển thị (ví dụ: HTML, JavaScript, URL) trước khi được hiển thị trên trang web. Hàm `html.escape()` trong Python là một ví dụ điển hình.

**Ví dụ mã nguồn an toàn (từ `app.py`):**

```python
# ✅ CÁCH AN TOÀN - HTML escape
content = html.escape(comment[2]) # Mã hóa nội dung bình luận trước khi hiển thị
```

Khi "Chế độ Bảo mật" được BẬT, bạn có thể thử lại các payload tấn công XSS. Bạn sẽ thấy mã JavaScript không còn được thực thi mà thay vào đó, nó sẽ được hiển thị dưới dạng văn bản thuần túy (ví dụ: `<script>alert('XSS Lưu Trữ bởi Hacker!');</script>` sẽ hiển thị nguyên văn trên trang).

## 6. Kết Luận & Khuyến Nghị

SQL Injection và XSS là những lỗ hổng nghiêm trọng có thể gây ra thiệt hại lớn cho ứng dụng và người dùng. Việc hiểu rõ cơ chế hoạt động của chúng và áp dụng các biện pháp phòng chống phù hợp là vô cùng quan trọng. Luôn nhớ:

*   **Không bao giờ tin tưởng dữ liệu đầu vào của người dùng.** Luôn kiểm tra, xác thực và mã hóa dữ liệu.
*   **Sử dụng Parameterized Queries** cho tất cả các tương tác với cơ sở dữ liệu.
*   **Mã hóa đầu ra (Output Encoding)** cho tất cả dữ liệu do người dùng tạo ra trước khi hiển thị trên trang web.
*   **Cập nhật kiến thức bảo mật thường xuyên** và tham khảo các tài liệu như OWASP Top 10.

## 7. Mở Rộng Lab Đào Sâu

Phiên bản hiện tại đã được mở rộng thêm các hạng mục để sinh viên học sâu hơn:

1. **Blind SQLi (time-based)**:
   - Endpoint: `/api/blind_check`
   - Có thể thử payload chứa `sleep(1)` để quan sát độ trễ trong chế độ có lỗ hổng.

2. **DOM XSS + Context Encoding**:
   - DOM XSS qua hash sink trong frontend.
   - Endpoint context demo: `/api/xss_context_demo` cho 4 ngữ cảnh (HTML body, attribute, JS string, URL).

3. **Mô phỏng tác động thực tế của XSS**:
   - Token lab: `/api/lab_token`
   - Endpoint giả lập attacker: `/api/capture_token`

4. **Mini-CTF và giám sát**:
   - Cờ CTF theo session: `/api/ctf_flags`
   - Log sự kiện nghi vấn: `/api/security_events`

5. **Bài tập vá lỗi bắt buộc (Fix-Me)**:
   - `exercises/fix_me_sqli.py`
   - `exercises/fix_me_xss.py`

6. **Kiểm chứng tự động**:
   - `tests/test_security_lab.py`
   - Chạy bằng `python -m pytest -q`

7. **Thực hành nâng cao bằng DevTools Console**:
   - Tài liệu mẫu script JavaScript: `docs/devtools_console_examples.md`
   - Bao gồm: bật/tắt mode, SQLi/Blind SQLi/XSS qua `fetch`, batch payload, đọc cờ CTF và log sự kiện.

8. **Bộ câu hỏi và lời giải thảo luận**:
   - Câu hỏi: `docs/discussion_questions.md`
   - Lời giải + dẫn chứng thực tế: `docs/discussion_answers.md`

## 8. Tài liệu tham khảo

[1] OWASP Foundation. (n.d.). *OWASP Top 10*. Retrieved from [https://owasp.org/www-project-top-ten/](https://owasp.org/www-project-top-ten/)
[2] OWASP Foundation. (n.d.). *SQL Injection*. Retrieved from [https://owasp.org/www-community/attacks/SQL_Injection](https://owasp.org/www-community/attacks/SQL_Injection)
[3] OWASP Foundation. (n.d.). *Cross-Site Scripting (XSS)*. Retrieved from [https://owasp.org/www-community/attacks/xss/](https://owasp.org/www-community/attacks/xss/)
