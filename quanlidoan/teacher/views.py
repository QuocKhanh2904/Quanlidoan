from django.shortcuts import render, redirect
from datetime import date, datetime
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from .models import *
from collections import defaultdict
from django.utils.timezone import now
from pathlib import Path
from django.db import connection
from django.conf import settings
from django.urls import reverse
from django.contrib import messages
from urllib.parse import unquote, quote
from django.utils.http import url_has_allowed_host_and_scheme

# Create your views here.
@login_required
def teacher_home(request):
    if not hasattr(request.user, 'giangvien'):
        return HttpResponseForbidden("Bạn không có quyền truy cập")
    return render(request, 'teacher.html')

def dictfetchall(cursor):
    cols = [c[0] for c in cursor.description]
    return [dict(zip(cols, row)) for row in cursor.fetchall()]

def _parse_date(s):
    try:
        return datetime.strptime(s, "%Y-%m-%d").date() if s else None
    except ValueError:
        return None


def _get_magv(user):
    # đổi theo related_name của bạn (giangvien hoặc giangvien_profile)
    gv = getattr(user, "giangvien", None) or getattr(user, "giangvien_profile", None)
    return getattr(gv, "magv", None)

def _check_own_project(magv, mada):
    with connection.cursor() as c:
        c.execute("SELECT COUNT(*) FROM DOAN WHERE MaDA=%s AND MaGV=%s", [mada, magv])
        cnt, = c.fetchone()
    return cnt > 0

def hoi_dong_cua_toi(request):
    magv = _get_magv(request.user)
    if not magv:
        return HttpResponseForbidden("Tài khoản chưa liên kết mã giảng viên.")

    q = (request.GET.get("q") or "").strip()
    show_past = (request.GET.get("past") == "1")

    where = ["TV.MaGV = %s"]
    params = [magv]

    if not show_past:
        where.append("(BB.NgayBaoVe IS NULL OR BB.NgayBaoVe >= CAST(GETDATE() AS DATE))")

    if q:
        like = f"%{q}%"
        where.append("(HD.TenHD LIKE %s OR D.TenDA LIKE %s OR HV.HoTen LIKE %s)")
        params += [like, like, like]

    where_sql = " AND ".join(where)

    with connection.cursor() as c:
        c.execute(f"""
            SELECT
              HD.MaHD       AS mahd,
              HD.TenHD      AS tenhd,
              BB.NgayBaoVe  AS ngaybaove,
              BB.DiaDiem    AS diadiem,
              D.MaDA        AS mada,
              D.TenDA       AS tenda,
              D.LinhVuc     AS linhvuc,
              D.TrangThai   AS trangthai,
              HV.MaHV       AS mahv,
              HV.HoTen      AS tenhv
            FROM THANHVIENHOIDONG TV
            JOIN HOIDONG HD ON HD.MaHD = TV.MaHD
            JOIN DOAN D     ON D.MaHD  = HD.MaHD
            OUTER APPLY (
                SELECT TOP 1 NgayBaoVe, DiaDiem
                FROM BIENBAN BB0
                WHERE BB0.MaDA = D.MaDA
                ORDER BY BB0.NgayBaoVe DESC, BB0.MaBB DESC
            ) AS BB
            LEFT JOIN DANGKY DK  ON DK.MaDA = D.MaDA AND DK.TrangThai = 1
            LEFT JOIN HOCVIEN HV ON HV.MaHV = DK.MaHV
            WHERE {where_sql}
            ORDER BY BB.NgayBaoVe, HD.MaHD, D.MaDA
        """, params)
        rows = dictfetchall(c)

    groups = defaultdict(lambda: {"de_tai": []})
    for r in rows:
        g = groups[r["mahd"]]
        if "tenhd" not in g:
            g.update({
                "mahd": r["mahd"],
                "tenhd": r["tenhd"],
                "ngaybaove": r["ngaybaove"],
                "diadiem": r["diadiem"],
            })
        if r["mada"]:
            g["de_tai"].append({
                "mada": r["mada"],
                "tenda": r["tenda"],
                "linhvuc": r["linhvuc"],
                "trangthai": r["trangthai"],
                "mahv": r["mahv"],
                "tenhv": r["tenhv"],
                "ngaybaove": r["ngaybaove"],
                "diadiem": r["diadiem"],
            })

    return render(request, "teacher/hoi_dong_cua_toi.html", {
        "q": q,
        "show_past": show_past,
        "hoidongs": list(groups.values()),
        "tong_hd": len(groups),
        "tong_dt": len(rows),
    })


