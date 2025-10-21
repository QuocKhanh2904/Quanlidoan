document.getElementById('changePasswordForm').addEventListener('submit', function (event) {
    event.preventDefault();
    var currentPassword = document.getElementById('currentPassword').value;
    var newPassword = document.getElementById('newPassword').value;
    var confirmNewPassword = document.getElementById('confirmNewPassword').value;
    data = {
        'current_password': currentPassword,
        'new_password': newPassword,
        'confirm_new_password': confirmNewPassword
    }
    fetch("/student/change_password/", {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
        },
        body: JSON.stringify(data)
    })
        .then(response => response.json())
        .then(data => {
            showAlert(data.message, data.status);
            if (data.status === 'success') {
                document.getElementById('changePasswordForm').reset();
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Đã xảy ra lỗi khi thay đổi mật khẩu.');
        })
})

function showAlert(message, type = "success") {
    const alertBox = document.getElementById("alertBox");
    alertBox.textContent = message;
    alertBox.className = `alert alert-${type} text-center`;
    alertBox.style.display = "block";
    setTimeout(() => {
        alertBox.style.display = "none";
    }, 5000);
}
