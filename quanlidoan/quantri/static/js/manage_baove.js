document.addEventListener("DOMContentLoaded", () => {
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    // === LỌC HỌC VIÊN THEO ĐỒ ÁN ===
    const selectDoAn = document.getElementById("selectDoAn");
    const selectHocVien = document.getElementById("selectHocVien");

    if (selectDoAn) {
        selectDoAn.addEventListener("change", async () => {
            const mada = selectDoAn.value;
            selectHocVien.innerHTML = '<option value="">-- Chọn học viên --</option>';

            if (!mada) return;

            try {
                const res = await fetch(`/quantri/dangky/by_doan/?mada=${encodeURIComponent(mada)}`);
                const data = await res.json();

                if (data.status === "success") {
                    data.data.forEach((hv) => {
                        const opt = document.createElement("option");
                        opt.value = hv.mahv;
                        opt.textContent = hv.hoten;
                        selectHocVien.appendChild(opt);
                    });
                } else {
                    alert(data.message);
                }
            } catch (err) {
                alert("Lỗi tải danh sách học viên!");
                console.error(err);
            }
        });
    }

    // === Thêm biên bản ===
    const addForm = document.getElementById("addBienBanForm");
    if (addForm) {
        addForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const formData = new FormData(addForm);
            try {
                const res = await fetch("/quantri/baove/create/", {
                    method: "POST",
                    body: formData,
                    headers: { "X-CSRFToken": csrftoken },
                });
                const data = await res.json();
                if (data.status === "success") location.reload();
                else alert(data.message);
            } catch (err) {
                console.error(err);
                alert("Lỗi kết nối!");
            }
        });
    }

    // === Xem chi tiết biên bản ===
    const viewModal = document.getElementById("viewBienBanModal");
    if (viewModal) {
        viewModal.addEventListener("show.bs.modal", async (event) => {
            const id = event.relatedTarget.dataset.id;
            const content = document.getElementById("bienbanDetailContent");
            content.innerHTML = "<p>Đang tải...</p>";

            try {
                const res = await fetch(`/quantri/baove/detail/${id}/`);
                const data = await res.json();

                if (data.status === "success") {
                    const bb = data.data;
                    let diemHtml = "";
                    bb.diemtv.forEach(tv => {
                        diemHtml += `<tr>
              <td>${tv.hoten}</td>
              <td>${tv.vaitro}</td>
              <td>${tv.diem}</td>
            </tr>`;
                    });

                    content.innerHTML = `
            <div class="mb-3">
              <h5>Thông tin biên bản</h5>
              <p><strong>Học viên:</strong> ${bb.hoten}</p>
              <p><strong>Đồ án:</strong> ${bb.tenda}</p>
              <p><strong>Ngày bảo vệ:</strong> ${bb.ngaybaove}</p>
              <p><strong>Địa điểm:</strong> ${bb.diadiem}</p>
              <p><strong>Nội dung:</strong> ${bb.noidung || "-"}</p>
            </div>

            <h5>Điểm thành viên hội đồng</h5>
            <table class="table table-bordered align-middle">
              <thead class="table-light"><tr><th>Thành viên</th><th>Vai trò</th><th>Điểm</th></tr></thead>
              <tbody>${diemHtml || "<tr><td colspan='3' class='text-center'>Chưa có điểm</td></tr>"}</tbody>
            </table>

            <div class="mt-3">
              <h5>Kết quả bảo vệ</h5>
              <p><strong>Điểm trung bình:</strong> ${bb.ketqua.diem || "-"}</p>
              <p><strong>Đánh giá:</strong> ${bb.ketqua.danhgia || "-"}</p>
              <p><strong>Xếp loại:</strong> ${bb.ketqua.xeploai || "-"}</p>
            </div>
          `;
                } else {
                    content.innerHTML = `<p class="text-danger">${data.message}</p>`;
                }
            } catch {
                content.innerHTML = "<p class='text-danger'>Lỗi tải dữ liệu.</p>";
            }
        });
    }

    // === Xóa biên bản ===
    document.querySelectorAll(".btnDeleteBienBan").forEach((btn) => {
        btn.addEventListener("click", async () => {
            if (!confirm("Bạn có chắc muốn xóa biên bản này?")) return;
            const id = btn.dataset.id;
            try {
                const res = await fetch("/quantri/baove/delete/", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": csrftoken,
                    },
                    body: JSON.stringify({ mabb: id }),
                });
                const data = await res.json();
                if (data.status === "success") location.reload();
                else alert(data.message);
            } catch {
                alert("Lỗi kết nối!");
            }
        });
    });

    // === MỞ MODAL SỬA ===
    const editModal = document.getElementById("editBienBanModal");
    if (editModal) {
        editModal.addEventListener("show.bs.modal", async (event) => {
            const id = event.relatedTarget.dataset.id;
            document.getElementById("editMaBB").value = id;

            const tbody = document.getElementById("editDiemTVBody");
            tbody.innerHTML = "<tr><td colspan='3' class='text-center text-muted'>Đang tải...</td></tr>";

            try {
                const res = await fetch(`/quantri/baove/detail/${id}/`);
                const data = await res.json();

                if (data.status === "success") {
                    const bb = data.data;
                    document.getElementById("editNgayBaoVe").value = bb.ngaybaove?.split("/").reverse().join("-") || "";
                    document.getElementById("editDiaDiem").value = bb.diadiem || "";
                    document.getElementById("editNoiDung").value = bb.noidung || "";
                    document.getElementById("editGhiChu").value = bb.ghichu || "";

                    if (bb.diemtv && bb.diemtv.length) {
                        tbody.innerHTML = "";
                        bb.diemtv.forEach(tv => {
                            const tr = document.createElement("tr");
                            tr.innerHTML = `
              <td>${tv.hoten}</td>
              <td>${tv.vaitro}</td>
              <td>
                <input type="number" step="0.25" min="0" max="10"
                       class="form-control form-control-sm diem-input"
                       data-matv="${tv.matv}"
                       value="${tv.diem ?? ''}">
              </td>
            `;
                            tbody.appendChild(tr);
                        });
                    } else {
                        tbody.innerHTML = "<tr><td colspan='3' class='text-center text-muted'>Chưa có điểm thành viên hội đồng</td></tr>";
                    }
                }
            } catch (err) {
                alert("Lỗi tải dữ liệu biên bản!");
                console.error(err);
            }
        });
    }

    // === GỬI YÊU CẦU CẬP NHẬT BIÊN BẢN + ĐIỂM ===
    const editForm = document.getElementById("editBienBanForm");
    if (editForm) {
        editForm.addEventListener("submit", async (e) => {
            e.preventDefault();

            const mabb = document.getElementById("editMaBB").value;
            const diemInputs = document.querySelectorAll(".diem-input");
            const diemtv = Array.from(diemInputs).map(inp => ({
                matv: inp.dataset.matv,
                diem: inp.value || null,
            }));

            const payload = {
                mabb,
                ngaybaove: document.getElementById("editNgayBaoVe").value,
                diadiem: document.getElementById("editDiaDiem").value,
                noidung: document.getElementById("editNoiDung").value,
                ghichu: document.getElementById("editGhiChu").value,
                diemtv,
            };

            try {
                const res = await fetch("/quantri/baove/update/", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": document.querySelector('[name=csrfmiddlewaretoken]').value,
                    },
                    body: JSON.stringify(payload),
                });
                const data = await res.json();
                if (data.status === "success") location.reload();
                else alert(data.message);
            } catch (err) {
                alert("Lỗi kết nối khi cập nhật!");
                console.error(err);
            }
        });
    }
});