def DanhSachDoAn(request):
    magv = _get_magv(request.user)
    if not magv:
        return HttpResponseForbidden("Tài khoản chưa liên kết mã giảng viên.")

    q = (request.GET.get("q") or "").strip()
    status = (request.GET.get("status") or "").strip()

    # --- 1) Danh sách có áp dụng lọc q/status ---
    where = ["D.MaGV = %s"]
    params = [magv]
    if q:
        like = f"%{q}%"
        where.append("""
            (
              D.TenDA LIKE %s OR D.LinhVuc LIKE %s OR D.MoTa LIKE %s
              OR CAST(D.MaDA AS NVARCHAR(50)) LIKE %s
            )
        """)
        params += [like, like, like, like]
    if status in {"0", "1", "2", "3"}:
        where.append("D.TrangThai = %s")
        params.append(int(status))
    where_sql = " AND ".join(where)

    with connection.cursor() as cur:
        cur.execute(f"""
            SELECT 
                D.MaDA        AS mada,
                D.TenDA       AS tenda,
                D.LinhVuc     AS linhvuc,
                D.TrangThai   AS trangthai,
                D.MoTa        AS mota,
                D.NgayGui     AS ngaygui,
                D.MaGV        AS magv,
                G.HoTen       AS giangvien,
                ISNULL(Tlatest.TienDoPhanTram, 0) AS tiendo,
                Tlatest.NgayCapNhat               AS ngaytiendo
            FROM DOAN D
            LEFT JOIN GIANGVIEN G ON D.MaGV = G.MaGV
            OUTER APPLY (
                SELECT TOP 1 T.TienDoPhanTram, T.NgayCapNhat
                FROM TIENDO T
                WHERE T.MaDA = D.MaDA
                ORDER BY T.NgayCapNhat DESC, T.MaTD DESC
            ) AS Tlatest
            WHERE {where_sql}
            ORDER BY D.NgayGui DESC, D.MaDA DESC
        """, params)
        doans = dictfetchall(cur)

    # --- 2) Tổng KHÔNG đổi (chỉ theo giáo viên) ---
    with connection.cursor() as c:
        c.execute("""
            SELECT
                COUNT(*)                                                   AS tong_so_do_an,
                ISNULL(SUM(CASE WHEN TrangThai=0 THEN 1 ELSE 0 END), 0)    AS tong_chua_duyet,
                ISNULL(SUM(CASE WHEN TrangThai=2 THEN 1 ELSE 0 END), 0)    AS tong_dang_thuc_hien,
                ISNULL(SUM(CASE WHEN TrangThai=3 THEN 1 ELSE 0 END), 0)    AS tong_da_hoan_thanh
            FROM DOAN
            WHERE MaGV = %s
        """, [magv])
        tong, chua_duyet, dang_th, da_ht = c.fetchone()

    ctx = {
        "doans": doans,
        "tong_so_do_an": tong,
        "tong_chua_duyet": chua_duyet,
        "tong_dang_thuc_hien": dang_th,
        "tong_da_hoan_thanh": da_ht,
        "count_filtered": len(doans),
        "q": q, "status": status,
    }
    return render(request, "danh_sach_do_an.html", ctx)


