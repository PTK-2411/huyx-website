document.addEventListener("DOMContentLoaded", function () {
  const token = localStorage.getItem("authToken");

  // 1. Kiểm tra quyền truy cập Token đầu tiên để chặn tải tài nguyên thừa
  if (!token) {
    window.location.href = "/login";
    return;
  }

  // 2. Lấy thông tin tài khoản thời gian thực từ Server Python
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
        throw new Error("Xác thực Token không hợp lệ");
      }
    })
    .then((data) => {
      // Đổ dữ liệu an toàn vào giao diện HTML
      document.getElementById("profile-name-title").innerText = data.username;
      document.getElementById("profile-username").value = data.username;
      document.getElementById("profile-balance").value =
        document.getElementById("profile-balance").value =
          data.coins.toLocaleString("vi-VN") + " VNĐ";
      document.getElementById("profile-token").value = token;

      // XỬ LÝ ĐỔ ROLE ĐỘNG:
      const roleElement = document.getElementById("profile-role-title");
      if (roleElement) {
        roleElement.innerText = data.role;

        if (data.role === "Admin") {
          roleElement.style.color = "#f59e0b"; // Màu vàng cam cho Admin
          roleElement.style.fontWeight = "bold";
        } else {
          roleElement.style.color = "#64748b"; // Màu xám cho Member
        }
      }

      // Giải phóng màn hình chờ
      const loadingScreen = document.getElementById("loading-screen");
      if (loadingScreen) {
        loadingScreen.style.opacity = "0";
        setTimeout(() => loadingScreen.remove(), 300);
      }
    })
    .catch((err) =>
      console.error("Lỗi đồng bộ hệ thống Profile:", err.message),
    );

  // ========================================================
  // NÚT BẤM SAO CHÉP (COPY) ACCESS TOKEN MỚI THÊM
  // ========================================================
  const btnCopy = document.getElementById("btn-copy-token");
  if (btnCopy) {
    btnCopy.addEventListener("click", function () {
      const tokenValue = document.getElementById("profile-token").value;

      if (!tokenValue || tokenValue === "Đang tải...") {
        alert("Chưa có dữ liệu token để sao chép!");
        return;
      }

      // Sử dụng API Clipboard hiện đại của trình duyệt
      navigator.clipboard
        .writeText(tokenValue)
        .then(() => {
          // Hiệu ứng đổi chữ tạm thời để người dùng biết đã copy thành công
          const originalHTML = btnCopy.innerHTML;
          btnCopy.innerHTML = '<i class="fa-solid fa-check"></i> Copied!';
          btnCopy.style.backgroundColor = "#10b981"; // Đổi sang màu xanh lá mượt mà

          setTimeout(() => {
            btnCopy.innerHTML = originalHTML;
            btnCopy.style.backgroundColor = ""; // Trả về màu xanh dương ban đầu trong profile.css
          }, 1500);
        })
        .catch((err) => {
          console.error("Lỗi khi sao chép:", err);
          alert(
            "Trình duyệt không hỗ trợ tự động sao chép, vui lòng copy thủ công!",
          );
        });
    });
  }

  // 3. Xử lý sự kiện Submit Đổi mật khẩu kết nối Backend API
  const formPassword = document.getElementById("form-change-password");
  if (formPassword) {
    formPassword.addEventListener("submit", function (e) {
      e.preventDefault();

      const oldPass = document.getElementById("old-password").value;
      const newPass = document.getElementById("new-password").value;
      const confirmPass = document.getElementById("confirm-password").value;

      if (newPass !== confirmPass) {
        alert("Mật khẩu mới nhập lại không trùng khớp!");
        return;
      }

      const formData = new FormData();
      formData.append("old_password", oldPass);
      formData.append("new_password", newPass);

      fetch("/api/change-password", {
        method: "POST",
        headers: {
          Authorization: "Bearer " + token,
        },
        body: formData,
      })
        .then((response) => response.json())
        .then((resData) => {
          if (resData.status === "success") {
            alert("Chúc mừng! Bạn đã đổi mật khẩu thành công.");
            formPassword.reset();
          } else {
            alert(resData.message);
          }
        })
        .catch((err) => {
          console.error("Lỗi kết nối đổi mật khẩu:", err);
          alert("Có lỗi xảy ra khi gửi yêu cầu tới máy chủ.");
        });
    });
  }
});
