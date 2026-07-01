document.addEventListener("DOMContentLoaded", function () {
  // Hàm tự động load bảng xếp hạng đại phú
  function loadLeaderboard() {
    const listContainer = document.getElementById("top-wealthy-list");
    const refreshTime = document.getElementById("ranking-refresh-time");

    if (!listContainer) return;

    fetch("/api/leaderboard")
      .then((response) => response.json())
      .then((res) => {
        if (res.status === "success" && res.data) {
          listContainer.innerHTML = ""; // Xóa dữ liệu loading cũ

          res.data.forEach((user, index) => {
            const rankNumber = index + 1;

            // Phân cấp danh hiệu hiển thị dựa trên thứ hạng hoặc Role của họ
            let badgeHTML = "";
            if (user.role === "Admin") {
              badgeHTML = `<span class="rank-badge badge-thachdau">Admin</span>`;
            } else if (rankNumber === 1) {
              badgeHTML = `<span class="rank-badge badge-thachdau">Top 1</span>`;
            } else if (rankNumber <= 3) {
              badgeHTML = `<span class="rank-badge badge-caothu">Đại Gia</span>`;
            } else {
              badgeHTML = `<span class="rank-badge badge-kimcuong">Thành Viên</span>`;
            }

            // Định dạng số dư tiền mặt sang chuỗi phân tách dấu chấm VNĐ
            const formattedBalance =
              user.balance.toLocaleString("vi-VN") + " VNĐ";

            // Tạo cấu trúc hàng xếp hạng mới
            const itemHTML = `
              <div class="ranking-item">
                <div class="avatar-box" style="${rankNumber <= 3 ? "border-color: #f59e0b; color: #f59e0b;" : ""}">
                  ${rankNumber}
                </div>
                <div class="rank-info">
                  <div class="rank-user">
                    ${user.username} ${badgeHTML}
                  </div>
                  <div class="rank-score">${formattedBalance}</div>
                </div>
              </div>
            `;
            listContainer.insertAdjacentHTML("beforeend", itemHTML);
          });

          // Cập nhật thời gian đồng bộ trên giao diện
          if (refreshTime) {
            const now = new Date();
            refreshTime.innerText = `Cập nhật: ${now.getHours().toString().padStart(2, "0")}:${now.getMinutes().toString().padStart(2, "0")}`;
          }
        }
      })
      .catch((err) => {
        console.error("Lỗi tải BXH đại phú:", err);
        listContainer.innerHTML = `<div style="color: #ef4444; font-size: 0.9rem;">Không thể tải bảng xếp hạng!</div>`;
      });
  }

  // Chạy ngay khi tải xong trang index
  loadLeaderboard();
});
