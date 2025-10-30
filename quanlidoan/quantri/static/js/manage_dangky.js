document.addEventListener("DOMContentLoaded", () => {
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    const lopSelect = document.getElementById("selectLop");
    const hvSelect = document.getElementById("selectHocVien");

    if (lopSelect) {
        lopSelect.addEventListener("change", async () => {
            const lop = lopSelect.value;
            hvSelect.innerHTML = '<option value="">-- Chọn học viên --</option>';

            if (!lop) return;

            try {
                const res = await fetch(`/quantri/hocvien/by_lop/?lop=${encodeURIComponent(lop)}`);
                const data = await res.json();

                if (data.status === "success") {
                    data.data.forEach((hv) => {
                        const opt = document.createElement("option");
                        opt.value = hv.mahv;
                        opt.textContent = hv.hoten;
                        hvSelect.appendChild(opt);
                    });
                } else {
                    alert(data.message || "Không tìm thấy học viên trong lớp này");
                }
            } catch (err) {
                alert("Lỗi tải danh sách học viên");
                console.error(err);
            }
        });
    }
    // === THÊM ĐĂNG KÝ ===
    const addForm = document.getElementById("addDangKyForm");
    if (addForm) {
        addForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const formData = new FormData(addForm);
            try {
                const res = await fetch("/quantri/dangky/create/", {
                    method: "POST",
                    body: formData,
                    headers: { "X-CSRFToken": csrftoken },
                });
                const data = await res.json();
                if (data.status === "success") location.reload();
                else alert(data.message);
            } catch {
                alert("Lỗi kết nối!");
            }
        });
    }

    // === XEM CHI TIẾT ===
    const viewModal = document.getElementById("viewDangKyModal");
    if (viewModal) {
        viewModal.addEventListener("show.bs.modal", async (event) => {
            const id = event.relatedTarget.dataset.id;
            const content = document.getElementById("dangkyDetailContent");
            content.innerHTML = "<p>Đang tải...</p>";
            try {
                const res = await fetch(`/quantri/dangky/detail/${id}/`);
                const data = await res.json();
                if (data.status === "success") {
                    const d = data.data;
                    content.innerHTML = `
            <p><strong>Mã đăng ký:</strong> ${d.madk}</p>
            <p><strong>Học viên:</strong> ${d.mahv__hoten}</p>
            <p><strong>Đồ án:</strong> ${d.mada__tenda}</p>
            <p><strong>Ngày đăng ký:</strong> ${d.ngaydk}</p>
          `;
                } else content.innerHTML = `<p class="text-danger">${data.message}</p>`;
            } catch {
                content.innerHTML = "<p class='text-danger'>Lỗi tải dữ liệu.</p>";
            }
        });
    }

    // === XÓA ĐĂNG KÝ ===
    document.querySelectorAll("#btnDeleteDangKy").forEach((btn) => {
        btn.addEventListener("click", async () => {
            if (!confirm("Bạn có chắc muốn xóa đăng ký này?")) return;
            const id = btn.dataset.id;
            const res = await fetch("/quantri/dangky/delete/", {
                method: "POST",
                headers: { "Content-Type": "application/json", "X-CSRFToken": csrftoken },
                body: JSON.stringify({ madk: id }),
            });
            const data = await res.json();
            if (data.status === "success") location.reload();
            else alert(data.message);
        });
    });

    // === SỬA ĐĂNG KÝ ===
    const editModal = document.getElementById("editDangKyModal");
    if (editModal) {
        // Khi mở modal sửa
        editModal.addEventListener("show.bs.modal", async (event) => {
            const id = event.relatedTarget.dataset.id;

            try {
                const res = await fetch(`/quantri/dangky/detail/${id}/`);
                const data = await res.json();

                if (data.status === "success") {
                    const d = data.data;
                    document.getElementById("edit_madk").value = d.madk;
                    document.getElementById("edit_tenhv").value = d.mahv__hoten;
                    document.getElementById("edit_mada").value = d.mada;
                    document.getElementById("edit_ngaydk").value = d.ngaydk;
                    document.getElementById("edit_trangthai").value = d.trangthai;
                } else {
                    alert(data.message);
                }
            } catch (err) {
                console.error(err);
                alert("Lỗi tải dữ liệu đăng ký!");
            }
        });

        // Khi nhấn nút “Cập nhật”
        const editForm = document.getElementById("editDangKyForm");
        editForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const formData = new FormData(editForm);
            try {
                const res = await fetch("/quantri/dangky/update/", {
                    method: "POST",
                    body: formData,
                    headers: { "X-CSRFToken": csrftoken },
                });
                const data = await res.json();
                if (data.status === "success") location.reload();
                else alert(data.message);
            } catch {
                alert("Lỗi kết nối máy chủ!");
            }
        });
    }
});
