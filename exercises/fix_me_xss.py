"""
Bài tập Fix-Me: XSS

Mục tiêu:
- Sửa hàm render để không còn thực thi script người dùng nhập.
- Escape đúng ngữ cảnh khi đưa dữ liệu vào HTML body và JS string.
"""

import html
import json


def render_comment_vulnerable(username: str, comment: str) -> str:
    """
    TODO cho sinh viên:
    1) Không render trực tiếp dữ liệu người dùng vào HTML.
    2) Dùng escape phù hợp để chặn Stored/Reflected XSS.
    """
    return f"<div><strong>{username}</strong>: {comment}</div>"


def render_comment_secure_example(username: str, comment: str) -> str:
    safe_user = html.escape(username)
    safe_comment = html.escape(comment)
    return f"<div><strong>{safe_user}</strong>: {safe_comment}</div>"


def build_js_snippet_vulnerable(user_input: str) -> str:
    """
    TODO cho sinh viên:
    1) Tránh tự nối chuỗi JavaScript bằng dấu nháy đơn.
    """
    return f"<script>const value = '{user_input}';</script>"


def build_js_snippet_secure_example(user_input: str) -> str:
    encoded = json.dumps(user_input, ensure_ascii=False)
    return f"<script>const value = {encoded};</script>"
