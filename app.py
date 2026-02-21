from flask import Flask, render_template, request, jsonify
import sqlite3
import os

app = Flask(__name__)

# Khởi tạo cơ sở dữ liệu SQLite
def get_db_connection():
    conn = sqlite3.connect(':memory:', check_same_thread=False)
    cursor = conn.cursor()
    
    # Tạo bảng nếu chưa tồn tại
    cursor.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password TEXT)')
    
    # Kiểm tra xem đã có dữ liệu chưa
    cursor.execute('SELECT COUNT(*) FROM users')
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO users (username, password) VALUES ('admin', 'p@ssw0rd123')")
        cursor.execute("INSERT INTO users (username, password) VALUES ('manus', 'ai_assistant_2026')")
        cursor.execute("INSERT INTO users (username, password) VALUES ('demo', 'demo123')")
        conn.commit()
    
    return conn

# Khởi tạo database toàn cục
db_conn = get_db_connection()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/login_vulnerable', methods=['POST'])
def login_vulnerable():
    """
    Endpoint có lỗ hổng SQL Injection
    Để demo tấn công, hãy thử nhập:
    Username: admin' OR '1'='1
    Password: anything
    """
    data = request.json
    username = data.get('username', '')
    password = data.get('password', '')
    
    # LỖI: Sử dụng f-string để xây dựng câu truy vấn SQL
    query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
    
    cursor = db_conn.cursor()
    try:
        cursor.execute(query)
        user = cursor.fetchone()
        
        if user:
            return jsonify({
                "status": "success",
                "message": f"✓ Chào mừng {user[1]}! (Bạn đã đăng nhập thành công)",
                "query_executed": query,
                "user_id": user[0],
                "username": user[1]
            })
        else:
            return jsonify({
                "status": "fail",
                "message": "✗ Sai tên đăng nhập hoặc mật khẩu!",
                "query_executed": query
            })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"✗ Lỗi SQL: {str(e)}",
            "query_executed": query
        })

@app.route('/api/login_secure', methods=['POST'])
def login_secure():
    """
    Endpoint an toàn - sử dụng Parameterized Queries
    Thử tấn công với cùng payload sẽ không thành công
    """
    data = request.json
    username = data.get('username', '')
    password = data.get('password', '')
    
    # CÁCH SỬA: Sử dụng Parameterized Queries (dấu hỏi chấm)
    query = "SELECT * FROM users WHERE username = ? AND password = ?"
    
    cursor = db_conn.cursor()
    try:
        cursor.execute(query, (username, password))
        user = cursor.fetchone()
        
        if user:
            return jsonify({
                "status": "success",
                "message": f"✓ Chào mừng {user[1]}! (Bạn đã đăng nhập thành công)",
                "user_id": user[0],
                "username": user[1]
            })
        else:
            return jsonify({
                "status": "fail",
                "message": "✗ Sai tên đăng nhập hoặc mật khẩu!"
            })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"✗ Lỗi: {str(e)}"
        })

@app.route('/api/test_accounts', methods=['GET'])
def test_accounts():
    """Trả về danh sách tài khoản test"""
    return jsonify({
        "accounts": [
            {"username": "admin", "password": "p@ssw0rd123"},
            {"username": "manus", "password": "ai_assistant_2026"},
            {"username": "demo", "password": "demo123"}
        ]
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