def ThemDoAn(request):
    # 🧩 Nếu người dùng bấm "Lưu"
    if request.method == "POST":
        tenda = request.POST.get("tenda", "").strip()
        linhvuc = request.POST.get("linhvuc", "").strip()
        soluong = request.POST.get("soluong") or None
        mota = request.POST.get("mota", "").strip() or None
        ngaybd = request.POST.get("ngaybd") or None
        ngaykt = request.POST.get("ngaykt") or None
        magv = request.user.giangvien.magv

        # ⚠️ Kiểm tra dữ liệu bắt buộc
        if not tenda:
            return render(request, "them_do_an.html", {
                "error": "Tên đồ án là bắt buộc.",
                "form": request.POST
            })

        # 🧠 Thực hiện lưu vào cơ sở dữ liệu
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO DOAN (TenDA, LinhVuc, SoLuongToiDa, NgayGui, MoTa, NgayBD, NgayKT, MaGV, TrangThai)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, '0');
            """, [tenda, linhvuc or None, soluong, date.today(), mota or None, ngaybd, ngaykt, magv])

        # ✅ Lưu thành công → quay lại danh sách đồ án
        return redirect("danh_sach_do_an")

    # 🧠 Nếu là GET → hiển thị form
    return render(request, "them_do_an.html")


def ChiTietDoAn(request, mada):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
              D.MaDA, D.TenDA, D.TrangThai, D.SoLuongToiDa, D.NgayGui,
              D.MoTa, D.LinhVuc, D.NgayBD, D.NgayKT,
              D.MaGV, G.HoTen AS TenGV
            FROM DOAN D
            LEFT JOIN GIANGVIEN G ON D.MaGV = G.MaGV
            WHERE D.MaDA = %s
        """, [mada])
        row = cursor.fetchone()

    if not row:
        return redirect("danh_sach_do_an")

    keys = ["MaDA","TenDA","TrangThai","SoLuongToiDa","NgayGui",
            "MoTa","LinhVuc","NgayBD","NgayKT","MaGV","TenGV"]
    da = dict(zip(keys, row))
    return render(request, "chi_tiet_do_an.html", {"da": da})

def SuaDoAn(request, mada):
    user = request.user

    # Lấy MaGV từ user (nếu là giáo viên)
    magv_user = getattr(getattr(user, "giangvien_profile", None), "magv", None)

    if request.method == "POST":
        tenda = request.POST.get("tenda", "").strip()
        linhvuc = request.POST.get("linhvuc", "").strip() or None
        soluong = request.POST.get("soluong") or None
        mota = request.POST.get("mota", "").strip() or None
        ngaybd = _parse_date(request.POST.get("ngaybd"))
        ngaykt = _parse_date(request.POST.get("ngaykt"))
        magv = request.POST.get("magv") or None
        
        if not tenda:
            return render(request, "sua_do_an.html", {
                "error": "Tên đồ án là bắt buộc.",
                "doan": request.POST
            })

        with connection.cursor() as cursor:
            # Nếu là giáo viên → chỉ được sửa đồ án của mình
            if magv_user:
                cursor.execute("""
                    UPDATE DOAN
                    SET TenDA=%s, LinhVuc=%s, SoLuongToiDa=%s, MoTa=%s, NgayBD=%s, NgayKT=%s
                    WHERE MaDA=%s AND MaGV=%s
                """, [tenda, linhvuc, soluong, mota, ngaybd, ngaykt, mada, magv_user])
            else:
                # Admin: nhận magv nếu có, nếu rỗng thì GIỮ NGUYÊN
                trangthai = request.POST.get("trangthai")
                ngaygui   = _parse_date(request.POST.get("ngaygui"))
                magv_raw  = request.POST.get("magv")  # không dùng "or None"
                cursor.execute("""
                    UPDATE DOAN
                    SET TenDA=%s, LinhVuc=%s,
                        TrangThai=COALESCE(%s, TrangThai),
                        SoLuongToiDa=%s,
                        NgayGui=COALESCE(%s, NgayGui),
                        MoTa=%s, NgayBD=%s, NgayKT=%s,
                        MaGV=COALESCE(NULLIF(%s, ''), MaGV)
                    WHERE MaDA=%s
                """, [tenda, linhvuc, trangthai, soluong, ngaygui, mota, ngaybd, ngaykt, magv_raw, mada])

        return redirect("danh_sach_do_an")

    # GET: lấy dữ liệu hiện tại
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT MaDA, TenDA, LinhVuc, TrangThai, SoLuongToiDa, NgayGui,
                   MoTa, NgayBD, NgayKT, MaGV
            FROM DOAN
            WHERE MaDA=%s
        """, [mada])
        row = cursor.fetchone()

    if not row:
        return redirect("danh_sach_do_an")

    doan = {
        "mada": row[0],
        "tenda": row[1],
        "linhvuc": row[2],
        "trangthai": row[3],
        "soluong": row[4],
        "ngaygui": row[5],
        "mota": row[6],
        "ngaybd": row[7],
        "ngaykt": row[8],
        "magv": row[9],
    }

    return render(request, "sua_do_an.html", {"doan": doan, "is_teacher": bool(magv_user)})

def XoaDoAn(request, mada):
    # Lấy thông tin cơ bản + tên giảng viên
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
              D.MaDA, D.TenDA, D.LinhVuc, D.TrangThai, D.NgayGui,
              D.SoLuongToiDa, D.MaGV, G.HoTen AS TenGV
            FROM DOAN D
            LEFT JOIN GIANGVIEN G ON D.MaGV = G.MaGV
            WHERE D.MaDA = %s
        """, [mada])
        row = cursor.fetchone()

    if not row:
        return redirect("danh_sach_do_an")

    if request.method == "POST":
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM DOAN WHERE MaDA=%s", [mada])
        return redirect("danh_sach_do_an")

    doan = {
        "mada": row[0],
        "tenda": row[1],
        "linhvuc": row[2],
        "trangthai": row[3],
        "ngaygui": row[4],
        "soluong": row[5],
        "magv": row[6],
        "tengv": row[7],
    }
    return render(request, "xoa_do_an.html", {"doan": doan})

