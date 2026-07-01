document.addEventListener("DOMContentLoaded", function () {

  // Lấy tất cả các mục lớn cha có chứa menu con (thẻ <li> có class .has-submenu)
  const menuItemsWithSubmenu = document.querySelectorAll(
    ".sidebar-menu .has-submenu",
  );

  menuItemsWithSubmenu.forEach((item) => {
    const submenu = item.querySelector(".submenu");
    const arrowIcon = item.querySelector(".arrow-icon");

    // 1. KHI CON TRỎ CHUỘT RÊ VÀO PHẠM VI MỤC CHA (Hoặc các mục con bên trong)
    item.addEventListener("mouseenter", function () {
      if (submenu && submenu.classList.contains("submenu")) {
        // Tự động mở mục ra bằng hiệu ứng trượt xuống
        submenu.classList.add("open");

        // Đổi mũi tên từ HƯỚNG LÊN thành HƯỚNG XUỐNG
        if (arrowIcon) {
          arrowIcon.classList.remove("fa-chevron-up");
          arrowIcon.classList.add("fa-chevron-down");
        }
      }
    });

    // 2. KHI CON TRỎ CHUỘT RỜI KHỎI TOÀN BỘ PHẠM VI MỤC CHA VÀ MENU CON
    item.addEventListener("mouseleave", function () {
      if (submenu && submenu.classList.contains("submenu")) {
        // Tự động đóng mục lại (thu menu từ từ lên trên)
        submenu.classList.remove("open");

        // Trả lại mũi tên HƯỚNG LÊN mặc định
        if (arrowIcon) {
          arrowIcon.classList.remove("fa-chevron-down");
          arrowIcon.classList.add("fa-chevron-up");
        }
      }
    });
  });
});
