"""
Bài tập Fix-Me: SQL Injection

Mục tiêu:
- Sửa endpoint đăng nhập đang dễ bị SQL Injection.
- Viết lại truy vấn theo Parameterized Query.
- Không đổi contract JSON đầu ra.
"""

import sqlite3


def login_vulnerable(conn: sqlite3.Connection, username: str, password: str):
    """
    TODO cho sinh viên:
    1) Đổi truy vấn này sang dạng parameterized query.
    2) Không dùng f-string hoặc nối chuỗi trực tiếp.
    """
    cursor = conn.cursor()
    query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
    cursor.execute(query)
    return cursor.fetchone()


def login_secure_example(conn: sqlite3.Connection, username: str, password: str):
    """
    Mẫu đáp án tham khảo.
    """
    cursor = conn.cursor()
    query = "SELECT * FROM users WHERE username = ? AND password = ?"
    cursor.execute(query, (username, password))
    return cursor.fetchone()