def BaoCaoDangKy(request):
    q = request.GET.get("q", "").strip()

    base_sql = """
        SELECT 
            HV.HoTen AS HocVien,
            DA.TenDA,
            GV.HoTen AS GiangVien,
            HD.TenHD
        FROM DANGKY DK
        JOIN HOCVIEN HV ON DK.MaHV = HV.MaHV
        JOIN DOAN DA ON DK.MaDA = DA.MaDA
        LEFT JOIN HUONGDANDOAN HDD ON HDD.MaDA = DA.MaDA AND (HDD.VaiTro = N'Hướng dẫn' OR HDD.VaiTro IS NULL)
        LEFT JOIN GIANGVIEN GV ON HDD.MaGV = GV.MaGV
        LEFT JOIN (
            SELECT TV.mahd, TV.matv, TV.magv
            FROM THANHVIENHOIDONG TV
        ) TV ON 1=1  -- chỉ để tạo đường sang HD; nếu có mapping đồ án-hội đồng riêng, hãy dùng bảng đó
        LEFT JOIN HOIDONG HD ON HD.MaHD = TV.MaHD
        /* WHERE (lọc) */
        ORDER BY HV.HoTen, DA.TenDA
    """
    params = []
    if q:
        base_sql = base_sql.replace("/* WHERE (lọc) */",
            "WHERE HV.HoTen LIKE %s OR DA.TenDA LIKE %s OR GV.HoTen LIKE %s OR HD.TenHD LIKE %s")
        like = f"%{q}%"
        params = [like, like, like, like]
    else:
        base_sql = base_sql.replace("/* WHERE (lọc) */", "")

    with connection.cursor() as cursor:
        cursor.execute(base_sql, params)
        rows = dictfetchall(cursor)

    ctx = {"rows": rows, "q": q, "tong": len(rows)}
    return render(request, "baocao_dangky.html", ctx)


# ---- Helpers quyền hạn ----
def _is_supervisor(magv, mada):
    """GV là người hướng dẫn đồ án (HUONGDANDOAN)."""
    with connection.cursor() as c:
        c.execute("""
            SELECT COUNT(*) 
            FROM HUONGDANDOAN 
            WHERE MaGV=%s AND MaDA=%s AND (VaiTro=N'Hướng dẫn' OR VaiTro IS NULL)
        """, [magv, mada])
        cnt, = c.fetchone()
    return cnt > 0

