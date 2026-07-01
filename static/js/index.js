document.addEventListener("DOMContentLoaded", function () {
  // 1. KHỞI TẠO NỀN PARTICLES JS
  if (typeof particlesJS !== "undefined") {
    particlesJS("particles-js", {
      "particles": {
        "number": { "value": 100, "density": { "enable": true, "value_area": 800 } },
        "color": { "value": "#00ffcc" },
        "shape": { "type": "circle" },
        "opacity": { "value": 0.6, "random": true },
        "size": { "value": 3, "random": true },
        "line_linked": { "enable": true, "distance": 150, "color": "#00ffcc", "opacity": 0.3, "width": 1 },
        "move": { "enable": true, "speed": 1, "direction": "none", "out_mode": "out" }
      },
      "interactivity": {
        "detect_on": "canvas",
        "events": {
          "onhover": { "enable": true, "mode": "grab" },
          "onclick": { "enable": false, "mode": "none" }
        },
        "modes": { "grab": { "distance": 140, "line_linked": { "opacity": 0.8 } } }
      },
      "retina_detect": true
    });
  }

  // 2. KIỂM TRA QUYỀN TRUY CẬP (TOKEN)
  const token = localStorage.getItem("authToken");
  if (!token) {
    window.location.href = "/login";
    return;
  }

  fetch("/api/me", {
    method: "POST",
    headers: {
      Authorization: "Bearer " + token,
    },
  })
    .then((response) => {
      if (response.status === 200) {
        return response.json();
      } else {
        localStorage.removeItem("authToken");
        window.location.href = "/login";
        throw new Error("Xác thực token thất bại");
      }
    })
    .then((data) => {
      document.getElementById("user-display").innerText = data.username;
      const coinsElement = document.getElementById("user-coins");
      if (coinsElement && data.coins !== undefined) {
        coinsElement.innerText = data.coins.toLocaleString("vi-VN");
      }

      const loadingScreen = document.getElementById("loading-screen");
      if (loadingScreen) {
        loadingScreen.style.opacity = "0";
        setTimeout(() => {
          loadingScreen.remove();
        }, 300);
      }
    })
    .catch((err) => console.log("Lỗi luồng xử lý hệ thống:", err.message));

  // 3. ĐÓNG / MỞ MENU BÊN TRÁI (TOGGLE SIDEBAR)
  const btnToggleSidebar = document.getElementById("btnToggleSidebar");
  const sidebar = document.querySelector(".sidebar");
  if (btnToggleSidebar && sidebar) {
    btnToggleSidebar.addEventListener("click", function () {
      sidebar.classList.toggle("collapsed");
    });
  }

  // 4. HIỆU ỨNG RÊ CHUỘT KHI DÙNG SUBMENU SIDEBAR
  const menuItemsWithSubmenu = document.querySelectorAll(".sidebar-menu .has-submenu");
  menuItemsWithSubmenu.forEach((item) => {
    const submenu = item.querySelector(".submenu");
    const arrowIcon = item.querySelector(".arrow-icon");

    item.addEventListener("mouseenter", function () {
      if (submenu && submenu.classList.contains("submenu")) {
        submenu.classList.add("open");
        if (arrowIcon) {
          arrowIcon.classList.remove("fa-chevron-up");
          arrowIcon.classList.add("fa-chevron-down");
        }
      }
    });

    item.addEventListener("mouseleave", function () {
      if (submenu && submenu.classList.contains("submenu")) {
        submenu.classList.remove("open");
        if (arrowIcon) {
          arrowIcon.classList.remove("fa-chevron-down");
          arrowIcon.classList.add("fa-chevron-up");
        }
      }
    });
  });

  // 5. ĐIỀU HƯỚNG VÀO TRANG HỒ SƠ CÁ NHÂN
  const userProfileTrigger = document.getElementById("userProfileTrigger");
  if (userProfileTrigger) {
    userProfileTrigger.addEventListener("click", function () {
      window.location.href = "/profile";
    });
  }

  // 6. SỰ KIỆN NÚT ĐĂNG XUẤT
  const btnLogout = document.getElementById("btnLogout");
  if (btnLogout) {
    btnLogout.addEventListener("click", function () {
      localStorage.removeItem("authToken");
      window.location.href = "/login";
    });
  }

  // 7. LOAD BẢNG XẾP HẠNG
  function loadLeaderboard() {
    const listContainer = document.getElementById("top-wealthy-list");
    const refreshTime = document.getElementById("ranking-refresh-time");

    if (!listContainer) return;

    fetch("/api/leaderboard")
      .then((response) => response.json())
      .then((res) => {
        if (res.status === "success" && res.data) {
          listContainer.innerHTML = "";
          res.data.forEach((user, index) => {
            const rankNumber = index + 1;
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

            const formattedBalance = user.balance.toLocaleString("vi-VN") + " VNĐ";
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

  loadLeaderboard();
});
