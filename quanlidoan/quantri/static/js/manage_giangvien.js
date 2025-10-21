document.addEventListener('DOMContentLoaded', function () {
  // --- Modal Thêm/Sửa ---
  const teacherModal = document.getElementById('teacherModal');
  const teacherForm = document.getElementById('teacherForm');

  teacherModal.addEventListener('show.bs.modal', function (e) {
    const btn = e.relatedTarget;
    const mode = btn?.dataset?.mode || 'edit';
    teacherModal.querySelector('.modal-title').textContent = (mode === 'create') ? 'Thêm giảng viên' : 'Sửa giảng viên';

    if (mode === 'create') {
      teacherForm.reset();
      document.getElementById('f_magv').value = '';
      return;
    }

    document.getElementById('f_magv').value = btn.dataset.magv || '';
    document.getElementById('f_hoten').value = btn.dataset.hoten || '';
    document.getElementById('f_email').value = btn.dataset.email || '';
    document.getElementById('f_sodienthoai').value = btn.dataset.sodienthoai || '';
    document.getElementById('f_donvi').value = btn.dataset.donvi || '';
    document.getElementById('f_username').value = btn.dataset.username || '';
    document.getElementById('f_userid').value = btn.dataset.userid || '';
  });

  teacherForm.addEventListener('submit', function (e) {
    e.preventDefault();
    const isCreate = teacherModal.querySelector('.modal-title').textContent.includes('Thêm');
    const formData = new FormData(teacherForm);
    const url = isCreate ? '/quantri/giangvien/create/' : '/quantri/giangvien/update/';

    fetch(url, { method: 'POST', body: formData, headers: { 'X-CSRFToken': csrftoken } })
      .then(r => r.json())
      .then(d => {
        if (d.status === 'success') {
          setTimeout(() => window.location.reload(), 600);
          alert(d.message || 'Thành công');
        } else alert(d.message || 'Thất bại');
      })
      .catch(() => alert('Lỗi kết nối'));
  });

  // --- Modal Xóa ---
  const deleteModal = document.getElementById('confirmDeleteTeacherModal');
  let magv = null;

  // Khi mở modal => lấy thông tin giảng viên
  deleteModal.addEventListener('show.bs.modal', function (e) {
    const btn = e.relatedTarget;
    magv = btn.dataset.magv;
    document.getElementById('del_teacher_id').textContent = magv || '';
    document.getElementById('del_teacher_name').textContent = btn.dataset.hoten || '';
  })

  document.getElementById('btnConfirmDeleteTeacher').addEventListener('click', function () {
    const url = '/quantri/giangvien/delete/';

    fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',   // 🔥 quan trọng
        'X-CSRFToken': csrftoken
      },
      body: JSON.stringify({ 'magv': magv })
    })
      .then(response => {
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        return response.json();               // chuyển sang JSON
      })
      .then(data => {
        alert(data.message || 'Đã xóa');
        if (data.status === 'success') {
          setTimeout(() => window.location.reload(), 600);
        }
      })
      .catch(error => {
        console.error('Lỗi:', error);
        alert('Lỗi kết nối hoặc phản hồi không hợp lệ.');
      });
  });
});
