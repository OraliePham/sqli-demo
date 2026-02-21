# Lời Giải Câu Hỏi Thảo Luận OWASP Lab

Tài liệu này là phần đáp án gợi ý cho `docs/discussion_questions.md`.
Mục tiêu là giúp giảng viên dẫn dắt thảo luận theo hướng "hiểu bản chất, không học vẹt payload".

## 1) SQL Injection - Login Bypass

1. Payload `admin' OR '1'='1` thành công vì ứng dụng nối chuỗi SQL trực tiếp, làm dữ liệu đầu vào trở thành một phần của mệnh đề điều kiện.
2. Đổi vị trí dấu nháy có thể gây lỗi cú pháp hoặc thay đổi logic `WHERE`, cho thấy SQLi phụ thuộc ngữ cảnh câu query gốc.
3. `query_executed` làm lộ cấu trúc DB/query cho attacker, giúp họ tối ưu payload nhanh hơn.
4. Chặn regex `"OR"` không bền vững vì attacker có nhiều biến thể payload khác (`oR`, comment, unicode, toán tử khác).
5. SQLi vẫn có thể thất bại nếu payload không khớp ngữ cảnh cú pháp, quyền DB bị hạn chế, hoặc query đã được parameterized.

## 2) SQL Injection - UNION Exfiltration

1. `UNION SELECT` yêu cầu cùng số cột và kiểu dữ liệu tương thích với query gốc.
2. Attacker thường dò bằng `ORDER BY n`, hoặc thử dần `UNION SELECT NULL, ...` để suy luận số cột.
3. `--` dùng để comment phần query còn lại, tránh lỗi do đuôi câu truy vấn gốc.
4. Stack trace giúp attacker biết tên bảng/cột, loại DB, vị trí lỗi, từ đó tăng tốc khai thác.
5. SQLi đọc dữ liệu (exfiltration) và SQLi sửa/xóa dữ liệu (tampering/destructive) có mức độ rủi ro và dấu hiệu vận hành khác nhau.

## 3) Blind SQLi - Time-based

1. Dù response text giống nhau, attacker vẫn suy luận bằng kênh phụ như độ trễ thời gian hoặc đúng/sai logic.
2. Time-based chậm nhưng đủ để trích xuất dữ liệu nhạy cảm theo từng bit/ký tự.
3. Để giảm nhiễu mạng, cần lặp nhiều lần, lấy median/average, và so sánh với baseline.
4. Ngưỡng hợp lý thường là chênh lệch rõ rệt so với baseline (ví dụ >700-1000ms trong lab này).
5. Parameterized query tách code và data nên payload không còn được thực thi như mã SQL.

## 4) Stored XSS

1. Stored XSS nguy hiểm hơn reflected vì payload được lưu lại và tác động nhiều nạn nhân theo thời gian.
2. Escape chỉ ở frontend là chưa đủ, vì dữ liệu có thể đi qua API khác hoặc kênh render khác.
3. Whitelist thẻ HTML tự viết tay dễ sai ngữ cảnh, nên dùng cơ chế encode/sanitizer đã được kiểm chứng.
4. Tác động thật gồm chiếm phiên, gửi hành động thay người dùng, đánh cắp dữ liệu, cài mã theo dõi.
5. Bật secure mode có thể chặn thực thi dữ liệu cũ nếu render layer hiện tại luôn escape trước khi hiển thị.

## 5) Reflected XSS

1. Reflected XSS không lưu payload ở server; payload chỉ sống trong request/response hiện tại.
2. Nó thường cần “mồi” vì nạn nhân phải truy cập URL/input chứa payload.
3. Escape một phần là không đủ vì mỗi ngữ cảnh cần quy tắc encode riêng.
4. Payload thành công ở HTML body có thể thất bại ở JS string vì parser và ký tự thoát khác nhau.
5. Trong thực tế, reflected XSS thường đi cùng phishing/social engineering để tăng tỷ lệ nạn nhân mở link.

## 6) DOM XSS

1. DOM XSS có thể phát sinh hoàn toàn ở client-side, backend an toàn vẫn chưa đủ.
2. `innerHTML` parse HTML và có thể kích hoạt script handler; `textContent` chỉ hiển thị text.
3. `location.hash` do người dùng/URL kiểm soát nên luôn là input không tin cậy.
4. Không có một hàm escape duy nhất cho mọi sink; phải encode theo đúng ngữ cảnh.
5. Debug nên bám luồng source -> transform -> sink, xác định chính xác nơi dữ liệu đi vào DOM nguy hiểm.

## 7) Context Encoding