def _can_update_progress(magv, mada):
    """GV được phép cập nhật tiến độ nếu là chủ nhiệm (DOAN.MaGV) hoặc người hướng dẫn."""
    return _check_own_project(magv, mada) or _is_supervisor(magv, mada)

# ---- 2.1 Danh sách đồ án GV đang hướng dẫn ----
def DanhSachHuongDan(request):
    magv = _get_magv(request.user)
    if not magv:
        return HttpResponseForbidden("Tài khoản chưa liên kết mã giảng viên.")

    q = (request.GET.get("q") or "").strip()
    status = (request.GET.get("status") or "").strip()

    where = ["HDD.MaGV = %s", "(HDD.VaiTro=N'Hướng dẫn' OR HDD.VaiTro IS NULL)"]
    params = [magv]

    if q:
        like = f"%{q}%"
        where.append("""
            (
              D.TenDA LIKE %s OR D.LinhVuc LIKE %s OR D.MoTa LIKE %s
              OR CAST(D.MaDA AS NVARCHAR(50)) LIKE %s
              OR HV.HoTen LIKE %s
            )
        """)
        params += [like, like, like, like, like]

    if status in {"0","1","2","3"}:
        where.append("D.TrangThai = %s")
        params.append(int(status))

    where_sql = " AND ".join(where)

    with connection.cursor() as c:
        c.execute(f"""
            SELECT 
                D.MaDA AS mada, D.TenDA AS tenda, D.LinhVuc AS linhvuc,
                D.TrangThai AS trangthai, D.MoTa AS mota, D.NgayGui AS ngaygui,
                -- sinh viên (nếu có đăng ký được duyệt)
                HV.HoTen AS tenhv,
                -- tiến độ mới nhất
                ISNULL(Tlatest.TienDoPhanTram,0) AS tiendo,
                Tlatest.NgayCapNhat AS ngaytiendo
            FROM HUONGDANDOAN HDD
            JOIN DOAN D        ON D.MaDA = HDD.MaDA
            LEFT JOIN (
                SELECT DK.MaDA, HV.HoTen
                FROM DANGKY DK 
                JOIN HOCVIEN HV ON HV.MaHV = DK.MaHV
                WHERE DK.TrangThai = 1
            ) AS HV ON HV.MaDA = D.MaDA
            OUTER APPLY (
                SELECT TOP 1 T.TienDoPhanTram, T.NgayCapNhat
                FROM TIENDO T
                WHERE T.MaDA = D.MaDA
                ORDER BY T.NgayCapNhat DESC, T.MaTD DESC
            ) AS Tlatest
            WHERE {where_sql}
            ORDER BY D.NgayGui DESC, D.MaDA DESC
        """, params)
        projects = dictfetchall(c)

    return render(request, "teacher/huongdan_list.html", {
        "projects": projects, "q": q, "status": status,
        "count_filtered": len(projects),
    })

# ---- 2.2 Xem & giao tiến độ cho đồ án hướng dẫn ----
def HD_XemTienDo(request, mada):
    magv = _get_magv(request.user)
    if not magv:
        return HttpResponseForbidden("Tài khoản chưa liên kết mã giảng viên.")
    if not _can_update_progress(magv, mada):
        return HttpResponseForbidden("Bạn không có quyền với đồ án này.")

    with connection.cursor() as c:
        c.execute("""
            SELECT D.MaDA AS mada, D.TenDA AS tenda, D.LinhVuc AS linhvuc,
                   T.TienDoPhanTram AS tiendo_moi, T.NgayCapNhat AS ngay_moi
            FROM DOAN D
            OUTER APPLY (
                SELECT TOP 1 TienDoPhanTram, NgayCapNhat
                FROM TIENDO
                WHERE MaDA=D.MaDA AND NguoiKiemTra IS NOT NULL     -- ★
                ORDER BY NgayCapNhat DESC, MaTD DESC
            ) AS T
            WHERE D.MaDA=%s
        """, [mada])
        rows = dictfetchall(c)
    if not rows:
        return redirect("ds_huong_dan")

    doan = rows[0]
    p = doan.get("tiendo_moi") or 0
    try:
        doan["tiendo_pct"] = int(round(float(p)))
    except Exception:
        doan["tiendo_pct"] = 0

    with connection.cursor() as c:
        c.execute("""
            SELECT MaTD AS matd, MoTaCongViec AS motacongviec,
                   [File] AS baocao, TienDoPhanTram AS tiendophantram,
                   NgayCapNhat AS ngaycapnhat, NguoiKiemTra AS nguoicham
            FROM TIENDO
            WHERE MaDA=%s
            ORDER BY NgayCapNhat DESC, MaTD DESC
        """, [mada])
        tiendos = dictfetchall(c)

    back_url = reverse("ds_huong_dan")
    return render(request, "teacher/hd_tiendo.html", {
        "doan": doan, "tiendos": tiendos, "back_url": back_url,
    })

