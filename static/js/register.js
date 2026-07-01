document
  .getElementById("registerForm")
  .addEventListener("submit", function (event) {
    event.preventDefault();

    const userField = document.getElementById("username");
    const passField = document.getElementById("password");
    const rePassField = document.getElementById("rePassword");

    const taiKhoan = userField.value.trim();
    const matKhau = passField.value;
    const nhapLaiMatKhau = rePassField.value;

    // 1. Kiểm tra mật khẩu trùng khớp ở Frontend trước
    if (matKhau !== nhapLaiMatKhau) {
      alert("Lỗi: Mật khẩu nhập lại không trùng khớp!");
      return;
    }

    // 2. Ép định dạng x-www-form-urlencoded chuẩn
    const rawBody = `username=${encodeURIComponent(taiKhoan)}&password=${encodeURIComponent(matKhau)}`;

    // 3. Bắn request lên API đăng ký
    fetch("/api/register", {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
      body: rawBody,
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.status === "success") {
          // Đăng ký thành công -> nhảy thẳng sang trang login không alert lằng nhằng
          window.location.href = "https://www.huyvx.online/login";
        } else {
          // Hiển thị lỗi nếu tài khoản đã tồn tại
          alert("Thất bại: " + data.message);
        }
      })
      .catch((err) => {
        console.error("Lỗi kết nối Server:", err);
      });
  });
