function openModal(id, name, field, startDate, endDate, desc) {
    document.getElementById('modal-id').innerText = id;
    document.getElementById('modal-name').innerText = name;
    document.getElementById('modal-field').innerText = field;
    document.getElementById('modal-start-date').innerText = formatDate(startDate);
    document.getElementById('modal-end-date').innerText = formatDate(endDate);
    document.getElementById('modal-desc').innerText = desc;

    var modal = new bootstrap.Modal(document.getElementById('topicModal'));
    modal.show();
}

function formatDate(dateString) {
    if (!dateString) return '';
    const date = new Date(dateString);
    const day = String(date.getDate()).padStart(2, '0');     // lấy ngày
    const month = String(date.getMonth() + 1).padStart(2, '0'); // tháng +1 (JS bắt đầu từ 0)
    const year = date.getFullYear();
    return `${day}/${month}/${year}`;
}