# ---- 2.4 Đánh giá / xác nhận kiểm tra một mốc ----
def HD_DanhGiaTienDo(request, matd):
    if request.method != "POST":
        with connection.cursor() as c:
            c.execute("SELECT MaDA FROM TIENDO WHERE MaTD=%s", [matd])
            row = c.fetchone()
        return redirect("hd_xem_tiendo", mada=row[0] if row else 0)

    magv = _get_magv(request.user)
    if not magv:
        return HttpResponseForbidden("Tài khoản chưa liên kết mã GV.")

    with connection.cursor() as c:
        c.execute("""
            SELECT MaDA, [File], TienDoPhanTram, NgayCapNhat, NguoiKiemTra
            FROM TIENDO WHERE MaTD=%s
        """, [matd])
        row = c.fetchone()
    if not row:
        return redirect("ds_huong_dan")

    mada, baocao, cur_percent, this_time, nguoicham = row

    if not _can_update_progress(magv, mada):
        return HttpResponseForbidden("Bạn không có quyền với đồ án này.")
    if not baocao:
        messages.error(request, "Chưa có báo cáo để chấm.")
        return redirect("hd_xem_tiendo", mada=mada)
    if nguoicham:  # đã chấm rồi
        messages.info(request, "Mốc này đã được duyệt trước đó.")
        return redirect("hd_xem_tiendo", mada=mada)

    try:
        new_percent = int(request.POST.get("phantram"))
    except (TypeError, ValueError):
        messages.error(request, "Vui lòng nhập phần trăm hợp lệ.")
        return redirect("hd_xem_tiendo", mada=mada)
    new_percent = max(0, min(100, new_percent))

    with connection.cursor() as c:
        c.execute("""
            SELECT TOP 1 TienDoPhanTram
            FROM TIENDO
            WHERE MaDA=%s AND NguoiKiemTra IS NOT NULL
              AND (NgayCapNhat < %s OR (NgayCapNhat=%s AND MaTD < %s))
            ORDER BY NgayCapNhat DESC, MaTD DESC
        """, [mada, this_time, this_time, matd])
        prev = c.fetchone()
    prev_percent = prev[0] if prev else 0
    if new_percent < prev_percent:
        messages.error(request, f"% mới ({new_percent}%) không được thấp hơn mốc đã duyệt trước đó ({prev_percent}%).")
        return redirect("hd_xem_tiendo", mada=mada)
    # Lấy mốc đã duyệt lớn nhất TRƯỚC mốc đang chấm
    with connection.cursor() as c:
        c.execute("""
            SELECT ISNULL(MAX(TienDoPhanTram),0)
            FROM TIENDO
            WHERE MaDA=%s AND NguoiKiemTra IS NOT NULL
            AND (NgayCapNhat < %s OR (NgayCapNhat=%s AND MaTD < %s))
        """, [mada, this_time, this_time, matd])
        max_before = row[0] if row and row[0] is not None else 0

    if new_percent < max_before:
        messages.error(request, f"% mới ({new_percent}%) không được nhỏ hơn mốc đã duyệt trước đó ({max_before}%).")
        return redirect("hd_xem_tiendo", mada=mada)

    # Lấy mốc đã duyệt nhỏ nhất SAU mốc đang chấm
    with connection.cursor() as c:
        c.execute("""
            SELECT MIN(TienDoPhanTram)
            FROM TIENDO
            WHERE MaDA=%s AND NguoiKiemTra IS NOT NULL
            AND (NgayCapNhat > %s OR (NgayCapNhat=%s AND MaTD > %s))
        """, [mada, this_time, this_time, matd])
        row = c.fetchone()
        min_after = row[0] if row and row[0] is not None else None

    if min_after is not None and new_percent > min_after:
        messages.error(request, f"% mới ({new_percent}%) không được lớn hơn mốc đã duyệt sau đó ({min_after}%).")
        return redirect("hd_xem_tiendo", mada=mada)


    with connection.cursor() as c:
        c.execute("""
            UPDATE TIENDO
            SET TienDoPhanTram=%s, NguoiKiemTra=%s
            WHERE MaTD=%s
        """, [new_percent, str(magv), matd])

        c.execute("""
            SELECT TOP 1 TienDoPhanTram
            FROM TIENDO
            WHERE MaDA=%s AND NguoiKiemTra IS NOT NULL
            ORDER BY NgayCapNhat DESC, MaTD DESC
        """, [mada])
        row = c.fetchone()
        latest = row[0] if row else 0
        if latest == 100:
            c.execute("UPDATE DOAN SET TrangThai=3 WHERE MaDA=%s", [mada])
        else:
            c.execute("UPDATE DOAN SET TrangThai=2 WHERE MaDA=%s AND TrangThai=3", [mada])

    messages.success(request, "Đã duyệt báo cáo & cập nhật %.")  # ký tự % trong message là bình thường
    return redirect("hd_xem_tiendo", mada=mada)
    

