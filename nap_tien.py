import sqlite3

def tang_tien_user(username, sotien):
    # Kết nối trực tiếp vào file database
    conn = sqlite3.connect("system.db")
    cursor = conn.cursor()
    
    # Thực thi lệnh cộng dồn tiền
    cursor.execute("""
        UPDATE users 
        SET balance = balance + ? 
        WHERE username = ?
    """, (sotien, username))
    
    # Kiểm tra xem có dòng nào được cập nhật không
    if cursor.rowcount > 0:
        print(f"-> Đã cộng thành công {sotien} VNĐ cho tài khoản: {username}")
    else:
        print(f"-> Lỗi: Không tìm thấy người dùng có tên '{username}'")
        
    conn.commit()
    conn.close()

# --- SỬ DỤNG: Điền tên và số tiền cần tăng ở đây ---
user_can_tang = "Huy@12031985"   # Nhập username người nhận
so_tien_nap = 1000000      # Số tiền muốn cộng thêm (ví dụ 100k)

tang_tien_user(user_can_tang, so_tien_nap)