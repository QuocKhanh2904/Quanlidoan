document.addEventListener("DOMContentLoaded", () => {
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    // Thêm tiến độ
    const form = document.getElementById("addTiendoForm");
    if (form) {
        form.addEventListener("submit", async (e) => {
            e.preventDefault();
            const formData = new FormData(form);
            try {
                const res = await fetch("/quantri/tiendo/create/", {
                    method: "POST",
                    body: formData,
                    headers: { "X-CSRFToken": csrftoken },
                });
                const data = await res.json();
                alert(data.message);
                if (data.status === "success") location.reload();
            } catch (err) {
                console.error(err);
                alert("Lỗi kết nối máy chủ!");
            }
        });
    }

    // Xóa tiến độ
    document.querySelectorAll("#btnDeleteTiendo").forEach((btn) => {
        btn.addEventListener("click", async () => {
            if (!confirm("Bạn có chắc muốn xóa tiến độ này?")) return;
            const id = btn.dataset.id;
            const res = await fetch("/quantri/tiendo/delete/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": csrftoken,
                },
                body: JSON.stringify({ matd: id }),
            });
            const data = await res.json();
            alert(data.message);
            if (data.status === "success") location.reload();
        });
    });

    // Xem chi tiết tiến độ
    // === XEM CHI TIẾT TIẾN ĐỘ ===
    const viewModal = document.getElementById("viewTiendoModal");
    if (viewModal) {
        viewModal.addEventListener("show.bs.modal", async (event) => {
            const id = event.relatedTarget.dataset.id;
            const content = document.getElementById("tiendoDetailContent");
            content.innerHTML = "<p>Đang tải...</p>";
            try {
                const res = await fetch(`/quantri/tiendo/detail/${id}/`);
                const data = await res.json();

                if (data.status === "success") {
                    const t = data.data;
                    content.innerHTML = `
          <div>
            <p><strong>Đồ án:</strong> ${t.mada__tenda}</p>
            <p><strong>Mô tả công việc:</strong><br>${t.motacongviec}</p>
            <p><strong>Tiến độ:</strong> ${t.tiendophantram}%</p>
            <p><strong>Người kiểm tra:</strong> ${t.nguoikiemtra}</p>
            <p><strong>Ngày cập nhật:</strong> ${t.ngaycapnhat}</p>
            ${t.file
                            ? `<p><strong>File:</strong> <a href="/media/${t.file}" target="_blank">Tải xuống</a></p>`
                            : `<p><strong>File:</strong> Không có</p>`
                        }
          </div>`;
                } else {
                    content.innerHTML = `<p class="text-danger">${data.message}</p>`;
                }
            } catch {
                content.innerHTML = "<p class='text-danger'>Lỗi tải dữ liệu.</p>";
            }
        });
    }

    // === SỬA TIẾN ĐỘ ===
    const editModal = document.getElementById("editTiendoModal");
    if (editModal) {
        editModal.addEventListener("show.bs.modal", async (event) => {
            const id = event.relatedTarget.dataset.id;
            try {
                const res = await fetch(`/quantri/tiendo/detail/${id}/`);
                const data = await res.json();
                if (data.status === "success") {
                    const t = data.data;
                    document.getElementById("edit_matd").value = t.matd;
                    document.getElementById("edit_motacv").value = t.motacongviec;
                    document.getElementById("edit_tiendo").value = t.tiendophantram;
                    document.getElementById("edit_nguoikiemtra").value = t.nguoikiemtra;
                    document.getElementById("currentFileContainer").innerHTML = t.file
                        ? `<p>File hiện tại: <a href="${t.file}" target="_blank">${t.file.split('/').pop()}</a></p>`
                        : "<p>Không có file đính kèm</p>";
                }
            } catch {
                alert("Lỗi tải dữ liệu!");
            }
        });

        // Gửi yêu cầu cập nhật
        const editForm = document.getElementById("editTiendoForm");
        if (editForm) {
            editForm.addEventListener("submit", async (e) => {
                e.preventDefault();
                const formData = new FormData(editForm);
                try {
                    const res = await fetch("/quantri/tiendo/update/", {
                        method: "POST",
                        body: formData,
                        headers: { "X-CSRFToken": csrftoken },
                    });
                    const data = await res.json();
                    if (data.status === "success") location.reload();
                    else alert(data.message);
                } catch (err) {
                    console.error(err);
                    alert("Lỗi kết nối máy chủ!");
                }
            });
        }
    }

    const form1 = document.getElementById("filterForm");
    const selects = form1.querySelectorAll("select");

    // Tự động submit khi thay đổi năm hoặc đồ án
    selects.forEach(select => {
        select.addEventListener("change", function () {
            form1.submit();
        });
    });
});