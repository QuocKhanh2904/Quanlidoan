// Chỉ submit khi nhấn Enter hoặc bấm nút submit.
// Không auto-submit khi đang gõ.
function initSearchOnSubmitOnly({
  formId = 'searchForm',
  inputId = 'searchInput',
  statusId = 'status-filter',   // nếu muốn đổi trạng thái tự submit
  autoSubmitStatus = true       // đặt false nếu KHÔNG muốn auto khi đổi trạng thái
} = {}) {
  const form   = document.getElementById(formId);
  if (!form) return;

  const q      = document.getElementById(inputId);
  const status = document.getElementById(statusId);

  // Nhấn Enter trong ô tìm kiếm -> submit
  if (q) {
    q.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') {
        // để chắc chắn submit thay vì refresh khác
        if (typeof form.requestSubmit === 'function') {
          e.preventDefault();
          form.requestSubmit();
        } else {
          form.submit();
        }
      }
    });
  }

  // Đổi trạng thái -> submit ngay (tuỳ chọn)
  if (autoSubmitStatus && status) {
    status.addEventListener('change', () => {
      if (typeof form.requestSubmit === 'function') form.requestSubmit();
      else form.submit();
    });
  }
}

// Cho phép gọi từ HTML
window.initSearchOnSubmitOnly = initSearchOnSubmitOnly;
