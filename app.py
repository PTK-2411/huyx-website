import datetime
import json
import os
import time
import psycopg2
import psycopg2.extras
import hashlib
import random
import requests
import random
from threading import Thread
from flask import Flask, jsonify, render_template, request, url_for, redirect
import jwt

app = Flask(__name__)
SECRET_KEY = "huyx_super_secret_key_123"
DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://neondb_owner:npg_7sFk6Tjergyb@ep-dark-cake-atro3nrq.c-9.us-east-1.aws.neon.tech/neondb?sslmode=require")

# -------------------------------------------------------------------------
# 1. CÁC HÀM TRỢ GIÚP KẾT NỐI VÀ KHỞI TẠO CƠ SỞ DỮ LIỆU SQL
# -------------------------------------------------------------------------
def get_db_connection():
    """Tạo kết nối tới PostgreSQL và cấu hình trả về Dictionary"""
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=psycopg2.extras.RealDictCursor)
    return conn

def init_db():
    """Khởi tạo cấu trúc các bảng SQL nếu chưa tồn tại"""
    conn = get_db_connection()
    cursor = conn.cursor()
    # Tạo bảng quản lý người dùng (users)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            auth_token TEXT DEFAULT '',
            balance INTEGER DEFAULT 0,
            role TEXT DEFAULT 'Member'
        )
    ''')
    
    # Tạo bảng quản lý tiến trình/đơn hàng (tiktok_view)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tiktok_view (
            id SERIAL PRIMARY KEY,
            username TEXT NOT NULL,
            url TEXT NOT NULL,             -- Đường dẫn (Link bài viết)
            type TEXT NOT NULL,            -- Loại dịch vụ (vd: tiktok_view)
            server TEXT NOT NULL,          -- Máy chủ thực hiện (sv1, sv2)
            quantity INTEGER NOT NULL,     -- Số lượng mua
            price INTEGER NOT NULL,        -- SỐ TIỀN CỦA JOB
            note TEXT DEFAULT '',          -- Ghi chú bổ sung
            status TEXT DEFAULT 'pending', -- Trạng thái: pending, processing, completed, error
            priority INTEGER NOT NULL,     -- Độ ưu tiên sắp xếp (1: Cao, 2: Thường)
            created_at DOUBLE PRECISION NOT NULL       -- Mốc thời gian tạo đơn
        )
    ''')
    
    # Tạo bảng quản lý tiến trình/đơn hàng (facebook_share)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS facebook_share (
            id SERIAL PRIMARY KEY,
            username TEXT NOT NULL,
            url TEXT NOT NULL,             -- Đường dẫn (Link bài viết)
            type TEXT NOT NULL,            -- Loại dịch vụ (vd: fb_share)
            server TEXT NOT NULL,          -- Máy chủ thực hiện (sv1, sv2)
            quantity INTEGER NOT NULL,     -- Số lượng mua
            price INTEGER NOT NULL,        -- SỐ TIỀN CỦA JOB
            note TEXT DEFAULT '',          -- Ghi chú bổ sung
            status TEXT DEFAULT 'pending', -- Trạng thái: pending, processing, completed, error
            priority INTEGER NOT NULL,     -- Độ ưu tiên sắp xếp (1: Cao, 2: Thường)
            created_at DOUBLE PRECISION NOT NULL       -- Mốc thời gian tạo đơn
        )
    ''')
    
    # Tạo bảng quản lý key vượt link rút gọn (task_keys)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS task_keys (
            key TEXT PRIMARY KEY,
            username TEXT NOT NULL,
            created_at DOUBLE PRECISION NOT NULL
        )
    ''')
    
    conn.commit()
    conn.close()

# Tự động kích hoạt cấu trúc SQL ngay khi chạy Server
init_db()


