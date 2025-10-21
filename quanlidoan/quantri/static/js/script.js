function showToast(message) {
    const toastEl = document.getElementById('liveToast');
    const toastBody = document.getElementById('toast-message');
    toastBody.textContent = message;

    const toast = new bootstrap.Toast(toastEl);
    toast.show();
}
