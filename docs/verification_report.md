# Báo Cáo Kiểm Chứng Triển Khai Lab

**Ngày kiểm chứng**: 21/02/2026  
**Người thực hiện**: Nguyen Doan Quynh Nhu

## 1) Mục tiêu đã triển khai

1. SQLi 3 mức:
- Bypass login: `/api/login`
- UNION exfiltration: `/api/search_product`
- Blind time-based: `/api/blind_check`

2. XSS 4 ngữ cảnh:
- Stored XSS: `/api/post_comment`, `/api/get_comments`
- Reflected XSS: `/api/search_reflect`
- DOM XSS: `/api/claim_dom_xss` + hash sink trên `templates/index.html`
- Context encoding: `/api/xss_context_demo`

3. Chuỗi tác động thực tế:
- Token lab: `/api/lab_token`
- Endpoint giả lập attacker: `/api/capture_token`

4. Bài tập vá lỗi bắt buộc:
- `exercises/fix_me_sqli.py`
- `exercises/fix_me_xss.py`
- `exercises/README.md`

5. Kiểm thử tự động:
- `tests/test_security_lab.py`

6. Logging và giám sát:
- `/api/security_events`
- `/api/clear_security_events`

7. Checklist OWASP:
- `docs/owasp_checklist.md`

8. Mini-CTF:
- `/api/ctf_flags`
- Các cờ sinh tự động khi khai thác thành công trong mode vulnerable.

## 2) Kết quả kiểm thử tự động

Lệnh đã chạy:

```bash
python -m pytest -q
```

Kết quả:

```text
............                                                             [100%]
12 passed in 1.17s
```

## 3) Danh sách test đã bao phủ

- SQLi login bypass (vulnerable/secure)
- SQLi UNION exfiltration (vulnerable/secure)
- Blind SQLi time-based (vulnerable/secure)
- Stored XSS escape trong secure mode
- Reflected XSS escape trong secure mode
- DOM XSS claim flag trong vulnerable mode
- Context encoding JS string an toàn
- Token capture impact nhận cờ trong vulnerable mode
- Security events có ghi nhận payload nghi vấn

## 4) Lưu ý kiểm chứng

- Kết quả `duration_ms` của Blind SQLi có thể dao động nhỏ theo máy chạy, nhưng test đang kiểm ngưỡng an toàn.
- Cờ CTF lưu theo session người dùng, reset bằng `/api/reset_lab_state`.
