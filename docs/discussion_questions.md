# Câu Hỏi Thảo Luận Cho Các Demo OWASP Lab

Tài liệu này dùng để dẫn dắt thảo luận trên lớp sau khi sinh viên đã thực hành demo SQLi/XSS trong lab.

## 1) SQL Injection - Login Bypass

1. Vì sao payload `admin' OR '1'='1` có thể đăng nhập được khi hệ thống ở chế độ có lỗ hổng?
2. Nếu đổi vị trí dấu nháy đơn trong payload, điều gì sẽ xảy ra với câu SQL thực thi?
3. Vì sao hiển thị `query_executed` trong môi trường thật lại rất nguy hiểm?
4. Nếu backend chỉ chặn chuỗi `"OR"` bằng regex, cách phòng thủ đó có bền vững không?
5. Có trường hợp nào login bypass thất bại dù backend vẫn nối chuỗi SQL trực tiếp không?

## 2) SQL Injection - UNION Exfiltration

1. Vì sao payload `UNION SELECT` phải có số cột tương thích với query gốc?
2. Làm sao kẻ tấn công “đoán” được số cột khi không thấy mã nguồn?
3. Tại sao comment SQL (`--`) thường xuất hiện ở cuối payload?
4. Nếu DB lỗi và trả stack trace, attacker có lợi gì?
5. Khác biệt giữa “đọc trộm dữ liệu” và “thay đổi dữ liệu” trong SQLi là gì?

## 3) Blind SQLi - Time-based

1. Khi response luôn giống nhau, vì sao attacker vẫn suy luận được dữ liệu?
2. Vì sao time-based SQLi thường chậm nhưng vẫn nguy hiểm?
3. Nếu mạng chập chờn (latency cao), làm sao phân biệt delay do payload hay do mạng?
4. Trong demo, ngưỡng `duration_ms` nào hợp lý để kết luận có lỗ hổng?
5. Vì sao parameterized query chặn được cả blind SQLi?

## 4) Stored XSS

1. Vì sao payload lưu trong DB có thể gây ảnh hưởng cho nhiều người dùng hơn reflected XSS?
2. Nếu escape ở frontend nhưng backend vẫn lưu raw payload, rủi ro còn không?
3. Tại sao không nên tin tưởng “chỉ cho phép một số thẻ HTML an toàn” nếu tự viết tay?
4. XSS có thể gây tác động gì ngoài `alert()`?
5. Nếu comment có chứa mã độc đã lưu từ trước, bật secure mode có xử lý được dữ liệu cũ không?

## 5) Reflected XSS

1. Điểm khác nhau cốt lõi giữa reflected XSS và stored XSS là gì?
2. Vì sao reflected XSS thường cần “mồi” nạn nhân qua URL hoặc input crafted?
3. Nếu chỉ escape một phần (ví dụ chỉ thay `<` và `>`), có đủ an toàn không?
4. Vì sao một payload hoạt động ở ngữ cảnh HTML body nhưng thất bại ở JS string?
5. Trong thực tế, reflected XSS thường kết hợp với social engineering như thế nào?

## 6) DOM XSS

1. Vì sao DOM XSS vẫn xảy ra dù backend đã escape đúng?
2. `innerHTML` và `textContent` khác nhau ra sao về bề mặt tấn công?
3. Nếu dữ liệu đến từ `location.hash`, vì sao vẫn phải coi là untrusted input?
4. Có thể phòng thủ DOM XSS bằng một hàm escape duy nhất cho mọi nơi không?
5. Khi debug DOM XSS, bước kiểm tra “source -> sink” nên thực hiện như thế nào?

## 7) Context Encoding

1. Vì sao `html.escape()` tốt cho HTML body nhưng chưa đủ cho JS string?
2. Vì sao encode cho URL query phải dùng `quote` thay vì escape HTML?
3. Điều gì xảy ra nếu áp dụng sai kiểu encode cho sai ngữ cảnh?
4. Thứ tự “validate -> encode -> render” nên đặt ở lớp nào của hệ thống?
5. Trong team lớn, làm sao tránh việc mỗi dev encode theo một kiểu khác nhau?

## 8) CTF Flags Và Security Logging

1. Vì sao log payload nghi vấn giúp đội phòng thủ học nhanh hơn?
2. Log nên chứa thông tin gì để vừa hữu ích vừa tránh lộ dữ liệu nhạy cảm?
3. Nếu attacker gửi payload lớn liên tục để làm đầy log, hệ thống nên chống thế nào?
4. CTF flag có thể dùng để đo năng lực học viên theo cách nào công bằng?
5. Vì sao “khai thác thành công” chưa đủ, mà còn cần “viết test để ngăn tái phát”?

## 9) Tình Huống “Nếu... Thì...”

1. Nếu ứng dụng đã dùng ORM, SQLi có còn khả năng xảy ra không?
2. Nếu dữ liệu đầu vào đã sanitize ở frontend, backend có thể bỏ kiểm tra không?
3. Nếu bật CSP mạnh, XSS có bị loại bỏ hoàn toàn không?
4. Nếu chỉ một endpoint bị lỗi, toàn hệ thống có thể bị ảnh hưởng thế nào?
5. Nếu sinh viên chỉ học payload mà không hiểu ngữ cảnh, nguy cơ hiểu sai là gì?

## 10) Câu Hỏi Tổng Kết Cuối Buổi

1. Với vai trò developer, bạn ưu tiên sửa lỗi nào trước và vì sao?
2. Với vai trò reviewer, bạn sẽ kiểm tra các anti-pattern nào trong pull request?
3. Với vai trò security engineer, bạn thiết kế pipeline test bảo mật tối thiểu ra sao?
4. Bài học quan trọng nhất rút ra từ demo SQLi/XSS hôm nay là gì?
5. Nếu phải thuyết phục team đầu tư bảo mật sớm, bạn sẽ dùng lập luận nào?