# -------------------------------------------------------------------------
# 2. WORKER CHẠY NGẦM - ĐỌC SQL VÀ THỰC HIỆN JOB THEO THỨ TỰ ƯU TIÊN
# -------------------------------------------------------------------------
def background_worker():
    print("[Hệ thống Hàng đợi SQL] Worker xử lý ngầm đã kích hoạt...")
    while True:
        conn = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Tìm đơn hàng đang chờ (pending)
            # Sắp xếp theo: priority tăng dần (1 chạy trước 2), ai tạo trước (created_at) chạy trước
            cursor.execute('''
                SELECT * FROM tiktok_view 
                WHERE status = 'pending' 
                ORDER BY priority ASC, created_at ASC 
                LIMIT 1
            ''')
            job = cursor.fetchone()
                
        except Exception as e:
            print(f"[HỆ THỐNG LỖI WORKER SQL]: {str(e)}")
            time.sleep(2)
        finally:
            if conn:
                conn.close()

# Khởi động luồng chạy ngầm đa nhiệm song song cùng Flask
worker_thread = Thread(target=background_worker, daemon=True)
worker_thread.start()


# -------------------------------------------------------------------------
# 3. ĐỊNH TUYẾN GIAO DIỆN (RENDER TEMPLATE)
# -------------------------------------------------------------------------
@app.route("/")
def index_page(): return render_template("index.html")

@app.route("/dmca-validation.html")
def dmca_validation(): return render_template("dmca-validation.html")

@app.route("/new-index")
def new_index(): return render_template("new_index.html")

@app.route("/login")
def login(): return render_template("login.html")

@app.route("/register")
def register_page(): return render_template("register.html")

@app.route("/profile")
def profile_page(): return render_template("profile.html")

@app.route("/get-key")
def get_key_page():
    key_value = request.args.get("key", "")
    return render_template("get_key.html", key_value=key_value)

@app.route("/kiem-tien/link-rut-gon")
def link_rut_gon():
    key_value = request.args.get("key", "")
    return render_template("link-rut-gon.html", key_value=key_value)

@app.route("/facebook/share")
def facebook_share():
    key_value = request.args.get("key", "")
    return render_template("facebook_share.html", key_value=key_value)

@app.route("/tiktok/view")
def tiktok_view():
    key_value = request.args.get("key", "")
    return render_template("tiktok_view.html", key_value=key_value)

@app.route("/nap-tien")
def nap_tien():
    key_value = request.args.get("key", "")
    return render_template("nap-tien.html", key_value=key_value)

@app.errorhandler(404)
def page_not_found(e):
    return redirect(url_for('index_page'))


# -------------------------------------------------------------------------
# 4. HỆ THỐNG CÁC API XỬ LÝ CHUẨN SQL
# -------------------------------------------------------------------------

# API Đăng nhập
@app.route("/api/login", methods=["POST"])
def login_api():
    try:
        username = request.form.get("username")
        password = request.form.get("password")
        remember = request.form.get("remember") == "true"

        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()

        if user and user["password"] == password:
            duration = datetime.timedelta(days=7) if remember else datetime.timedelta(days=1)
            expiration = datetime.datetime.now(datetime.timezone.utc) + duration

            payload = {"user": username, "exp": expiration}
            token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

            # Đồng bộ token mới vào SQL
            cursor.execute("UPDATE users SET auth_token = %s WHERE username = %s", (token, username))
            conn.commit()
            conn.close()

            return jsonify({"status": "success", "message": "Đăng nhập thành công!", "token": token}), 200

        conn.close()
        return jsonify({"status": "error", "message": "Tài khoản hoặc mật khẩu không chính xác!"}), 401
    except Exception as e:
        return jsonify({"status": "error", "message": f"Lỗi Server Login: {str(e)}"}), 500


