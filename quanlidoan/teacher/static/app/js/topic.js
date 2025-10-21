

function openModal(mada, tenda, linhvuc, giangvien, mota) {
    document.getElementById("modal").style.display = "block";
    document.getElementById("modal-id").innerText = mada;
    document.getElementById("modal-name").innerText = tenda;
    document.getElementById("modal-field").innerText = linhvuc;
    document.getElementById("modal-teacher").innerText = giangvien;
    document.getElementById("modal-desc").innerText = mota;
}

function closeModal() {
    document.getElementById("modal").style.display = "none";
}

window.onclick = function (event) {
    let modal = document.getElementById("modal");
    if (event.target == modal) {
        modal.style.display = "none";
    }
}
