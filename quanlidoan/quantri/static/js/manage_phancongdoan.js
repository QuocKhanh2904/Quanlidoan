document.addEventListener('DOMContentLoaded', () => {
  // --- Lấy các thành phần giao diện ---
  const assignModal = document.getElementById('modalAssignGV');
  const assignForm = document.getElementById('assignGVForm');
  const selectHD = document.getElementById('assign_mahd');
  const selectGV = document.getElementById('assign_magv');

  // Khi mở modal
  assignModal.addEventListener('show.bs.modal', event => {
    const button = event.relatedTarget;
    const mada = button.getAttribute('data-mada');
    const tenda = button.getAttribute('data-tenda');
    const mahd = button.getAttribute('data-mahd');
    const magv = button.getAttribute('data-magv');

    document.getElementById('assign_mada_hidden').value = mada;
    document.getElementById('assign_mada_text').textContent = mada || '(Không có)';
    document.getElementById('assign_tenda').textContent = tenda || '(Không có)';

    const selectHD = document.getElementById('assign_mahd');
    const selectGV = document.getElementById('assign_magv');

    if (mahd) {
      // Đã có hội đồng -> khóa lại
      selectHD.value = mahd;
      selectHD.disabled = true;
      // tải giảng viên thuộc hội đồng đó
      fetch(`/quantri/hoidong/giangvien/?mahd=${mahd}`)
        .then(r => r.json())
        .then(d => {
          if (d.status === 'success') {
            selectGV.innerHTML = '<option value="">-- Chọn giảng viên --</option>';
            d.data.forEach(gv => {
              const opt = document.createElement('option');
              opt.value = gv.magv;
              opt.textContent = gv.hoten;
              selectGV.appendChild(opt);
            });
            if (magv) selectGV.value = magv;
          }
        });
    } else {
      // Chưa có hội đồng -> cho phép chọn
      selectHD.value = '';
      selectHD.disabled = false;
      selectGV.innerHTML = '<option value="">-- Chọn giảng viên --</option>';
    }
  });

  // 🟦 Khi chọn hội đồng → lấy danh sách giảng viên trong hội đồng
  selectHD.addEventListener('change', async () => {
    const mahd = selectHD.value;
    if (!mahd) {
      selectGV.innerHTML = '<option value="">-- Chọn giảng viên --</option>';
      return;
    }
    try {
      const res = await fetch(`/quantri/hoidong/giangvien/?mahd=${mahd}`);
      const data = await res.json();
      if (data.status === 'success') {
        selectGV.innerHTML = '<option value="">-- Chọn giảng viên --</option>';
        data.data.forEach(gv => {
          const opt = document.createElement('option');
          opt.value = gv.magv;
          opt.textContent = gv.hoten;
          selectGV.appendChild(opt);
        });
      } else {
        selectGV.innerHTML = '<option value="">Không có giảng viên</option>';
      }
    } catch {
      selectGV.innerHTML = '<option value="">Lỗi tải giảng viên</option>';
    }
  });

  // 🟩 Gửi form phân công
  assignForm.addEventListener('submit', async e => {
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
      if (data.status === 'success') {
        setTimeout(() => window.location.reload(), 600);
      } else alert(data.message)

    } catch {
      showToast('Lỗi kết nối đến máy chủ!', 'error');
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