1. `html.escape()` phù hợp HTML text node, nhưng JS string cần JSON encoding để tránh break quote/script context.
2. URL query phải URL-encode (`quote`) để giữ đúng semantics URI.
3. Encode sai ngữ cảnh có thể tạo cảm giác “đã bảo vệ” nhưng thực tế vẫn bypass được.
4. Quy trình tốt: validate business rule ở backend, encode tại thời điểm render theo sink cụ thể.
5. Nên chuẩn hóa bằng utility chung/code review checklist để tránh mỗi dev tự xử lý khác nhau.

## 8) CTF Flags Và Security Logging

1. Log payload nghi vấn giúp blue team nhận mẫu tấn công, thời điểm, endpoint bị nhắm.
2. Log nên có endpoint, loại sự kiện, timestamp, mức độ; tránh log dữ liệu bí mật thô.
3. Chống log flooding bằng rate limit, cắt độ dài payload, sampling, và cơ chế lưu trữ xoay vòng.
4. CTF flag đo tiến độ học viên tốt nếu map rõ theo kỹ năng (SQLi, XSS, blind, impact, monitoring).
5. Viết test giúp biến tri thức thành “hàng rào chống tái phát” trong CI/CD, không chỉ vá một lần.

## 9) Tình Huống “Nếu... Thì...”

1. Dùng ORM vẫn có thể dính SQLi nếu có raw query, string formatting, hoặc unsafe interpolation.
2. Frontend sanitize không thay thế backend validation/encoding vì attacker có thể gọi API trực tiếp.
3. CSP mạnh giảm đáng kể XSS nhưng không loại bỏ hoàn toàn khi policy cấu hình sai hoặc có bypass.
4. Một endpoint yếu có thể mở đường lateral movement sang dữ liệu/tài khoản toàn hệ thống.
5. Học payload không học ngữ cảnh dẫn đến “thuộc câu thần chú” nhưng không biết phòng thủ đúng.

## 10) Câu Hỏi Tổng Kết Cuối Buổi

1. Ưu tiên sửa lỗi dựa trên tác động kinh doanh + khả năng khai thác + phạm vi ảnh hưởng.
2. Reviewer cần soi anti-pattern: raw SQL, `innerHTML`, thiếu encode theo sink, thiếu test regression.
3. Pipeline tối thiểu gồm unit test security, API regression test, SAST/DAST cơ bản, và checklist PR.
4. Bài học cốt lõi: mọi input đều không tin cậy; phải tách data/code và encode theo ngữ cảnh.
5. Lập luận thuyết phục team: chi phí phòng ngừa sớm luôn thấp hơn chi phí sự cố + mất uy tín.

## 11) Dẫn Chứng Thực Tế (5 Ví Dụ)

1. TalkTalk (2015) - SQL Injection gây lộ dữ liệu khách hàng  
Ý nghĩa học tập: chỉ một điểm nhập liệu yếu có thể kéo theo sự cố dữ liệu diện rộng.

2. Heartland Payment Systems (2008) - SQL Injection mở đường vào hệ thống xử lý thanh toán  
Ý nghĩa học tập: SQLi không chỉ là lỗi “ứng dụng web nhỏ”, mà có thể ảnh hưởng chuỗi thanh toán lớn.

3. MySpace Samy Worm (2005) - Stored XSS tự lan truyền qua hồ sơ người dùng  
Ý nghĩa học tập: Stored XSS có thể tự nhân rộng như worm, không dừng ở một nạn nhân.

4. Twitter OnMouseOver Worm (2010) - XSS khiến tài khoản tự động đăng/repost ngoài ý muốn  
Ý nghĩa học tập: XSS có thể chuyển thành hành vi giả mạo người dùng ở quy mô lớn.

5. Tình huống bug bounty điển hình (anonymized) - Blind SQLi + DOM XSS chain  
Ý nghĩa học tập: trong thực tế, attacker thường chain nhiều lỗ hổng nhỏ để đạt tác động lớn.

## 12) 5 Mini-Case Cho Thảo Luận Trên Lớp

1. Case thương mại điện tử: ô tìm kiếm sản phẩm bị UNION SQLi, lộ bảng users.
2. Case cổng nội bộ: bình luận ticket bị Stored XSS, đánh cắp token phiên hỗ trợ.
3. Case landing page marketing: tham số `q` phản chiếu thẳng ra HTML gây Reflected XSS.
4. Case dashboard SPA: `location.hash` gán vào `innerHTML`, phát sinh DOM XSS dù backend sạch.
5. Case vận hành SOC: log quá nhiều payload rác, đội giám sát không phát hiện tín hiệu thật.

Mỗi case nên yêu cầu sinh viên trả lời:
1. Điểm source/sink ở đâu?
2. Tác động kinh doanh là gì?
3. Cách vá tối thiểu và cách vá bền vững khác nhau ra sao?
4. Cần thêm test nào để không tái phát?
