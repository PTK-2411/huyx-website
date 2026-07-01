document.addEventListener("DOMContentLoaded", () => {
  const btnGenerateTask = document.getElementById("btnGenerateTask");
  const taskActions = document.getElementById("taskActions");
  const taskStep = document.getElementById("taskStep");
  const shortLink = document.getElementById("shortLink");
  const taskKeyInput = document.getElementById("taskKey");
  const btnVerifyTask = document.getElementById("btnVerifyTask");

  if (!btnGenerateTask) return; // Không có thì return luôn

  btnGenerateTask.addEventListener("click", async () => {
    const token = localStorage.getItem("authToken");
    if (!token) {
      alert("Vui lòng đăng nhập để thực hiện nhiệm vụ!");
      window.location.href = "/login";
      return;
    }

    // Disable button to prevent multiple clicks
    const originalText = btnGenerateTask.innerHTML;
    btnGenerateTask.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Đang tạo...';
    btnGenerateTask.disabled = true;

    const selectedServerRadio = document.querySelector('input[name="server-select"]:checked');
    const selectedServer = selectedServerRadio ? selectedServerRadio.value : "sv1";

    try {
      const response = await fetch("/api/task/generate", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify({ server: selectedServer })
      });

      const data = await response.json();
      if (data.status === "success") {
        shortLink.href = data.short_url;
        shortLink.textContent = data.short_url;
        
        taskActions.style.display = "none";
        taskStep.style.display = "block";
        
        const serverGroup = document.getElementById("serverSelectionGroup");
        if (serverGroup) serverGroup.style.display = "none";
      } else {
        alert(data.message || "Có lỗi xảy ra khi tạo nhiệm vụ.");
        btnGenerateTask.innerHTML = originalText;
        btnGenerateTask.disabled = false;
      }
    } catch (error) {
      console.error("Lỗi:", error);
      alert("Lỗi kết nối máy chủ!");
      btnGenerateTask.innerHTML = originalText;
      btnGenerateTask.disabled = false;
    }
  });

  btnVerifyTask.addEventListener("click", async () => {
    const token = localStorage.getItem("authToken");
    const key = taskKeyInput.value.trim();

    if (!key) {
      alert("Vui lòng nhập mã xác nhận (Key)!");
      taskKeyInput.focus();
      return;
    }

    if (!token) {
      alert("Vui lòng đăng nhập!");
      window.location.href = "/login";
      return;
    }

    const originalText = btnVerifyTask.innerHTML;
    btnVerifyTask.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Đang kiểm tra...';
    btnVerifyTask.disabled = true;

    try {
      const response = await fetch("/api/task/verify", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify({ key })
      });

      const data = await response.json();
      if (data.status === "success") {
        alert(data.message);
        // Cập nhật số dư hiển thị
        const userCoinsElement = document.getElementById("user-coins");
        if (userCoinsElement && data.new_balance !== undefined) {
          userCoinsElement.textContent = data.new_balance.toLocaleString("vi-VN");
        }
        
        // Reset giao diện
        taskKeyInput.value = "";
        taskStep.style.display = "none";
        taskActions.style.display = "block";
        const serverGroup = document.getElementById("serverSelectionGroup");
        if (serverGroup) serverGroup.style.display = "block";
        btnGenerateTask.innerHTML = '<i class="fa-solid fa-plus"></i> Tạo nhiệm vụ mới';
        btnGenerateTask.disabled = false;
      } else {
        alert(data.message || "Key không hợp lệ hoặc không thuộc về bạn.");
      }
    } catch (error) {
      console.error("Lỗi:", error);
      alert("Lỗi kết nối máy chủ!");
    } finally {
      btnVerifyTask.innerHTML = originalText;
      btnVerifyTask.disabled = false;
    }
  });
});
