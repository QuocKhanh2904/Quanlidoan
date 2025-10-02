document.addEventListener("DOMContentLoaded", function () {
    const fileInput = document.getElementById("filebaocao");
    const filePreview = document.getElementById("filePreview");

    if (fileInput) {
        fileInput.addEventListener("change", function () {
            if (fileInput.files.length > 0) {
                filePreview.textContent = "📎 File đã chọn: " + fileInput.files[0].name;
            } else {
                filePreview.textContent = "";
            }
        });
    }
});

var button = document.getElementById("submitReport");

button.addEventListener("click", function () {
    var motacongviec = document.getElementById("motacongviec").value.trim();
    var filebaocao = document.getElementById("filebaocao").files[0];
    if (!motacongviec || !filebaocao) {
        alert("Vui lòng điền đầy đủ thông tin.");
        return;
    }
    const formData = new FormData();
    formData.append("motacongviec", motacongviec);
    formData.append("filebaocao", filebaocao);

    fetch('/submit_report/', {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
        }
    })
        .then(response => response.json())
        .then(data => {
            if (data.status === "success") {
                console.log(data.message);
                showToast(data.message);
                // Thực hiện các hành động khác nếu cần, ví dụ: reset form
                document.getElementById("motacongviec").value = "";
                document.getElementById("filebaocao").value = "";
                document.getElementById("filePreview").textContent = "";
            } else {
                console.log(data.message);
                showToast(data.message);
            }
        })
        .catch(error => {
            console.error("Error:", error);
        })
});

