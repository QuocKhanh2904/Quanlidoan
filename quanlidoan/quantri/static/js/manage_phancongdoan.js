document.addEventListener('DOMContentLoaded', () => {
  // --- Lấy các thành phần giao diện ---
  const assignModal = document.getElementById('modalAssignGV');
  const rejectModal = document.getElementById('modalReject');
  const toastEl = document.getElementById('toast');
  const toastBody = toastEl.querySelector('.toast-body');
  const toast = new bootstrap.Toast(toastEl);

  // --------------------------------------------------
  // 🟦 Hiển thị modal "Phân công giảng viên"
  // --------------------------------------------------
  assignModal.addEventListener('show.bs.modal', event => {
  const button = event.relatedTarget;
  const mada = button.getAttribute('data-mada');
  const tenda = button.getAttribute('data-tenda');
  const magv = button.getAttribute('data-magv');

  // Gán dữ liệu vào form
  document.getElementById('assign_mada_hidden').value = mada;   // input hidden (để gửi form)
  document.getElementById('assign_mada_text').textContent = mada; // span hiển thị mã đồ án
  document.getElementById('assign_tenda').textContent = tenda;

  // Reset lựa chọn giảng viên
  const select = document.getElementById('assign_magv');
  select.value = magv || '';
});


  // --------------------------------------------------
  // 🟥 Hiển thị modal "Từ chối đăng ký"
  // --------------------------------------------------
  rejectModal.addEventListener('show.bs.modal', event => {
    const button = event.relatedTarget;
    const mada = button.getAttribute('data-mada');
    const tenda = button.getAttribute('data-tenda');

    document.getElementById('reject_mada').value = mada;
    document.getElementById('reject_tenda').textContent = tenda;
    document.getElementById('reject_id').textContent = mada;
  });
  
  // --------------------------------------------------
  // 🟩 Gửi yêu cầu PHÂN CÔNG GIẢNG VIÊN
  // --------------------------------------------------
  const assignForm = document.getElementById('assignGVForm');
  assignForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const url = "/quantri/phancongdoan/update/";
    const formData = new FormData(assignForm);

    try {
      const response = await fetch(url, {
        method: 'POST',
        body: formData,
        headers: { 'X-CSRFToken': getCookie('csrftoken') },
      });
      const data = await response.json();

      showToast(data.message, data.status);
      if (data.status === 'success') {
        setTimeout(() => window.location.reload(), 1000);
      }
    } catch (err) {
      showToast('Lỗi kết nối đến máy chủ!', 'error');
    }
  });

  // --------------------------------------------------
  // 🟧 Gửi yêu cầu TỪ CHỐI ĐĂNG KÝ
  // --------------------------------------------------
  const rejectForm = document.getElementById('rejectForm');
  rejectForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const url = "/quantri/phancongdoan/reject/";
    const formData = new FormData(rejectForm);

    try {
      const response = await fetch(url, {
        method: 'POST',
        body: formData,
        headers: { 'X-CSRFToken': getCookie('csrftoken') },
      });
      const data = await response.json();

      showToast(data.message, data.status);
      if (data.status === 'success') {
        notify(d.message || 'Đã hủy yêu cầu');
        setTimeout(() => window.location.reload(), 1000);
      }
    } catch (err) {
      showToast('Không thể gửi yêu cầu. Vui lòng thử lại!', 'error');
    }
  });

  // --------------------------------------------------
  // ⚙️ Hàm tiện ích: Hiển thị thông báo (Toast)
  // --------------------------------------------------
  function showToast(message, type = 'success') {
    toastBody.textContent = message;
    const toastDiv = toastEl.querySelector('.toast');
    toastEl.classList.remove('bg-success', 'bg-danger', 'text-white');

    if (type === 'success') {
      toastEl.classList.add('bg-success', 'text-white');
    } else {
      toastEl.classList.add('bg-danger', 'text-white');
    }

    toast.show();
  }

  // --------------------------------------------------
  // ⚙️ Hàm tiện ích: Lấy CSRF Token từ cookie
  // --------------------------------------------------
  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === name + '=') {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }
});
