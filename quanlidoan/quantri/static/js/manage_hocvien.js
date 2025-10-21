document.addEventListener('DOMContentLoaded', function () {

  // URL (đổi theo urls.py của bạn; nếu có namespace, dùng 'hocvien:create' ...)
  const URL_CREATE = "/quantri/hocvien/create/";
  const URL_UPDATE_TEMPLATE = "/quantri/hocvien/update/";
  const URL_DELETE_TEMPLATE = "/quantri/hocvien/delete/";

  // Toast
  const toastEl = document.getElementById('toast');
  const toast = toastEl ? new bootstrap.Toast(toastEl, { delay: 2400 }) : null;
  const notify = (msg) => { if (!toast) return; toastEl.querySelector('.toast-body').textContent = msg; toast.show(); };

  // Modal Thêm/Sửa
  const studentModal = document.getElementById('studentModal');
  const studentForm = document.getElementById('studentForm');

  studentModal.addEventListener('show.bs.modal', function (e) {
    const btn = e.relatedTarget;
    const mode = btn?.dataset?.mode || 'edit';
    studentModal.querySelector('.modal-title').textContent = (mode === 'create') ? 'Thêm học viên' : 'Sửa học viên';

    if (mode === 'create') {
      studentForm.reset();
      document.getElementById('f_mahv').value = '';
      return;
    }

    document.getElementById('f_mahv').value = btn.dataset.mahv || '';
    document.getElementById('f_hoten').value = btn.dataset.hoten || '';
    document.getElementById('f_email').value = btn.dataset.email || '';
    document.getElementById('f_sodienthoai').value = btn.dataset.sodienthoai || '';
    document.getElementById('f_lop').value = btn.dataset.lop || '';
    document.getElementById('f_username').value = btn.dataset.username || '';
    document.getElementById('f_userid').value = btn.dataset.userid || '';
  });

  // Submit (AJAX)
  studentForm.addEventListener('submit', function (e) {
    e.preventDefault();
    const isCreate = studentModal.querySelector('.modal-title').textContent.includes('Thêm');
    const formData = new FormData(studentForm);
    const mahv = document.getElementById('f_mahv').value;
    const url = isCreate ? URL_CREATE : URL_UPDATE_TEMPLATE;

    fetch(url, { method: 'POST', body: formData, headers: { 'X-CSRFToken': csrftoken } })
      .then(r => r.json())
      .then(d => {
        if (d.status === 'success') {
          alert(d.message)
          setTimeout(() => window.location.reload(), 600);
        } else alert(d.message)
      })
      .catch(() => notify('Lỗi kết nối'));
  });

  // Modal Xóa
  const deleteModal = document.getElementById('confirmDeleteStudentModal');
  var delMahv = null;

  deleteModal.addEventListener('show.bs.modal', function (e) {
    const btn = e.relatedTarget;
    delMahv = btn.dataset.mahv;
    document.getElementById('del_student_id').textContent = delMahv || '';
    document.getElementById('del_student_name').textContent = btn.dataset.hoten || '';
  });

  document.getElementById('btnConfirmDeleteStudent').addEventListener('click', function () {
    fetch(URL_DELETE_TEMPLATE, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCookie('csrftoken'),
      },
      body: JSON.stringify({ 'mahv': delMahv }),
    })
      .then(response => response.json())
      .then(data => {
        if (data.status === "success") {
          alert(data.message)
          setTimeout(() => window.location.reload(), 600);
        } else {
          alert(data.message)
        }
      })
      .catch(error => {
        alert(error)
      });
  })
}
)