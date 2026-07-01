import sqlite3
import time

DB_FILE = "system.db"  # Đường dẫn tới file database chung

def get_db_connection():
    """Tạo kết nối tới cơ sở dữ liệu SQLite"""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def process_jobs():
    print("[HỆ THỐNG WORKER] Đang chạy bộ quét và xử lý đơn hàng tập trung...")
    print(" -> Tiêu chí: Ưu tiên Máy chủ SV2 trước, SV1 sau. Đơn nhỏ ID thấp chạy trước.\n")
    
    while True:
        conn = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # 1. ĐỌC VÀ SẮP XẾP DỮ LIỆU THEO TIÊU CHÍ:
            # - Chỉ lấy các job đang ở trạng thái chờ ('waiting')
            # - Sắp xếp SV2 lên trước SV1 bằng câu lệnh CASE WHEN (sv2 nhận trọng số 1, sv1 nhận trọng số 2)
            # - Tiếp theo, nếu cùng một server thì ai có id nhỏ hơn (vào trước) sẽ được sắp xếp lên trước.
            cursor.execute('''
                SELECT id, server, type, url, quantity, price, 'tiktok_view' as table_name 
                FROM tiktok_view 
                WHERE status = 'waiting'
                UNION ALL
                SELECT id, server, type, url, quantity, price, 'facebook_share' as table_name 
                FROM facebook_share 
                WHERE status = 'waiting'
                ORDER BY 
                    CASE WHEN server = 'sv2' THEN 1 ELSE 2 END ASC,
                    id ASC
                LIMIT 1
            ''')
            
            job = cursor.fetchone()
            
            if job:
                job_id = job['id']
                table_name = job['table_name']
                
                # 2. CHỐNG TRANH GIÀNH JOB (ATOM LOCKING):
                # Thay đổi trạng thái từ 'waiting' sang 'processing' (đang thực hiện).
                # Điều kiện bắt buộc: 'WHERE id = ? AND status = 'waiting''
                # Nếu có máy khác đã nhanh tay giành mất job này trước 1 phần triệu giây, 
                # câu lệnh dưới đây sẽ cập nhật thất bại (rowcount == 0), giúp tránh chạy trùng đơn.
                cursor.execute(f'''
                    UPDATE {table_name} 
                    SET status = 'processing' 
                    WHERE id = ? AND status = 'waiting'
                ''', (job_id,))
                conn.commit()
                
                # Kiểm tra xem máy này có thực sự khóa và giành được job thành công không
                if cursor.rowcount > 0:
                    print(f"[TIẾN TRÌNH] -> Đã giành quyền xử lý thành công đơn hàng ID #{job_id}")
                    print(f"   |-- Dịch vụ: {job['type']} | Máy chủ: {job['server']}")
                    print(f"   |-- Liên kết: {job['url']}")
                    print(f"   |-- Số lượng: {job['quantity']} | Tổng chi trả: {job['price']} VNĐ")
                    print(f"   |-- Bảng lưu trữ: {table_name}")
                    
                    # -------------------------------------------------------------
                    # 3. ĐOẠN CHÈN SCRIPT XỬ LÝ (BOT / SELENIUM / CHROMEDRIVER CỦA BẠN)
                    # -------------------------------------------------------------
                    try:
                        # Giả lập thời gian công cụ của bạn chạy thực tế (ví dụ: mất 8 giây để buff xong)
                        time.sleep(8) 
                        
                        # Giả sử tool của bạn chạy thành công không có lỗi gì xảy ra:
                        job_success = True 
                    except Exception as tool_err:
                        print(f"   |-- Lỗi trong lúc tool đang chạy đơn #{job_id}: {str(tool_err)}")
                        job_success = False
                    # -------------------------------------------------------------
                    
                    # 4. HOÀN THÀNH JOB (Cập nhật trạng thái thành 'success')
                    if job_success:
                        cursor.execute(f"UPDATE {table_name} SET status = 'success' WHERE id = ?", (job_id,))
                        conn.commit()
                        print(f"[THÀNH CÔNG] -> Đơn hàng ID #{job_id} đã hoàn thành và cập nhật trạng thái sang 'success'.\n")
                    else:
                        # Nếu tool lỗi, có thể trả về trạng thái 'error' để bạn kiểm tra lại sau
                        cursor.execute(f"UPDATE {table_name} SET status = 'error' WHERE id = ?", (job_id,))
                        conn.commit()
                        print(f"[THẤT BẠI] -> Đơn hàng ID #{job_id} gặp sự cố vận hành.\n")
                        
                else:
                    # Rơi vào trường hợp này nghĩa là job_id này vừa bị một máy khác khóa trước rồi
                    print(f"[TRANH CHẤP CHIẾM ĐƠN] Hụt đơn ID #{job_id}, đang bỏ qua để tìm đơn khác...")
                    continue
            
            else:
                # Nếu không có đơn nào ở trạng thái 'waiting', ngủ 1 giây rồi tiếp tục quét database
                time.sleep(10)
                
        except Exception as e:
            print(f"[LỖI HỆ THỐNG VẬN HÀNH JOB]: {str(e)}")
            time.sleep(2)
        finally:
            if conn:
                conn.close()

if __name__ == "__main__":
    process_jobs()