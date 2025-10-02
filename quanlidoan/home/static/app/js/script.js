function showMessage(type, message) {
    const container = document.getElementById("notification-container");

    // Tạo div thông báo
    const notification = document.createElement("div");
    notification.classList.add("notification", type);
    notification.textContent = message;

    // Thêm vào container
    container.appendChild(notification);

    // Xóa sau 3s
    setTimeout(() => {
        notification.remove();
    }, 3000);
}
