from flask import Flask, render_template, request, jsonify, session
import sqlite3
import os
from datetime import datetime
import html

app = Flask(__name__)
app.secret_key = 'owasp_lab_secret_key_2026'

# ============================================================================
# DATABASE INITIALIZATION
# ============================================================================

def get_db_connection():
    """Khởi tạo kết nối cơ sở dữ liệu SQLite"""
    conn = sqlite3.connect(':memory:', check_same_thread=False)
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

# ============================================================================
# ROUTES
# ============================================================================

@app.route('/')
def index():
    """Trang chủ"""
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    """Trang dashboard với các bài thực hành"""
    return render_template('dashboard.html')

# ============================================================================
# SQL INJECTION ENDPOINTS
# ============================================================================

@app.route('/api/login', methods=['POST'])
def login():
    """
    Endpoint đăng nhập - SQLi Demo
    Chế độ bảo mật được kiểm soát bởi tham số 'secure' trong session
    """
    data = request.json
    username = data.get('username', '')
    password = data.get('password', '')
    secure_mode = session.get('secure_mode', False)
    
    cursor = db_conn.cursor()
    
    try:
        if secure_mode:
            # ✅ CÁCH AN TOÀN: Parameterized Queries
            query = "SELECT * FROM users WHERE username = ? AND password = ?"
            cursor.execute(query, (username, password))
            user = cursor.fetchone()
            
            return jsonify({
                "status": "success" if user else "fail",
                "message": f"✓ Chào mừng {user[1]}!" if user else "✗ Sai tên đăng nhập hoặc mật khẩu!",
                "secure": True
            })
        else:
            # ❌ CÁCH LỖI: String concatenation
            query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
            cursor.execute(query)
            user = cursor.fetchone()
            
            return jsonify({
                "status": "success" if user else "fail",
                "message": f"✓ Chào mừng {user[1]}!" if user else "✗ Sai tên đăng nhập hoặc mật khẩu!",
                "query_executed": query,
                "secure": False
            })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"✗ Lỗi SQL: {str(e)}",
            "secure": False
        })

@app.route('/api/search_product', methods=['POST'])
def search_product():
    """
    Endpoint tìm kiếm sản phẩm - SQLi Demo
    """
    data = request.json
    search_term = data.get('search', '')
    secure_mode = session.get('secure_mode', False)
    
    cursor = db_conn.cursor()
    
    try:
        if secure_mode:
            # ✅ CÁCH AN TOÀN
            query = "SELECT * FROM products WHERE name LIKE ? OR description LIKE ?"
            search_pattern = f"%{search_term}%"
            cursor.execute(query, (search_pattern, search_pattern))
            products = cursor.fetchall()
            
            return jsonify({
                "status": "success",
                "products": [{"id": p[0], "name": p[1], "price": p[2], "description": p[3]} for p in products],
                "secure": True
            })
        else:
            # ❌ CÁCH LỖI
            query = f"SELECT * FROM products WHERE name LIKE '%{search_term}%' OR description LIKE '%{search_term}%'"
            cursor.execute(query)
            products = cursor.fetchall()
            
            return jsonify({
                "status": "success",
                "products": [{"id": p[0], "name": p[1], "price": p[2], "description": p[3]} for p in products],
                "query_executed": query,
                "secure": False
            })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"✗ Lỗi SQL: {str(e)}",
            "secure": False
        })

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
    data = request.json
    username = data.get('username', 'Ẩn danh')
    content = data.get('content', '')
    secure_mode = session.get('secure_mode', False)
    
    if not content.strip():
        return jsonify({"status": "fail", "message": "Bình luận không được để trống!"})
    
    cursor = db_conn.cursor()
    
    try:
        # Lưu bình luận vào database (không validate/escape ở đây)
        cursor.execute(
            "INSERT INTO comments (username, content, created_at) VALUES (?, ?, ?)",
            (username, content, datetime.now().isoformat())
        )
        db_conn.commit()
        
        return jsonify({
            "status": "success",
            "message": "Bình luận đã được đăng!",
            "secure": secure_mode
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
    data = request.json
    search_term = data.get('search', '')
    secure_mode = session.get('secure_mode', False)
    
    if secure_mode:
        # ✅ CÁCH AN TOÀN: HTML escape
        search_display = html.escape(search_term)
    else:
        # ❌ CÁCH LỖI: Không escape
        search_display = search_term
    
    return jsonify({
        "status": "success",
        "message": f"Kết quả tìm kiếm cho: {search_display}",
        "search_term": search_display,
        "secure": secure_mode
    })

# ============================================================================
# SECURITY CONTROL ENDPOINTS
# ============================================================================

@app.route('/api/set_security_mode', methods=['POST'])
def set_security_mode():
    """
    Bật/tắt chế độ bảo mật
    """
    data = request.json
    secure = data.get('secure', False)
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
        "vulnerable_xss": """
# ❌ CÁCH LỖI - Không escape HTML
content = comment_content  # Trực tiếp hiển thị
        """,
        "secure_xss": """
# ✅ CÁCH AN TOÀN - HTML escape
content = html.escape(comment_content)
        """
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
