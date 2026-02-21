from flask import Flask, render_template, request, jsonify, session
import sqlite3
import os
import time
import re
import json
import uuid
from datetime import datetime
from urllib.parse import quote
import html

app = Flask(__name__)
app.secret_key = 'owasp_lab_secret_key_2026'

SECURITY_EVENTS = []
MAX_SECURITY_EVENTS = 250

SQLI_PATTERN = re.compile(
    r"(--|/\*|\*/|;|'|\"|\bOR\b|\bUNION\b|\bSELECT\b|\bDROP\b|\bSLEEP\s*\()",
    re.IGNORECASE,
)
XSS_PATTERN = re.compile(
    r"(<script|</script>|onerror\s*=|onload\s*=|javascript:|<img|<svg|<iframe)",
    re.IGNORECASE,
)


def _now_iso():
    return datetime.now().isoformat(timespec="seconds")


def _get_client_ip():
    forwarded_for = request.headers.get("X-Forwarded-For", "")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.remote_addr or "unknown"


def _ensure_session_state():
    if "secure_mode" not in session:
        session["secure_mode"] = False
    if "ctf_flags" not in session:
        session["ctf_flags"] = []
    if "lab_token" not in session:
        session["lab_token"] = f"TKN-{uuid.uuid4().hex[:12].upper()}"


def _log_security_event(category, payload, secure_mode, note=""):
    event = {
        "time": _now_iso(),
        "category": category,
        "endpoint": request.path,
        "method": request.method,
        "secure_mode": bool(secure_mode),
        "payload": str(payload)[:220],
        "ip": _get_client_ip(),
        "note": note,
    }
    SECURITY_EVENTS.insert(0, event)
    del SECURITY_EVENTS[MAX_SECURITY_EVENTS:]


def _award_flag(flag_id, summary):
    _ensure_session_state()
    flags = list(session.get("ctf_flags", []))
    existing = {item["id"] for item in flags}
    if flag_id in existing:
        return False
    flags.append({"id": flag_id, "summary": summary, "earned_at": _now_iso()})
    session["ctf_flags"] = flags
    return True


def _is_sqli_payload(value):
    return bool(SQLI_PATTERN.search(value or ""))


def _is_xss_payload(value):
    return bool(XSS_PATTERN.search(value or ""))


def _sqlite_sleep(seconds):
    try:
        delay = float(seconds)
    except (TypeError, ValueError):
        delay = 0.0
    delay = max(0.0, min(delay, 2.0))
    time.sleep(delay)
    return 0

# ============================================================================
# DATABASE INITIALIZATION
# ============================================================================

