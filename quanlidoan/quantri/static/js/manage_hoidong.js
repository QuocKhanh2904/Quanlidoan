document.addEventListener('DOMContentLoaded', function () {
  // CSRF
  function getCookie(name) {
    const v = `; ${document.cookie}`.split(`; ${name}=`);
    if (v.length === 2) return decodeURIComponent(v.pop().split(';').shift());
  }
  const csrftoken = getCookie('csrftoken');

  // URL (đổi theo urls.py của bạn; nếu có namespace thì thêm 'hoidong:' ...)
  const URL_CREATE = "/quantri/hoidong/create/";
  const URL_UPDATE_TEMPLATE = "/quantri/hoidong/update/";
  const URL_DELETE_TEMPLATE = "/quantri/hoidong/delete/";
  const URL_MEMBERS_LIST_TEMPLATE = "/quantri/thanhvienhoidong/list/";
  const URL_MEMBERS_ADD_TEMPLATE = "/quantri/thanhvienhoidong/addmember/";
  const URL_MEMBERS_DEL_TEMPLATE = "/quantri/thanhvienhoidong/delete/";

  // Toast
  const toastEl = document.getElementById('toast');
  const toast = toastEl ? new bootstrap.Toast(toastEl, { delay: 2400 }) : null;
  const notify = (msg) => { if (!toast) return; toastEl.querySelector('.toast-body').textContent = msg; toast.show(); };

  // Modal Thêm/Sửa
  const committeeModal = document.getElementById('committeeModal');
  const committeeForm = document.getElementById('committeeForm');
  const memberSection = document.getElementById('memberSection');
  const memberTableBody = document.querySelector('#memberTable tbody');

  function renderMembers(rows) {
    memberTableBody.innerHTML = '';
    if (!rows || !rows.length) {
      memberTableBody.innerHTML = '<tr><td colspan="4" class="text-center text-muted">Chưa có thành viên</td></tr>';
      return;
    }
    rows.forEach(r => {
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td>${r.matv}</td>
        <td>${r.hoten || '-'}</td>
        <td>${r.vaitro || '-'}</td>
        <td class="text-end">
          <button type="button" class="btn btn-sm btn-outline-danger btn-del-member" data-matv="${r.matv}">Xóa</button>
        </td>
      `;
      memberTableBody.appendChild(tr);
    });
  }

  async function loadMembers(mahd) {
    try {
      // 👇 Gửi mã hội đồng qua query string
      const url = `/quantri/thanhvienhoidong/list/?mahd=${encodeURIComponent(mahd)}`;

      const response = await fetch(url, {
        method: 'GET',
        headers: { 'X-CSRFToken': csrftoken },
      });

      // Kiểm tra phản hồi HTTP
      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }

      const data = await response.json();

      if (data.status === 'success') {
        renderMembers(data.data || []);
      } else {
        console.warn('Server trả về lỗi:', data.message);
        renderMembers([]);
      }
    } catch (err) {
      console.error('Lỗi tải danh sách thành viên:', err);
      renderMembers([]);
    }
  }

  committeeModal.addEventListener('show.bs.modal', function (e) {
    const btn = e.relatedTarget;
    const mode = btn?.dataset?.mode || 'edit';
    committeeModal.querySelector('.modal-title').textContent = (mode === 'create') ? 'Thêm hội đồng' : 'Sửa hội đồng / Thành viên';

    // Reset form
    committeeForm.reset();
    document.getElementById('f_mahd').value = '';

    if (mode === 'create') {
      memberSection.style.display = 'none';
      return;
    }

    // Điền dữ liệu form
    document.getElementById('f_mahd').value = btn.dataset.mahd || '';
    document.getElementById('f_tenhd').value = btn.dataset.tenhd || '';
    document.getElementById('f_linhvuc').value = btn.dataset.linhvuc || '';
    document.getElementById('f_ngaythanhlap').value = btn.dataset.ngaythanhlap || '';
    document.getElementById('f_ngayketthuc').value = btn.dataset.ngayketthuc || '';

    // Hiện khu thành viên + nạp danh sách
    memberSection.style.display = '';
    loadMembers(btn.dataset.mahd);
  });

  // Submit create/update hội đồng
  committeeForm.addEventListener('submit', function (e) {
    e.preventDefault();
    const isCreate = committeeModal.querySelector('.modal-title').textContent.includes('Thêm');
    const formData = new FormData(committeeForm);
    const mahd = document.getElementById('f_mahd').value;
    const url = isCreate ? URL_CREATE : URL_UPDATE_TEMPLATE;

    fetch(url, { method: 'POST', body: formData, headers: { 'X-CSRFToken': csrftoken } })
      .then(r => r.json())
      .then(d => {
        if (d.status === 'success') {
          alert(d.message)
          setTimeout(() => window.location.reload(), 600);
        } else console.log(d.message)
      })
      .catch(() => notify('Lỗi kết nối'));
  });

  // Thêm thành viên
  document.getElementById('btnAddMember').addEventListener('click', function () {
    const mahd = document.getElementById('f_mahd').value;
    if (!mahd) return;

    const magv = document.getElementById('f_magv').value;
    const vaitro = document.getElementById('f_vaitro').value.trim();
    if (!magv) { notify('Chọn giảng viên'); return; }

    const url = URL_MEMBERS_ADD_TEMPLATE;
    const fd = new FormData();
    fd.append('magv', magv);
    fd.append('vaitro', vaitro);
    fd.append('mahd', mahd);

    fetch(url, { method: 'POST', body: fd, headers: { 'X-CSRFToken': csrftoken } })
      .then(r => r.json())
      .then(d => {
        notify(d.message || 'Đã thêm thành viên');
        if (d.status === 'success') loadMembers(mahd);
      })
      .catch(() => notify('Lỗi kết nối'));
  });

  // Xóa thành viên (ủy quyền click)
  document.querySelector('#memberTable').addEventListener('click', function (e) {
    const btn = e.target.closest('.btn-del-member');
    if (!btn) return;
    const matv = btn.dataset.matv;
    const mahd = document.getElementById('f_mahd').value;
    if (!matv || !mahd) return;

    const url = URL_MEMBERS_DEL_TEMPLATE;
    fetch(url, {
      method: 'POST', headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCookie('csrftoken'),
      },
      body: JSON.stringify({ 'matv': matv }),
    })
      .then(response => response.json())
      .then(data => {
        if (data.status === 'success') {
          notify(data.message);
          loadMembers(mahd);
        }
        else {
          alert(data.message)
        }
      })
      .catch(error => {
        alert(error)
      });
  });

  // Modal Xóa hội đồng
  const deleteModal = document.getElementById('confirmDeleteCommitteeModal');
  let delMaHD = null;

  deleteModal.addEventListener('show.bs.modal', function (e) {
    const btn = e.relatedTarget;
    delMaHD = btn.dataset.mahd;
    document.getElementById('del_hd_id').textContent = delMaHD || '';
    document.getElementById('del_hd_name').textContent = btn.dataset.tenhd || '';
  });

  document.getElementById('btnConfirmDeleteCommittee').addEventListener('click', function () {
    const url = URL_DELETE_TEMPLATE;
    fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCookie('csrftoken'),
      },
      body: JSON.stringify({ 'mahd': delMaHD })
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
  });
});