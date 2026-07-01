document.addEventListener("DOMContentLoaded", function () {
  const formOrder = document.getElementById("form-order-share");
  if (!formOrder) return;

  const inputUrl = document.getElementById("post-url");
  const inputQuantity = document.getElementById("share-quantity");
  const inputNote = document.getElementById("order-note");
  const radioServers = document.getElementsByName("server-select");
  const txtSinglePrice = document.getElementById("single-price");
  const txtTotalPrice = document.getElementById("total-price");
  const userCoinsElement = document.getElementById("user-coins");

  // Lấy thẻ chứa thông báo động
  const messageBox = document.getElementById("form-message-box");

  const priceConfig = {
    sv1: 15,
    sv2: 35,
  };

  // HÀM HIỂN THỊ THÔNG BÁO: Tạo khoảng cách với nút bên dưới khi xuất hiện
  function showMessage(text, type) {
    if (!messageBox) return;
    messageBox.innerText = text;
    messageBox.style.marginBottom = "15px"; // Tạo khoảng cách 15px an toàn với nút bấm bên dưới

    if (type === "success") {
      messageBox.style.color = "#22c55e"; // Màu xanh lá thành công
    } else {
      messageBox.style.color = "#ef4444"; // Màu đỏ cảnh báo lỗi
    }
  }

  // HÀM XÓA THÔNG BÁO: Triệt tiêu khoảng cách để nút bấm khít lại vị trí cũ
  function clearMessage() {
    if (!messageBox) return;
    messageBox.innerText = "";
    messageBox.style.marginBottom = "0px"; // Đưa khoảng cách về 0px khi trống dữ liệu
  }

  function getCurrentCoins() {
    if (!userCoinsElement) return 0;
    return parseInt(userCoinsElement.innerText.replace(/[^0-9]/g, "")) || 0;
  }

  function calculateTotal() {
    let selectedServer = "sv1";
    for (const radio of radioServers) {
      if (radio.checked) {
        selectedServer = radio.value;
        break;
      }
    }

    const pricePerShare = priceConfig[selectedServer];
    const quantity = parseInt(inputQuantity.value) || 0;
    const total = pricePerShare * quantity;

    txtSinglePrice.innerText = pricePerShare.toLocaleString("vi-VN") + " VNĐ";
    txtTotalPrice.innerText = total.toLocaleString("vi-VN") + " VNĐ";

    return total;
  }

  // Lắng nghe sự kiện để xóa thông báo và thu hẹp khoảng cách ngay khi người dùng chỉnh sửa đơn
  inputQuantity.addEventListener("input", function () {
    calculateTotal();
    clearMessage();
  });

  radioServers.forEach((radio) =>
    radio.addEventListener("change", function () {
      calculateTotal();
      clearMessage();
    }),
  );

  // XỬ LÝ SỰ KIỆN SUBMIT TẠO TIẾN TRÌNH
  formOrder.addEventListener("submit", function (e) {
    e.preventDefault();
    clearMessage(); // Xóa sạch trạng thái cũ

    const currentCoins = getCurrentCoins();
    const totalCost = calculateTotal();

    // 1. Kiểm tra số tiền trong ví
    if (currentCoins < totalCost) {
      const missingAmount = (totalCost - currentCoins).toLocaleString("vi-VN");
      showMessage(
        `Tạo đơn thất bại! Số dư không đủ, thiếu ${missingAmount} VNĐ.`,
        "error",
      );
      return;
    }

    let selectedServer = "sv1";
    for (const radio of radioServers) {
      if (radio.checked) {
        selectedServer = radio.value;
        break;
      }
    }

    const orderData = {
      url: inputUrl.value.trim(),
      server: selectedServer,
      quantity: parseInt(inputQuantity.value) || 0,
      note: inputNote.value.trim(),
      total_price: totalCost,
    };

    const token = localStorage.getItem("authToken");

    // 2. Gửi request API lên hệ thống backend
    fetch("/api/order/tiktok-view", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: "Bearer " + token,
      },
      body: JSON.stringify(orderData),
    })
      .then((response) => {
        if (response.ok) return response.json();
        throw new Error("Lỗi kết nối máy chủ.");
      })
      .then((data) => {
        if (data.status === "success") {
          showMessage(
            "Chúc mừng! Bạn đã tạo tiến trình tăng view Tiktok thành công.",
            "success",
          );

          if (data.new_coins !== undefined && userCoinsElement) {
            userCoinsElement.innerText = data.new_coins.toLocaleString("vi-VN");
          }

          formOrder.reset();
          calculateTotal();
        } else {
          showMessage("Thất bại: " + data.message, "error");
        }
      })
      .catch((err) => {
        console.error(err);
        showMessage(
          "Đã xảy ra lỗi trong quá trình kết nối đến hệ thống!",
          "error",
        );
      });
  });
});
