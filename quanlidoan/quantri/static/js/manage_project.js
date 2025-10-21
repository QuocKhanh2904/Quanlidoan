document.addEventListener('DOMContentLoaded', function () {

  // thêm
  const form = document.getElementById('createProjectForm');
  const modalEl = document.getElementById('modalCreateProject');
  if (!form || !modalEl) return;
  form.addEventListener('submit', function (e) {
    e.preventDefault();
    const url = form.dataset.url;
    if (!url) {
      console.log("Không tìm thấy URL gửi yêu cầu");
      return;
    }

    const formData = new FormData(form);
    fetch(url, {
      method: 'POST',
      body: formData,
      headers: {
        'X-CSRFToken': getCookie('csrftoken')
      }
    })
      .then(response => response.json())
      .then(data => {
        if (data.status === 'success') {
          const modal = bootstrap.Modal.getInstance(modalEl);
          modal.hide();
          alert(data.message);
          window.location.reload();
        } else {
          alert(data.message);
        }
      })
      .catch(error => {
        console.error(error);
        alert('Không thể gửi dữ liệu. Vui lòng thử lại.');
      })
  })

  // sửa
  const editModalEl = document.getElementById('modalEditProject');
  const editForm = document.getElementById('editProjectForm');
  if (!editModalEl || !editForm) return;
  showModalEditProject(editModalEl);
  editForm.addEventListener('submit', function (e) {
    e.preventDefault();
    const url = editForm.dataset.url;
    const formData = new FormData(editForm);
    fetch(url, {
      method: 'POST',
      body: formData,
      headers: {
        'X-CSRFToken': getCookie('csrftoken')
      }
    })
      .then(response => response.json())
      .then(data => {
        if (data.status === 'success') {
          const modalInstance = bootstrap.Modal.getInstance(editModalEl);
          modalInstance?.hide();
          alert(data.message || 'Cập nhật thành công!');
          window.location.reload();
        } else {
          alert(data.message || 'Cập nhật thất bại.');
        }
      })
      .catch(error => {
        console.error('Lỗi khi gửi dữ liệu:', error);
        alert('Không thể cập nhật dữ liệu. Vui lòng thử lại.');
      });
  });

  // Xóa
  const deleteModalEl = document.getElementById('modalDeleteProject');
  const deleteForm = document.getElementById('deleteProjectForm');
  if (!deleteModalEl || !deleteForm) return;
  showModalDeleteProject(deleteModalEl);
  deleteForm.addEventListener('submit', function (e) {
    e.preventDefault();
    const url = deleteForm.dataset.url;
    const formData = new FormData(deleteForm)
    fetch(url, {
      method: 'POST',
      body: formData,
      headers: {
        'X-CSRFToken': getCookie('csrftoken'),
      }
    })
      .then(response => response.json())
      .then(data => {
        if (data.status === 'success') {
          const modalInstance = bootstrap.Modal.getInstance(deleteModalEl);
          modalInstance?.hide();
          alert(data.message || 'Xóa thành công!');
          window.location.reload();
        } else {
          alert(data.message || 'Xóa thất bại.');
        }
      })
      .catch(error => {
        console.error('Lỗi khi gửi dữ liệu:', error);
        alert('Không thể xóa dữ liệu. Vui lòng thử lại.');
      });
  });
})

function showModalEditProject(editModalEl) {
  editModalEl.addEventListener('show.bs.modal', function (event) {
    const button = event.relatedTarget; // nút đã nhấn

    document.getElementById('edit_mada').value = button.dataset.mada || '';
    document.getElementById('edit_tenda').value = button.dataset.tenda || '';
    document.getElementById('edit_trangthai').value = button.dataset.trangthai || '0';
    document.getElementById('edit_soluongtoida').value = button.dataset.soluongtoida || '';
    document.getElementById('edit_ngaybd').value = button.dataset.ngaybd || '';
    document.getElementById('edit_ngaykt').value = button.dataset.ngaykt || '';
    document.getElementById('edit_linhvuc').value = button.dataset.linhvuc || '';
    document.getElementById('edit_mota').value = button.dataset.mota || '';
    document.getElementById('edit_mahd').value = button.dataset.mahd || '';

    const fileLink = document.getElementById('current_file_link');
    const noFileText = document.getElementById('no_file_text');
    const removeFileCheckbox = document.getElementById('remove_file');

    const fileUrl = button.dataset.file || '';
    if (fileUrl) {
      fileLink.href = fileUrl;
      fileLink.style.display = 'inline-block';
      noFileText.style.display = 'none';
    } else {
      fileLink.href = '#';
      fileLink.style.display = 'none';
      noFileText.style.display = 'inline';
    }

    removeFileCheckbox.checked = false;
  });
}

function showModalDeleteProject(deleteModalEl) {
  deleteModalEl.addEventListener('show.bs.modal', function (event) {
    const button = event.relatedTarget; // nút đã nhấn
    document.getElementById('delete_id').textContent = button.dataset.mada || '';
    document.getElementById('delete_name').textContent = button.dataset.tenda || '';
    document.getElementById('delete_mada').value = button.dataset.mada || '';
    document.getElementById('delete_file').value = button.dataset.file || '';
  });
}
