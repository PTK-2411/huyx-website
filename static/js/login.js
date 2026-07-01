document
  .getElementById("loginForm")
  .addEventListener("submit", function (event) {
    // 1. Chặn load lại trang
    event.preventDefault();

    console.log("Đã kích hoạt sự kiện Submit!");

    try {
      // 2. Lấy chính xác ID từ HTML của bạn (username và password)
      const userField = document.getElementById("username");
      const passField = document.getElementById("password");
      const rememberField = document.getElementById("remember");

      if (!userField || !passField) {
        console.error(
          "LỖI: Không tìm thấy ô input username hoặc password trong HTML!",
        );
        return;
      }

      const taiKhoan = userField.value;
      const matKhau = passField.value;
      const nhoMatKhau = rememberField ? rememberField.checked : false;

      // 3. Ép định dạng CHUỖI THUẦN (giống hệt: data='username=ptkhoa&password=...')
      // Dùng encodeURIComponent để nó tự đổi các ký tự như @, !, / thành %40, %2F y hệt Python
      const rawBody = `username=${encodeURIComponent(taiKhoan)}&password=${encodeURIComponent(matKhau)}&remember=${nhoMatKhau}`;

      console.log("Chuỗi data chuẩn bị gửi đi:", rawBody);

      // 4. Thực hiện bắn Request
      fetch("/api/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
        body: rawBody,
      })
        .then((response) => {
          console.log("Server phản hồi với Status Code:", response.status);
          return response.json();
        })
        .then((data) => {
          console.log("Dữ liệu trả về từ Server:", data);
          if (data.status === "success") {
            // 1. Lưu token tự động vào trình duyệt
            localStorage.setItem("authToken", data.token);

            // 2. Không thông báo, đá thẳng về trang chủ index ngay lập tức
            window.location.href = "https://www.huyvx.online/";
          } else {
            alert("Thất bại: " + data.message);
          }
        })
        .catch((err) => {
          console.error("Lỗi khi fetch (Có thể sập server hoặc sai URL):", err);
        });
    } catch (error) {
      console.error("JS bị crash giữa chừng do lỗi logic cấu trúc:", error);
    }
  });