# API Đăng ký tài khoản mới
@app.route("/api/register", methods=["POST"])
def register_api():
    try:
        username = request.form.get("username")
        password = request.form.get("password")

        if not username or not password:
            return jsonify({"status": "error", "message": "Vui lòng nhập đủ thông tin đăng ký!"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT username FROM users WHERE username = %s", (username,))
        if cursor.fetchone():
            conn.close()
            return jsonify({"status": "error", "message": "Tài khoản này đã tồn tại!"}), 400

        # Lưu thông tin tài khoản mới
        cursor.execute("INSERT INTO users (username, password, balance, role) VALUES (%s, %s, 0, 'Member')", (username, password))
        conn.commit()
        conn.close()
        
        return jsonify({"status": "success", "message": "Đăng ký thành công! Chào mừng bạn."}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# API Lấy thông tin tài khoản hiện tại
@app.route("/api/me", methods=["POST"])
def me_api():
    try:
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"status": "error", "message": "Không tìm thấy Token phiên làm việc!"}), 401

        token = auth_header.split(" ")[1]
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        username = payload["user"]

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        conn.close()
        
        if user and user["auth_token"] == token:
            return jsonify({
                "status": "success",
                "username": username,
                "coins": user["balance"],
                "role": user["role"]
            }), 200
        else:
            return jsonify({"status": "error", "message": "Mã phiên đăng nhập không hợp lệ"}), 401

    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return jsonify({"status": "error", "message": "Phiên làm việc hết hạn, vui lòng đăng nhập lại!"}), 401
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# API Đổi mật khẩu bảo mật
@app.route("/api/change-password", methods=["POST"])
def change_password_api():
    try:
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"status": "error", "message": "Chưa đăng nhập hệ thống!"}), 401

        token = auth_header.split(" ")[1]
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        username = payload["user"]

        old_password = request.form.get("old_password")
        new_password = request.form.get("new_password")

        if not old_password or not new_password:
            return jsonify({"status": "error", "message": "Vui lòng nhập đầy đủ thông tin!"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()

        if user and user["auth_token"] == token:
            if user["password"] != old_password:
                conn.close()
                return jsonify({"status": "error", "message": "Mật khẩu cũ không chính xác!"}), 400
            
            if old_password == new_password:
                conn.close()
                return jsonify({"status": "error", "message": "Mật khẩu mới trùng mật khẩu cũ!"}), 400

            cursor.execute("UPDATE users SET password = %s WHERE username = %s", (new_password, username))
            conn.commit()
            conn.close()

            return jsonify({"status": "success", "message": "Thay đổi mật khẩu thành công!"}), 200
        else:
            conn.close()
            return jsonify({"status": "error", "message": "Phiên làm việc không tồn tại!"}), 401

    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return jsonify({"status": "error", "message": "Xác thực phiên làm việc thất bại!"}), 401
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# API Lấy danh sách bảng xếp hạng đại gia
@app.route("/api/leaderboard", methods=["GET"])
def get_leaderboard():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT username, balance, role FROM users ORDER BY balance DESC LIMIT 10")
        rows = cursor.fetchall()
        conn.close()

        leaderboard_data = []
        for row in rows:
            leaderboard_data.append({
                "username": row["username"],
                "balance": row["balance"],
                "role": row["role"]
            })

        return jsonify({"status": "success", "data": leaderboard_data}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# -------------------------------------------------------------------------
# 5. API TIẾP NHẬN ĐƠN HÀNG TĂNG VIEW TIKTOK (CÓ KIỂM TRA SỐ DƯ & LƯU PRICE)
# -------------------------------------------------------------------------
@app.route("/api/order/tiktok-view", methods=["POST"])
def create_tiktok_view_order():
    try:
        # Xác thực quyền sở hữu token đăng nhập
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"status": "error", "message": "Vui lòng đăng nhập hệ thống để tiếp tục!"}), 401

        token = auth_header.split(" ")[1]
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        username = payload["user"]

        # Nhận gói tin JSON từ Client gửi lên
        data = request.get_json()
        if not data:
            return jsonify({"status": "error", "message": "Định dạng dữ liệu không hợp lệ."}), 400

        url = data.get("url", "").strip()
        server = data.get("server", "sv1")
        quantity = int(data.get("quantity", 0))
        
        # --- SỬA TẠI ĐÂY: Ép kiểu int() để tránh lỗi so sánh Số với Chuỗi ---
        total_price = int(data.get("total_price", 0))  
        note = data.get("note", "").strip()

        if not url or quantity < 500 or total_price <= 0:
            return jsonify({"status": "error", "message": "Dữ liệu đơn hàng hoặc số tiền không hợp lệ."}), 400

        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        
        if not user or user["auth_token"] != token:
            conn.close()
            return jsonify({"status": "error", "message": "Phiên làm việc đã kết thúc."}), 401

        current_balance = int(user["balance"]) # Đảm bảo số dư trong DB cũng là số nguyên
        
        # Kiểm tra số dư chuẩn số nguyên vs số nguyên
        if current_balance < total_price:
            conn.close()
            return jsonify({
                "status": "error", 
                "message": f"Số dư tài khoản không đủ để thanh toán đơn hàng này. Bạn còn thiếu {total_price - current_balance} VNĐ."
            }), 400

        # Nếu đủ tiền -> Tiến hành trừ tiền user trong cơ sở dữ liệu
        new_balance = current_balance - total_price
        cursor.execute("UPDATE users SET balance = %s WHERE username = %s", (new_balance, username))

        # Phân mức ưu tiên cho máy chủ chọn mua (Số bé đứng trước trong hàng đợi)
        priority = 1 if server == "sv2" else 2
        timestamp = time.time()

        # Đẩy công việc vào bảng `tiktok_view` ở trạng thái 'waiting'
        cursor.execute('''
            INSERT INTO tiktok_view (username, url, type, server, quantity, price, note, priority, status, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'waiting', %s)
        ''', (username, url, 'tiktok_view', server, quantity, total_price, note, priority, timestamp))

        conn.commit()
        conn.close()

        print(f"[SQL Hàng đợi] Đã thêm thành công job mới từ user {username} với số tiền {total_price} VNĐ")
        return jsonify({
            "status": "success",
            "message": "Đã tạo tiến trình thành công! Đơn hàng đã được đưa vào danh sách hàng đợi.",
            "new_coins": new_balance
        }), 200

    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return jsonify({"status": "error", "message": "Phiên xác thực đăng nhập không hợp lệ."}), 401
    except Exception as e:
        return jsonify({"status": "error", "message": f"Lỗi tạo tiến trình hệ thống: {str(e)}"}), 500

# -------------------------------------------------------------------------
# 5.5. API TIẾP NHẬN ĐƠN HÀNG TĂNG SHARE FACEBOOK (CÓ KIỂM TRA SỐ DƯ & LƯU PRICE)
# -------------------------------------------------------------------------
@app.route("/api/order/facebook-share", methods=["POST"])
def create_facebook_share_order():
    try:
        # Xác thực quyền sở hữu token đăng nhập
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"status": "error", "message": "Vui lòng đăng nhập hệ thống để tiếp tục!"}), 401

        token = auth_header.split(" ")[1]
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        username = payload["user"]

        # Nhận gói tin JSON từ Client gửi lên
        data = request.get_json()
        if not data:
            return jsonify({"status": "error", "message": "Định dạng dữ liệu không hợp lệ."}), 400

        url = data.get("url", "").strip()
        server = data.get("server", "sv1")
        quantity = int(data.get("quantity", 0))
        
        # --- SỬA TẠI ĐÂY: Ép kiểu int() để tránh lỗi so sánh Số với Chuỗi ---
        total_price = int(data.get("total_price", 0))  
        note = data.get("note", "").strip()

        if not url or quantity < 50 or total_price <= 0:
            return jsonify({"status": "error", "message": "Dữ liệu đơn hàng hoặc số tiền không hợp lệ."}), 400

        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        
        if not user or user["auth_token"] != token:
            conn.close()
            return jsonify({"status": "error", "message": "Phiên làm việc đã kết thúc."}), 401

        current_balance = int(user["balance"]) # Đảm bảo số dư trong DB cũng là số nguyên
        
        # Kiểm tra số dư chuẩn số nguyên vs số nguyên
        if current_balance < total_price:
            conn.close()
            return jsonify({
                "status": "error", 
                "message": f"Số dư tài khoản không đủ để thanh toán đơn hàng này. Bạn còn thiếu {total_price - current_balance} VNĐ."
            }), 400

        # Nếu đủ tiền -> Tiến hành trừ tiền user trong cơ sở dữ liệu
        new_balance = current_balance - total_price
        cursor.execute("UPDATE users SET balance = %s WHERE username = %s", (new_balance, username))

        # Phân mức ưu tiên cho máy chủ chọn mua (Số bé đứng trước trong hàng đợi)
        priority = 1 if server == "sv2" else 2
        timestamp = time.time()

        # Đẩy công việc vào bảng `facebook_share` ở trạng thái 'waiting'
        cursor.execute('''
            INSERT INTO facebook_share (username, url, type, server, quantity, price, note, priority, status, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'waiting', %s)
        ''', (username, url, 'facebook_share', server, quantity, total_price, note, priority, timestamp))

        conn.commit()
        conn.close()

        print(f"[SQL Hàng đợi] Đã thêm thành công job mới từ user {username} với số tiền {total_price} VNĐ")
        return jsonify({
            "status": "success",
            "message": "Đã tạo tiến trình thành công! Đơn hàng đã được đưa vào danh sách hàng đợi.",
            "new_coins": new_balance
        }), 200

    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return jsonify({"status": "error", "message": "Phiên xác thực đăng nhập không hợp lệ."}), 401
    except Exception as e:
        return jsonify({"status": "error", "message": f"Lỗi tạo tiến trình hệ thống: {str(e)}"}), 500