def get_db_connection():
    """Khởi tạo kết nối cơ sở dữ liệu SQLite"""
    conn = sqlite3.connect(':memory:', check_same_thread=False)
    conn.create_function("sleep", 1, _sqlite_sleep)
    cursor = conn.cursor()
    
    # Tạo bảng users
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE,
            password TEXT,
            email TEXT
        )
    ''')
    
    # Tạo bảng products
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY,
            name TEXT,
            price REAL,
            description TEXT
        )
    ''')
    
    # Tạo bảng comments (cho XSS demo)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY,
            username TEXT,
            content TEXT,
            created_at TEXT
        )
    ''')
    
    # Kiểm tra và thêm dữ liệu mẫu
    cursor.execute('SELECT COUNT(*) FROM users')
    if cursor.fetchone()[0] == 0:
        # Thêm users
        cursor.execute("INSERT INTO users (username, password, email) VALUES ('admin', 'admin123', 'admin@owasp.lab')")
        cursor.execute("INSERT INTO users (username, password, email) VALUES ('user1', 'password1', 'user1@owasp.lab')")
        cursor.execute("INSERT INTO users (username, password, email) VALUES ('nhu', 'nhu2026', 'nhu@owasp.lab')")
        
        # Thêm products
        cursor.execute("INSERT INTO products (name, price, description) VALUES ('Laptop văn phòng', 999.99, 'Laptop hiệu năng ổn định cho công việc')")
        cursor.execute("INSERT INTO products (name, price, description) VALUES ('Chuột không dây', 29.99, 'Chuột kết nối không dây tiện lợi')")
        cursor.execute("INSERT INTO products (name, price, description) VALUES ('Bàn phím cơ', 79.99, 'Bàn phím cơ gõ êm, độ bền cao')")
        
        conn.commit()
    
    return conn

db_conn = get_db_connection()


@app.before_request
def _prepare_session():
    _ensure_session_state()


# ============================================================================
# ROUTES
# ============================================================================

@app.route('/')
def index():
    """Trang chủ"""
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    """Giữ tương thích URL dashboard"""
    return render_template('index.html')

# ============================================================================
# SQL INJECTION ENDPOINTS
# ============================================================================

@app.route('/api/login', methods=['POST'])
def login():
    """
    Endpoint đăng nhập - SQLi Demo
    Chế độ bảo mật được kiểm soát bởi tham số 'secure' trong session
    """
    data = request.get_json(silent=True) or {}
    username = data.get('username', '')
    password = data.get('password', '')
    secure_mode = session.get('secure_mode', False)
    cursor = db_conn.cursor()

    suspicious = _is_sqli_payload(username) or _is_sqli_payload(password)
    if suspicious:
        _log_security_event(
            "SQLi/Login",
            f"username={username} | password={password}",
            secure_mode,
            "Payload nghi vấn tại form đăng nhập.",
        )

    try:
        if secure_mode:
            query = "SELECT * FROM users WHERE username = ? AND password = ?"
            cursor.execute(query, (username, password))
        else:
            query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
            cursor.execute(query)

        user = cursor.fetchone()
        flag_awarded = False
        if not secure_mode and suspicious and user:
            flag_awarded = _award_flag(
                "FLAG-SQLI-LOGIN-001",
                "Khai thác SQL Injection để bypass đăng nhập.",
            )

        response = {
            "status": "success" if user else "fail",
            "message": f"✓ Chào mừng {user[1]}!" if user else "✗ Sai tên đăng nhập hoặc mật khẩu!",
            "secure": bool(secure_mode),
            "flag_awarded": flag_awarded,
        }
        if not secure_mode:
            response["query_executed"] = query
        return jsonify(response)
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"✗ Lỗi SQL: {str(e)}",
            "secure": bool(secure_mode),
        })

@app.route('/api/search_product', methods=['POST'])
def search_product():
    """
    Endpoint tìm kiếm sản phẩm - SQLi Demo
    """
    data = request.get_json(silent=True) or {}
    search_term = data.get('search', '')
    secure_mode = session.get('secure_mode', False)
    cursor = db_conn.cursor()

    suspicious = _is_sqli_payload(search_term)
    if suspicious:
        _log_security_event(
            "SQLi/Search",
            search_term,
            secure_mode,
            "Payload nghi vấn tại tìm kiếm sản phẩm.",
        )

    try:
        if secure_mode:
            query = "SELECT * FROM products WHERE name LIKE ? OR description LIKE ?"
            search_pattern = f"%{search_term}%"
            cursor.execute(query, (search_pattern, search_pattern))
        else:
            query = f"SELECT * FROM products WHERE name LIKE '%{search_term}%' OR description LIKE '%{search_term}%'"
            cursor.execute(query)

        products = cursor.fetchall()
        flag_awarded = False
        if not secure_mode and "union" in search_term.lower():
            flag_awarded = _award_flag(
                "FLAG-SQLI-UNION-002",
                "Khai thác UNION SQLi để trích xuất dữ liệu.",
            )

        response = {
            "status": "success",
            "products": [{"id": p[0], "name": p[1], "price": p[2], "description": p[3]} for p in products],
            "secure": bool(secure_mode),
            "flag_awarded": flag_awarded,
        }
        if not secure_mode:
            response["query_executed"] = query
        return jsonify(response)
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"✗ Lỗi SQL: {str(e)}",
            "secure": bool(secure_mode)
        })


@app.route('/api/blind_check', methods=['POST'])
def blind_check():
    """
    Blind SQLi demo: phản hồi chung, quan sát qua thời gian phản hồi.
    """
    data = request.get_json(silent=True) or {}
    probe = data.get('probe', '')
    secure_mode = session.get('secure_mode', False)
    cursor = db_conn.cursor()

    suspicious = _is_sqli_payload(probe)
    if suspicious:
        _log_security_event(
            "SQLi/Blind",
            probe,
            secure_mode,
            "Payload nghi vấn tại blind SQLi.",
        )

    started = time.perf_counter()
    try:
        if secure_mode:
            query = "SELECT id FROM users WHERE username = ?"
            cursor.execute(query, (probe,))
        else:
            query = f"SELECT id FROM users WHERE username = '{probe}'"
            cursor.execute(query)
        _ = cursor.fetchone()
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"✗ Lỗi SQL: {str(e)}",
            "secure": bool(secure_mode),
        })

    duration_ms = int((time.perf_counter() - started) * 1000)
    flag_awarded = False
    if not secure_mode and suspicious and "sleep" in probe.lower():
        flag_awarded = _award_flag(
            "FLAG-SQLI-BLIND-003",
            "Khai thác blind SQLi dạng time-based.",
        )

    response = {
        "status": "success",
        "message": "Yêu cầu đã được ghi nhận.",
        "duration_ms": duration_ms,
        "secure": bool(secure_mode),
        "flag_awarded": flag_awarded,
    }
    if not secure_mode:
        response["query_executed"] = query
    return jsonify(response)

# ============================================================================
# XSS ENDPOINTS
# ============================================================================

@app.route('/api/get_comments', methods=['GET'])
def get_comments():
    """
    Lấy danh sách bình luận - XSS Demo
    """
    secure_mode = session.get('secure_mode', False)
    cursor = db_conn.cursor()
    cursor.execute("SELECT id, username, content, created_at FROM comments ORDER BY id DESC")
    comments = cursor.fetchall()
    
    result = []
    for comment in comments:
        if secure_mode:
            # ✅ CÁCH AN TOÀN: HTML escape
            content = html.escape(comment[2])
        else:
            # ❌ CÁCH LỖI: Không escape
            content = comment[2]
        
        result.append({
            "id": comment[0],
            "username": html.escape(comment[1]),
            "content": content,
            "created_at": comment[3]
        })
    
    return jsonify({
        "status": "success",
        "comments": result,
        "secure": secure_mode
    })

@app.route('/api/post_comment', methods=['POST'])
def post_comment():
    """
    Đăng bình luận - XSS Demo (Stored XSS)
    """
    data = request.get_json(silent=True) or {}
    username = data.get('username', 'Ẩn danh')
    content = data.get('content', '')
    secure_mode = session.get('secure_mode', False)
    
    if not content.strip():
        return jsonify({"status": "fail", "message": "Bình luận không được để trống!"})

    suspicious = _is_xss_payload(content)
    if suspicious:
        _log_security_event(
            "XSS/Stored",
            content,
            secure_mode,
            "Payload nghi vấn tại bình luận.",
        )

    cursor = db_conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO comments (username, content, created_at) VALUES (?, ?, ?)",
            (username, content, _now_iso())
        )
        db_conn.commit()

        flag_awarded = False
        if not secure_mode and suspicious:
            flag_awarded = _award_flag(
                "FLAG-XSS-STORED-004",
                "Khai thác Stored XSS qua bình luận.",
            )

        return jsonify({
            "status": "success",
            "message": "Bình luận đã được đăng!",
            "secure": bool(secure_mode),
            "flag_awarded": flag_awarded,
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Lỗi: {str(e)}"
        })

@app.route('/api/search_reflect', methods=['POST'])
def search_reflect():
    """
    Tìm kiếm phản ánh - XSS Demo (Reflected XSS)
    """
    data = request.get_json(silent=True) or {}
    search_term = data.get('search', '')
    secure_mode = session.get('secure_mode', False)

    suspicious = _is_xss_payload(search_term)
    if suspicious:
        _log_security_event(
            "XSS/Reflected",
            search_term,
            secure_mode,
            "Payload nghi vấn tại reflected search.",
        )

    search_display = html.escape(search_term) if secure_mode else search_term
    flag_awarded = False
    if not secure_mode and suspicious:
        flag_awarded = _award_flag(
            "FLAG-XSS-REFLECTED-005",
            "Khai thác Reflected XSS qua ô tìm kiếm.",
        )

    return jsonify({
        "status": "success",
        "message": f"Kết quả tìm kiếm cho: {search_display}",
        "search_term": search_display,
        "secure": bool(secure_mode),
        "flag_awarded": flag_awarded,
    })


@app.route('/api/xss_context_demo', methods=['POST'])
def xss_context_demo():
    """
    Minh họa XSS theo ngữ cảnh: HTML body, attribute, JS string, URL query.
    """
    data = request.get_json(silent=True) or {}
    user_input = data.get("value", "")
    secure_mode = session.get("secure_mode", False)

    if _is_xss_payload(user_input):
        _log_security_event(
            "XSS/Context",
            user_input,
            secure_mode,
            "Payload nghi vấn tại context encoding demo.",
        )

    vulnerable = {
        "html_body": f"<div>{user_input}</div>",
        "html_attribute": f"<img src=\"/avatar.png\" alt=\"{user_input}\">",
        "javascript_string": f"<script>const userValue = '{user_input}';</script>",
        "url_query": f"/search?q={user_input}",
    }

    safe_body = html.escape(user_input)
    safe_attr = html.escape(user_input, quote=True)
    safe_js = json.dumps(user_input, ensure_ascii=False)
    safe_url = quote(user_input, safe="")
    secure = {
        "html_body": f"<div>{safe_body}</div>",
        "html_attribute": f"<img src=\"/avatar.png\" alt=\"{safe_attr}\">",
        "javascript_string": f"<script>const userValue = {safe_js};</script>",
        "url_query": f"/search?q={safe_url}",
    }

    return jsonify({
        "status": "success",
        "secure_mode": bool(secure_mode),
        "input": user_input,
        "vulnerable_samples": vulnerable,
        "secure_samples": secure,
        "explain": {
            "html_body": "Escape HTML entities trước khi render vào nội dung thẻ.",
            "html_attribute": "Escape ký tự quote và ký tự đặc biệt trong thuộc tính.",
            "javascript_string": "Dùng JSON encoding cho chuỗi JavaScript.",
            "url_query": "URL encode tham số trước khi nối URL.",
        },
    })


@app.route('/api/claim_dom_xss', methods=['POST'])
def claim_dom_xss():
    """
    Ghi nhận khai thác DOM XSS từ phía client.
    """
    data = request.get_json(silent=True) or {}
    payload = data.get("payload", "")
    secure_mode = session.get("secure_mode", False)

    suspicious = _is_xss_payload(payload)
    if suspicious:
        _log_security_event(
            "XSS/DOM",
            payload,
            secure_mode,
            "Payload nghi vấn tại DOM sink (hash).",
        )

    flag_awarded = False
    if not secure_mode and suspicious:
        flag_awarded = _award_flag(
            "FLAG-XSS-DOM-006",
            "Khai thác DOM XSS qua URL hash + innerHTML.",
        )

    return jsonify({
        "status": "success",
        "secure": bool(secure_mode),
        "flag_awarded": flag_awarded,
    })

# ============================================================================
# IMPACT SIMULATION + CTF + MONITORING
# ============================================================================

@app.route('/api/lab_token', methods=['GET'])
def lab_token():
    """Trả về token giả lập để minh họa tác động XSS."""
    return jsonify({
        "status": "success",
        "token": session.get("lab_token"),
        "note": "Token này chỉ dùng trong môi trường lab.",
    })


@app.route('/api/capture_token', methods=['POST'])
def capture_token():
    """Endpoint giả lập attacker nhận token."""
    data = request.get_json(silent=True) or {}
    token = data.get("token", "")
    source = data.get("source", "unknown")
    secure_mode = session.get("secure_mode", False)

    if token:
        _log_security_event(
            "XSS/Impact",
            token,
            secure_mode,
            f"Token bị gửi tới endpoint capture từ nguồn: {source}",
        )

    flag_awarded = False
    if not secure_mode and token and token == session.get("lab_token"):
        flag_awarded = _award_flag(
            "FLAG-XSS-IMPACT-007",
            "Mô phỏng đánh cắp token thành công.",
        )

    return jsonify({
        "status": "success",
        "message": "Đã ghi nhận token tại endpoint giả lập attacker.",
        "secure": bool(secure_mode),
        "flag_awarded": flag_awarded,
    })


@app.route('/api/ctf_flags', methods=['GET'])
def ctf_flags():
    """Danh sách cờ CTF đã đạt trong session hiện tại."""
    flags = session.get("ctf_flags", [])
    return jsonify({"status": "success", "flags": flags, "total": len(flags)})


@app.route('/api/security_events', methods=['GET'])
def security_events():
    """Danh sách sự kiện bảo mật gần nhất."""
    return jsonify({"status": "success", "events": SECURITY_EVENTS[:80], "total": len(SECURITY_EVENTS)})


@app.route('/api/clear_security_events', methods=['POST'])
def clear_security_events():
    """Xóa log sự kiện bảo mật (cho mục đích demo)."""
    SECURITY_EVENTS.clear()
    return jsonify({"status": "success", "message": "Đã xóa log sự kiện bảo mật."})


@app.route('/api/reset_lab_state', methods=['POST'])
def reset_lab_state():
    """Reset bình luận + cờ CTF + token lab."""
    cursor = db_conn.cursor()
    cursor.execute("DELETE FROM comments")
    db_conn.commit()
    session["ctf_flags"] = []
    session["lab_token"] = f"TKN-{uuid.uuid4().hex[:12].upper()}"
    SECURITY_EVENTS.clear()
    return jsonify({"status": "success", "message": "Đã reset trạng thái lab."})

# ============================================================================
# SECURITY CONTROL ENDPOINTS
# ============================================================================

@app.route('/api/set_security_mode', methods=['POST'])
def set_security_mode():
    """
    Bật/tắt chế độ bảo mật
    """
    data = request.get_json(silent=True) or {}
    secure = bool(data.get('secure', False))
    session['secure_mode'] = secure
    
    return jsonify({
        "status": "success",
        "message": f"Chế độ bảo mật: {'BẬT ✓' if secure else 'TẮT ✗'}",
        "secure_mode": secure
    })

@app.route('/api/get_security_mode', methods=['GET'])
def get_security_mode():
    """
    Lấy trạng thái chế độ bảo mật hiện tại
    """
    secure_mode = session.get('secure_mode', False)
    return jsonify({
        "secure_mode": secure_mode,
        "status": "BẬT ✓" if secure_mode else "TẮT ✗"
    })

@app.route('/api/clear_comments', methods=['POST'])
def clear_comments():
    """
    Xóa tất cả bình luận (cho demo)
    """
    cursor = db_conn.cursor()
    cursor.execute("DELETE FROM comments")
    db_conn.commit()
    
    return jsonify({
        "status": "success",
        "message": "Tất cả bình luận đã được xóa!"
    })

@app.route('/api/test_accounts', methods=['GET'])
def test_accounts():
    """
    Trả về danh sách tài khoản test
    """
    return jsonify({
        "accounts": [
            {"username": "admin", "password": "admin123"},
            {"username": "user1", "password": "password1"},
            {"username": "nhu", "password": "nhu2026"}
        ]
    })

@app.route('/api/source_code', methods=['GET'])
def source_code():
    """
    Trả về mã nguồn của các hàm lỗi để phân tích
    """
    return jsonify({
        "vulnerable_login": """
# ❌ CÁCH LỖI - SQL Injection
query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
cursor.execute(query)
        """,
        "secure_login": """
# ✅ CÁCH AN TOÀN - Parameterized Queries
query = "SELECT * FROM users WHERE username = ? AND password = ?"
cursor.execute(query, (username, password))
        """,
        "blind_sqli_time_based": """
# ❌ CÁCH LỖI - Blind SQLi (time-based)
query = f"SELECT id FROM users WHERE username = '{probe}'"
cursor.execute(query)  # payload có thể gọi sleep(1)
        """,
        "vulnerable_xss": """
# ❌ CÁCH LỖI - Không escape HTML
content = comment_content  # Trực tiếp hiển thị
        """,
        "secure_xss": """
# ✅ CÁCH AN TOÀN - Escape theo ngữ cảnh
html_body = html.escape(input_value)
js_string = json.dumps(input_value)
url_value = quote(input_value, safe="")
        """
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