def HD_HuyDuyetTienDo(request, matd):
    """Hủy duyệt một mốc: đặt NguoiKiemTra=NULL, tính lại % & trạng thái đồ án."""
    if request.method != "POST":
        with connection.cursor() as c:
            c.execute("SELECT MaDA FROM TIENDO WHERE MaTD=%s", [matd])
            row = c.fetchone()
        return redirect("hd_xem_tiendo", mada=row[0] if row else 0)

    # Lấy thông tin mốc
    with connection.cursor() as c:
        c.execute("""
            SELECT MaDA, NguoiKiemTra
            FROM TIENDO
            WHERE MaTD=%s
        """, [matd])
        row = c.fetchone()

    if not row:
        messages.error(request, "Không tìm thấy mốc tiến độ.")
        return redirect("ds_huong_dan")

    mada, nguoicham = row

    magv = _get_magv(request.user)
    if not magv:
        return HttpResponseForbidden("Tài khoản chưa liên kết mã giảng viên.")
    if not _can_update_progress(magv, mada):
        return HttpResponseForbidden("Bạn không có quyền với đồ án này.")

    if not nguoicham:
        messages.info(request, "Mốc này hiện chưa được duyệt.")
        return redirect("hd_xem_tiendo", mada=mada)

    # Hủy duyệt
    with connection.cursor() as c:
        c.execute("""
            UPDATE TIENDO
            SET NguoiKiemTra = NULL
            WHERE MaTD=%s
        """, [matd])

        # Tính lại % đã duyệt mới nhất & cập nhật trạng thái đồ án
        c.execute("""
            SELECT TOP 1 TienDoPhanTram
            FROM TIENDO
            WHERE MaDA=%s AND NguoiKiemTra IS NOT NULL
            ORDER BY NgayCapNhat DESC, MaTD DESC
        """, [mada])
        row = c.fetchone()
        latest = row[0] if row else 0

        if latest == 100:
            c.execute("UPDATE DOAN SET TrangThai=3 WHERE MaDA=%s", [mada])
        else:
            # nếu trước đó là 3 nhưng giờ không còn đủ 100% thì kéo về 2
            c.execute("UPDATE DOAN SET TrangThai=2 WHERE MaDA=%s AND TrangThai=3", [mada])

    messages.success(request, "Đã hủy duyệt mốc tiến độ. Bạn có thể chấm lại.")
    url = reverse("hd_xem_tiendo", kwargs={"mada": mada})
    back = request.GET.get("back")
    return redirect(f"{url}?back={quote(back)}" if back else url)