# -------------------------------------------------------------------------
# 6. API ADMIN: CỘNG TIỀN CHO NGƯỜI DÙNG NHANH CHÓNG
# -------------------------------------------------------------------------
@app.route("/api/admin/add-balance", methods=["POST"])
def admin_add_balance():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"status": "error", "message": "Gói tin không hợp lệ."}), 400
            
        username = data.get("username")
        amount = int(data.get("amount", 0))

        if not username or amount <= 0:
            return jsonify({"status": "error", "message": "Tên tài khoản hoặc số tiền cộng phải lớn hơn 0."}), 400

        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT balance FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        
        if not user:
            conn.close()
            return jsonify({"status": "error", "message": "Không tồn tại người dùng này trên hệ thống."}), 404
            
        new_balance = user["balance"] + amount
        cursor.execute("UPDATE users SET balance = %s WHERE username = %s", (new_balance, username))
        
        conn.commit()
        conn.close()
        
        print(f"[ADMIN KHỞI CHẠY] Nạp thành công {amount} VNĐ cho tài khoản: {username}")
        return jsonify({
            "status": "success", 
            "message": f"Đã tăng thành công {amount} VNĐ cho tài khoản {username}.",
            "new_balance": new_balance
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": f"Lỗi hệ thống nạp ví: {str(e)}"}), 500


# -------------------------------------------------------------------------
# 7. API LINK RÚT GỌN (TẠO NHIỆM VỤ & XÁC NHẬN KEY)
# -------------------------------------------------------------------------
@app.route("/api/task/generate", methods=["POST"])
def generate_task_api():
    try:
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"status": "error", "message": "Vui lòng đăng nhập!"}), 401

        token = auth_header.split(" ")[1]
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        username = payload["user"]

        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT auth_token FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        if not user or user["auth_token"] != token:
            conn.close()
            return jsonify({"status": "error", "message": "Phiên làm việc không hợp lệ."}), 401

        # Tạo key
        now = datetime.datetime.now()
        raw_string = f"{now.hour}{now.day}{now.month}{now.year}{username}{random.randint(1, 1000)}"
        key = hashlib.md5(raw_string.encode('utf-8')).hexdigest()

        # Lưu key vào db
        timestamp = time.time()
        cursor.execute("INSERT INTO task_keys (key, username, created_at) VALUES (%s, %s, %s)", (key, username, timestamp))
        conn.commit()
        conn.close()

        # Lấy server user chọn
        data = request.get_json() or {}
        server = data.get("server", "sv1")

        # Tạo link rút gọn
        destination_url = f"https://www.huyvx.online/get-key?key={key}"
        
        try:
            if server == "sv2":
                api_url = f"https://yeumoney.com/QL_api.php?token=9fb74e28d941538e01d71552386f86241f9aff7ddc1da57786993ccc528c534c&format=json&url={destination_url}"
                resp = requests.get(api_url, timeout=10)
                data_resp = resp.json()
                if data_resp.get("status") == "success":
                    short_url = data_resp.get("shortenedUrl")
                else:
                    short_url = destination_url
            elif server == "sv3":
                api_url = f"https://api.layma.net/api/admin/shortlink/quicklink?tokenUser=10eaad794c00892994bbea04b8d910a7&format=json&url={destination_url}"
                resp = requests.get(api_url, timeout=10)
                data_resp = resp.json()
                if data_resp.get("success") is True:
                    short_url = data_resp.get("html")
                else:
                    short_url = destination_url
            else:
                api_url = f"https://link4m.co/api-shorten/v2?api=69c8d401760509710940c862&url={destination_url}"
                resp = requests.get(api_url, timeout=10)
                data_resp = resp.json()
                if data_resp.get("status") == "success":
                    short_url = data_resp.get("shortenedUrl")
                else:
                    short_url = destination_url
        except Exception as e:
            short_url = destination_url

        return jsonify({
            "status": "success",
            "short_url": short_url
        }), 200

    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return jsonify({"status": "error", "message": "Phiên xác thực đăng nhập không hợp lệ."}), 401
    except Exception as e:
        return jsonify({"status": "error", "message": f"Lỗi tạo nhiệm vụ: {str(e)}"}), 500

