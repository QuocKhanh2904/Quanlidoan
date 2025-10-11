function showToast(message, status) {
    const toastContainer = document.querySelector('.toast-container');

    const toast = document.createElement("div");
    toast.className = `toast align-items-center text-bg-${status === "success" ? "success" : "danger"} border-0`;
    toast.setAttribute("role", "alert");
    toast.setAttribute("aria-live", "assertive");
    toast.setAttribute("aria-atomic", "true");

    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
    `;

    toastContainer.appendChild(toast);

    const bsToast = new bootstrap.Toast(toast, { delay: 3000 });
    bsToast.show();

    // Xóa sau khi ẩn
    toast.addEventListener('hidden.bs.toast', () => {
        toast.remove();
    });
}

// Hàm gửi request đăng ký
function registerTopic(topicId, action, button) {
    button.innerHTML = "⏳ Đang đăng ký...";
    button.disabled = true;

    fetch("/student/topic/regist_topic/", {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
        },
        body: JSON.stringify({ 'topicId': topicId, 'action': action }),
    })
        .then(response => response.json())
        .then(data => {
            if (data.status === "success") {
                button.innerHTML = "✅ Đã đăng ký";
                button.classList.remove("btn-primary");
                button.classList.add("btn-success");
            } else {
                button.innerHTML = "❌ Thử lại";
                button.disabled = false;
                button.classList.remove("btn-primary");
                button.classList.add("btn-danger");
            }
            showToast(data.message, data.status);
        })
        .catch(error => {
            console.error("Error:", error);
            button.innerHTML = "❌ Thử lại";
            button.disabled = false;
            button.classList.remove("btn-primary");
            button.classList.add("btn-danger");
            showToast("Có lỗi xảy ra khi đăng ký!", "error");
        });
}

// Gắn event listener
document.addEventListener("DOMContentLoaded", function () {
    const registerBtn = document.querySelector(".btn-register");

    if (registerBtn) {
        registerBtn.addEventListener("click", function () {
            const topicId = this.getAttribute("data-topicid");
            const action = this.getAttribute("data-action");
            registerTopic(topicId, action, this);
        });
    }
});