@app.route("/api/task/verify", methods=["POST"])
def verify_task_api():
    try:
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"status": "error", "message": "Vui lòng đăng nhập!"}), 401

        token = auth_header.split(" ")[1]
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        username = payload["user"]

        data = request.get_json()
        if not data:
            return jsonify({"status": "error", "message": "Dữ liệu không hợp lệ."}), 400

        key = data.get("key", "").strip()
        if not key:
            return jsonify({"status": "error", "message": "Vui lòng nhập mã xác nhận."}), 400

        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Kiểm tra token hợp lệ
        cursor.execute("SELECT balance, auth_token FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        if not user or user["auth_token"] != token:
            conn.close()
            return jsonify({"status": "error", "message": "Phiên làm việc không hợp lệ."}), 401

        # Kiểm tra key
        cursor.execute("SELECT * FROM task_keys WHERE key = %s AND username = %s", (key, username))
        task = cursor.fetchone()

        if not task:
            conn.close()
            return jsonify({"status": "error", "message": "Mã xác nhận không hợp lệ hoặc không thuộc về bạn!"}), 400

        # Đúng key, xoá key và cộng tiền
        cursor.execute("DELETE FROM task_keys WHERE key = %s", (key,))
        
        new_balance = user["balance"] + 300
        cursor.execute("UPDATE users SET balance = %s WHERE username = %s", (new_balance, username))
        
        conn.commit()
        conn.close()

        return jsonify({
            "status": "success",
            "message": "Cộng thành công 300 VNĐ vào tài khoản!",
            "new_balance": new_balance
        }), 200

    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return jsonify({"status": "error", "message": "Phiên xác thực đăng nhập không hợp lệ."}), 401
    except Exception as e:
        return jsonify({"status": "error", "message": f"Lỗi xác nhận mã: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(host="localhost", port=8080, debug=True)