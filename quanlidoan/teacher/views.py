from django.shortcuts import render, redirect
from django.utils import timezone
from datetime import date, datetime
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from .models import *
from collections import defaultdict
from django.template.loader import get_template
from django.http import HttpResponse
from weasyprint import HTML
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
    return render(request, 'teacher_home.html')

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

@login_required
def hoi_dong_cua_toi(request):
    magv = _get_magv(request.user)
    if not magv:
        return HttpResponseForbidden("Tài khoản chưa liên kết mã giảng viên.")

    q = (request.GET.get("q") or "").strip()
    show_past = (request.GET.get("past") == "1")

    where = ["TV.MaGV = %s"]
    params = [magv]

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
                HV.HoTen      AS tenhv,
                TV.VaiTro     AS vai_tro,

                -- ✅ Điểm trung bình hội đồng (lấy từ KETQUABAOVE đã được trigger tính)
                (
                    SELECT TOP 1 KQ.Diem
                    FROM KETQUABAOVE KQ
                    JOIN BIENBAN BBX ON KQ.MaBB = BBX.MaBB
                    WHERE BBX.MaDA = D.MaDA
                    ORDER BY BBX.NgayBaoVe DESC, BBX.MaBB DESC
                ) AS diem_hoidong,

                -- ✅ Có biên bản hay chưa
                CASE WHEN EXISTS(SELECT 1 FROM BIENBAN BBX WHERE BBX.MaDA = D.MaDA)
                     THEN 1 ELSE 0 END AS has_bienban,

                -- ✅ Đã chấm đủ hay chưa (kiểm tra trigger đã tạo bản ghi)
                CASE WHEN EXISTS(
                    SELECT 1 FROM KETQUABAOVE KQ
                    JOIN BIENBAN BBX ON KQ.MaBB = BBX.MaBB
                    WHERE BBX.MaDA = D.MaDA
                )
                THEN 1 ELSE 0 END AS da_nhap_diem

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
            ORDER BY BB.NgayBaoVe DESC, HD.MaHD, D.MaDA
        """, params)
        rows = dictfetchall(c)

    # ✅ Gom nhóm theo hội đồng
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
            r["is_secretary"] = (r.get("vai_tro") == "Thư ký")
            r["can_enter_score"] = bool(r["has_bienban"])
            g["de_tai"].append(r)

    return render(request, "hoi_dong_cua_toi.html", {
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

    # ✅ KHÔNG dùng f-string để tránh lỗi dấu %
    sql = (
        """
        SELECT 
            D.MaDA AS mada,
            D.TenDA AS tenda,
            D.LinhVuc AS linhvuc,
            D.TrangThai AS trangthai,
            D.MoTa AS mota,
            D.NgayGui AS ngaygui,

            D.DiemHuongDan        AS diem_hd,
            D.NgayChamHuongDan    AS ngaycham,

            HV.HoTen AS tenhv,

            ISNULL(Tlatest.TienDoPhanTram,0) AS tiendo,
            Tlatest.NgayCapNhat               AS ngaytiendo
        FROM HUONGDANDOAN HDD
        JOIN DOAN D ON D.MaDA = HDD.MaDA
        LEFT JOIN (
            SELECT DK.MaDA, HV.HoTen
            FROM DANGKY DK
            JOIN HOCVIEN HV ON HV.MaHV = DK.MaHV
            WHERE DK.TrangThai = 1
        ) AS HV ON HV.MaDA = D.MaDA
        OUTER APPLY (
            SELECT TOP 1 T.TienDoPhanTram, T.NgayCapNhat
            FROM TIENDO T
            WHERE T.MaDA = D.MaDA AND T.NguoiKiemTra IS NOT NULL
            ORDER BY T.NgayCapNhat DESC, T.MaTD DESC
        ) AS Tlatest
        WHERE """
        + where_sql +
        """
        ORDER BY D.NgayGui DESC, D.MaDA DESC
        """
    )

    # Mở cursor đúng cách
    with connection.cursor() as c:
        c.execute(sql, params)
        doans = dictfetchall(c)

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
            "q": q,
            "status": status,
        }
        return render(request, "danh_sach_do_an.html", ctx)

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
                if magv_raw is not None and magv_raw.strip() != "":
                    with connection.cursor() as cursor:
                        cursor.execute("""
                            IF NOT EXISTS (
                                SELECT 1 FROM HUONGDANDOAN
                                WHERE MaDA = %s AND MaGV = %s
                                AND (VaiTro = N'Hướng dẫn' OR VaiTro IS NULL)
                            )
                            BEGIN
                                INSERT INTO HUONGDANDOAN (MaDA, MaGV, VaiTro)
                                VALUES (%s, %s, N'Hướng dẫn');
                            END
                        """, [mada, magv_raw, mada, magv_raw])

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

def _is_secretary(magv, mada):
    """Giáo viên là Thư ký trong hội đồng của đồ án."""
    with connection.cursor() as c:
        c.execute("""
            SELECT COUNT(*)
            FROM THANHVIENHOIDONG TV
            JOIN HOIDONG HD ON HD.MaHD = TV.MaHD
            JOIN DOAN D ON D.MaHD = HD.MaHD
            WHERE D.MaDA = %s AND TV.MaGV = %s AND TV.VaiTro = N'Thư ký'
        """, [mada, magv])
        cnt, = c.fetchone()
    return cnt > 0

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
                D.MaDA AS mada,
                D.TenDA AS tenda,
                D.LinhVuc AS linhvuc,
                D.TrangThai AS trangthai,
                D.MoTa AS mota,
                D.NgayGui AS ngaygui,
                D.DiemHuongDan AS diem_hd,             -- ✅ điểm hướng dẫn
                D.NhanXetHuongDan AS nhanxet_hd,       -- ✅ nhận xét
                D.NgayChamHuongDan AS ngaycham_hd,     -- ✅ ngày chấm
                HV.HoTen AS tenhv,
                ISNULL(Tlatest.TienDoPhanTram,0) AS tiendo,
                Tlatest.NgayCapNhat AS ngaytiendo
            FROM HUONGDANDOAN HDD
            JOIN DOAN D ON D.MaDA = HDD.MaDA
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

    return render(request, "huongdan_list.html", {
        "projects": projects,
        "q": q,
        "status": status,
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
    return render(request, "hd_tiendo.html", {
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

    # Giới hạn hợp lệ
    new_percent = max(0, min(100, new_percent))

    with connection.cursor() as c:
        # ✅ Lấy phần trăm đã duyệt lớn nhất TRƯỚC mốc hiện tại (trong cùng đồ án)
        c.execute("""
            SELECT ISNULL(MAX(TienDoPhanTram), 0)
            FROM TIENDO
            WHERE MaDA = %s
            AND NguoiKiemTra IS NOT NULL
            AND (NgayCapNhat < %s OR (NgayCapNhat = %s AND MaTD < %s))
        """, [mada, this_time, this_time, matd])
        prev_row = c.fetchone()
        prev_percent = prev_row[0] if prev_row and prev_row[0] is not None else 0

        # ✅ Lấy phần trăm đã duyệt nhỏ nhất SAU mốc hiện tại (trong cùng đồ án)
        c.execute("""
            SELECT MIN(TienDoPhanTram)
            FROM TIENDO
            WHERE MaDA = %s
            AND NguoiKiemTra IS NOT NULL
            AND (NgayCapNhat > %s OR (NgayCapNhat = %s AND MaTD > %s))
        """, [mada, this_time, this_time, matd])
        next_row = c.fetchone()
        next_percent = next_row[0] if next_row and next_row[0] is not None else None

    # 🚦 Kiểm tra điều kiện tiến độ tăng hợp lý trong cùng đồ án
    if new_percent < prev_percent:
        messages.error(
            request,
            f"% mới ({new_percent}%) không được nhỏ hơn mốc đã duyệt trước đó ({prev_percent}%) của đồ án này."
        )
        return redirect("hd_xem_tiendo", mada=mada)

    if next_percent is not None and new_percent > next_percent:
        messages.error(
            request,
            f"% mới ({new_percent}%) không được lớn hơn mốc đã duyệt sau đó ({next_percent}%) của đồ án này."
        )
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
        if latest >= 100:
            c.execute("UPDATE DOAN SET TrangThai = 3 WHERE MaDA = %s", [mada])  # Hoàn thành
        elif latest > 0:
            c.execute("UPDATE DOAN SET TrangThai = 2 WHERE MaDA = %s", [mada])  # Đang thực hiện
        else:
            c.execute("UPDATE DOAN SET TrangThai = 1 WHERE MaDA = %s", [mada])  # Đã duyệt (chưa bắt đầu)

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

@login_required
def HD_ChamDiem(request, mada):
    magv = _get_magv(request.user)
    if not magv:
        return HttpResponseForbidden("Tài khoản chưa liên kết mã giảng viên.")

    # ✅ Chỉ cho truy cập nếu GV là hướng dẫn hoặc thư ký hội đồng
    if not (_can_update_progress(magv, mada) or _is_secretary(magv, mada)):
        return HttpResponseForbidden("Bạn không có quyền với đồ án này.")

    # Xử lý đường quay lại an toàn
    raw_back = request.GET.get("back")
    back_url = unquote(raw_back) if raw_back else (request.META.get("HTTP_REFERER") or reverse("ds_huong_dan"))
    if not url_has_allowed_host_and_scheme(back_url, {request.get_host()}, request.is_secure()):
        back_url = reverse("ds_huong_dan")

    # ✅ Chỉ cho chấm khi tiến độ đã duyệt 100%
    with connection.cursor() as c:
        c.execute("""
            SELECT ISNULL(MAX(TienDoPhanTram), 0)
            FROM TIENDO
            WHERE MaDA = %s AND NguoiKiemTra IS NOT NULL
        """, [mada])
        row = c.fetchone()
    approved_max = int(row[0]) if row and row[0] is not None else 0
    if approved_max < 100:
        messages.warning(request, f"Tiến độ hiện tại {approved_max}% — chỉ chấm điểm khi đạt 100%.")
        return redirect(back_url)

    # ✅ Lấy thông tin đồ án hiện tại
    with connection.cursor() as c:
        c.execute("""
            SELECT MaDA, TenDA, DiemHuongDan, DiemHoiDong, DiemPhanBien,
                   NhanXetHuongDan, NhanXetHoiDong
            FROM DOAN WHERE MaDA = %s
        """, [mada])
        row = c.fetchone()

    if not row:
        messages.error(request, "Không tìm thấy đồ án.")
        return redirect(back_url)

    mada_db, tenda, diem_hd, diem_hdong, diem_phanbien, nx_hd, nx_hdong = row
    is_secretary = _is_secretary(magv, mada)

    # ======================= XỬ LÝ POST ==========================
    if request.method == "POST":
        if not is_secretary:
            messages.error(request, "Chỉ thành viên hội đồng có vai trò Thư ký mới được nhập điểm hội đồng.")
            return redirect(back_url)

        diem_raw = (request.POST.get("diem") or "").strip()
        nhanxet = (request.POST.get("nhanxet") or "").strip() or None

        try:
            diem = float(diem_raw)
        except ValueError:
            messages.error(request, "Điểm không hợp lệ (0–10).")
            return redirect("hd_cham_diem", mada=mada)
        if not (0.0 <= diem <= 10.0):
            messages.error(request, "Điểm phải nằm trong khoảng 0–10.")
            return redirect("hd_cham_diem", mada=mada)

        with connection.cursor() as c:
            # ✅ Cập nhật điểm hội đồng (thư ký nhập)
            c.execute("""
                UPDATE DOAN
                SET DiemHoiDong = %s,
                    NhanXetHoiDong = %s,
                    NgayChamHoiDong = SYSDATETIME()
                WHERE MaDA = %s
            """, [diem, nhanxet, mada])

            # ✅ Lấy toàn bộ điểm của 5 thành viên hội đồng
            c.execute("""
                SELECT DT.Diem
                FROM DIEMTHANHVIEN DT
                JOIN THANHVIENHOIDONG TV ON DT.MaTV = TV.MaTV
                JOIN HOIDONG HD ON HD.MaHD = TV.MaHD
                JOIN DOAN D ON D.MaHD = HD.MaHD
                WHERE D.MaDA = %s
            """, [mada])
            diem_hd_list = [float(r[0]) for r in c.fetchall() if r[0] is not None]

        return redirect(back_url)

    # ======================= XỬ LÝ GET ==========================
    data = {
        "mada": mada_db,
        "tenda": tenda,
        "diem_hd": diem_hd,
        "diem_hdong": diem_hdong,
        "diem_phanbien": diem_phanbien,
        "nx_hd": nx_hd,
        "nx_hdong": nx_hdong,
        "back_url": back_url,
        "is_secretary": is_secretary,
    }
    return render(request, "hd_chamdiem.html", data)


@login_required
def ChamDiemHuongDan(request, mada):
    magv = _get_magv(request.user)
    if not magv:
        return HttpResponseForbidden("Tài khoản chưa liên kết mã giảng viên.")

    # ✅ Chỉ cho phép giảng viên hướng dẫn đồ án này
    if not _is_supervisor(magv, mada):
        return HttpResponseForbidden("Bạn không phải là giáo viên hướng dẫn của đồ án này.")

    # ✅ Chỉ cho chấm khi tiến độ đã duyệt 100%
    with connection.cursor() as c:
        c.execute("""
            SELECT ISNULL(MAX(TienDoPhanTram), 0)
            FROM TIENDO
            WHERE MaDA = %s AND NguoiKiemTra IS NOT NULL
        """, [mada])
        row = c.fetchone()
    approved_max = int(row[0]) if row and row[0] is not None else 0
    if approved_max < 100:
        messages.warning(request, f"Tiến độ hiện tại {approved_max}% — chỉ chấm điểm khi đạt 100%.")
        return redirect(reverse("ds_huong_dan"))

    # ✅ Lấy thông tin đồ án
    with connection.cursor() as c:
        c.execute("""
            SELECT MaDA, TenDA, DiemHuongDan, NhanXetHuongDan, NgayChamHuongDan
            FROM DOAN
            WHERE MaDA = %s
        """, [mada])
        row = c.fetchone()

    if not row:
        messages.error(request, "Không tìm thấy đồ án.")
        return redirect(reverse("ds_huong_dan"))

    mada_db, tenda, diem_hd, nhanxet_hd, ngaycham = row

    # ✅ Xử lý POST: cho phép cập nhật lại điểm (chấm lại)
    if request.method == "POST":
        diem_raw = (request.POST.get("diem") or "").strip()
        nhanxet = (request.POST.get("nhanxet") or "").strip() or None
        try:
            diem = float(diem_raw)
        except ValueError:
            messages.error(request, "Điểm không hợp lệ (0–10).")
            return redirect(reverse("cham_diem_huong_dan", args=[mada]))
        if not (0.0 <= diem <= 10.0):
            messages.error(request, "Điểm phải nằm trong khoảng 0–10.")
            return redirect(reverse("cham_diem_huong_dan", args=[mada]))

        with connection.cursor() as c:
            c.execute("""
                UPDATE DOAN
                SET DiemHuongDan = %s,
                    NhanXetHuongDan = %s,
                    NgayChamHuongDan = SYSDATETIME()
                WHERE MaDA = %s
            """, [diem, nhanxet, mada])

        messages.success(request, "✅ Đã lưu / cập nhật điểm hướng dẫn thành công.")
        return redirect(reverse("ds_huong_dan"))

    # ✅ Render giao diện
    ctx = {
        "mada": mada_db,
        "tenda": tenda,
        "diem_hd": diem_hd,
        "nhanxet_hd": nhanxet_hd,
        "ngaycham": ngaycham,
        "is_locked": False,  # ❌ Không khóa form nữa
    }
    return render(request, "cham_diem_huongdan.html", ctx)


@login_required
def ChamDiemHoiDong(request, mada):
    magv = _get_magv(request.user)
    if not magv:
        return HttpResponseForbidden("Tài khoản chưa liên kết mã giảng viên.")

    # ✅ Kiểm tra giảng viên có trong hội đồng đồ án không
    with connection.cursor() as c:
        c.execute("""
            SELECT TV.MaTV, TV.VaiTro
            FROM THANHVIENHOIDONG TV
            JOIN HOIDONG HD ON TV.MaHD = HD.MaHD
            JOIN DOAN D ON D.MaHD = HD.MaHD
            WHERE D.MaDA = %s AND TV.MaGV = %s
        """, [mada, magv])
        row = c.fetchone()

    if not row:
        return HttpResponseForbidden("Bạn không thuộc hội đồng của đồ án này.")

    ma_tv, vai_tro = row
    is_secretary = (vai_tro == "Thư ký")

    # ✅ Kiểm tra có biên bản bảo vệ chưa
    with connection.cursor() as c:
        c.execute("""
            SELECT TOP 1 MaBB, NgayBaoVe
            FROM BIENBAN
            WHERE MaDA = %s
            ORDER BY NgayBaoVe DESC, MaBB DESC
        """, [mada])
        row = c.fetchone()

    if not row:
        messages.warning(request, "Chưa có biên bản bảo vệ cho đồ án này.")
        return redirect("hoi_dong_cua_toi")

    ma_bb, ngaybaove = row

    # ✅ Lấy điểm hướng dẫn và phản biện trực tiếp từ DOAN
    with connection.cursor() as c:
        c.execute("""
            SELECT DiemHuongDan, DiemPhanBien
            FROM DOAN
            WHERE MaDA = %s
        """, [mada])
        row = c.fetchone()
    diem_huongdan, diem_phanbien = (row if row else (None, None))

    # ✅ Lấy danh sách thành viên hội đồng + điểm từng người
    with connection.cursor() as c:
        c.execute("""
            SELECT TV.MaTV, GV.HoTen, TV.VaiTro, DT.Diem
            FROM THANHVIENHOIDONG TV
            JOIN GIANGVIEN GV ON GV.MaGV = TV.MaGV
            JOIN HOIDONG HD ON HD.MaHD = TV.MaHD
            JOIN DOAN D ON D.MaHD = HD.MaHD
            LEFT JOIN DIEMTHANHVIEN DT ON DT.MaTV = TV.MaTV AND DT.MaBB = %s
            WHERE D.MaDA = %s
            ORDER BY 
                CASE TV.VaiTro
                    WHEN N'Chủ tịch' THEN 1
                    WHEN N'Thư ký' THEN 2
                    ELSE 3
                END
        """, [ma_bb, mada])
        thanhviens = dictfetchall(c)

    # ✅ Nếu POST → lưu điểm hội đồng
    if request.method == "POST":
        if not is_secretary:
            return HttpResponseForbidden("Chỉ thư ký được phép nhập điểm hội đồng.")

        with connection.cursor() as c:
            for tv in thanhviens:
                field = f"diem_{tv['MaTV']}"
                val = request.POST.get(field)
                if not val:
                    continue
                try:
                    diem = float(val)
                except ValueError:
                    continue
                if not (0 <= diem <= 10):
                    continue

                c.execute("""
                    IF EXISTS (SELECT 1 FROM DIEMTHANHVIEN WHERE MaTV=%s AND MaBB=%s)
                        UPDATE DIEMTHANHVIEN SET Diem=%s WHERE MaTV=%s AND MaBB=%s;
                    ELSE
                        INSERT INTO DIEMTHANHVIEN (MaTV, MaBB, Diem)
                        VALUES (%s, %s, %s);
                """, [tv["MaTV"], ma_bb, diem, tv["MaTV"], ma_bb, tv["MaTV"], ma_bb, diem])

        messages.success(request, "✅ Đã lưu điểm hội đồng thành công.")
        return redirect("hoi_dong_cua_toi")

    # ✅ Trả dữ liệu ra template
    return render(request, "cham_diem_hoi_dong.html", {
        "thanhviens": thanhviens,
        "mada": mada,
        "ngaybaove": ngaybaove,
        "is_secretary": is_secretary,
        "diem_huongdan": diem_huongdan,
        "diem_phanbien": diem_phanbien,
    })


@login_required
def DanhSachPhanBien(request):
    magv = _get_magv(request.user)
    if not magv:
        return HttpResponseForbidden("Tài khoản chưa liên kết mã giảng viên.")

    q = (request.GET.get("q") or "").strip()
    params = [magv]
    where = ["HDD.MaGV = %s"]  # ✅ chỉ cần phân công là được chấm

    if q:
        like = f"%{q}%"
        where.append("(D.TenDA LIKE %s OR HV.HoTen LIKE %s)")
        params += [like, like]

    where_sql = " AND ".join(where)

    with connection.cursor() as c:
        c.execute(f"""
            SELECT
                D.MaDA, 
                D.TenDA, 
                D.LinhVuc, 
                D.TrangThai,
                HV.HoTen AS TenHV,
                HD.TenHD, 
                HD.MaHD,
                BB.MaBB, 
                BB.NgayBaoVe,
                ISNULL((
                    SELECT MAX(TienDoPhanTram)
                    FROM TIENDO
                    WHERE MaDA = D.MaDA AND NguoiKiemTra IS NOT NULL
                ), 0) AS TienDo,       -- ✅ Thêm tiến độ
                D.DiemPhanBien         -- ✅ Lấy điểm phản biện
            FROM HUONGDANDOAN HDD
            JOIN DOAN D ON D.MaDA = HDD.MaDA
            LEFT JOIN (
                SELECT DK.MaDA, HV.HoTen
                FROM DANGKY DK
                JOIN HOCVIEN HV ON HV.MaHV = DK.MaHV
                WHERE DK.TrangThai = 1
            ) AS HV ON HV.MaDA = D.MaDA
            LEFT JOIN HOIDONG HD ON D.MaHD = HD.MaHD
            OUTER APPLY (
                SELECT TOP 1 MaBB, NgayBaoVe
                FROM BIENBAN BB
                WHERE BB.MaDA = D.MaDA
                ORDER BY NgayBaoVe DESC, MaBB DESC
            ) AS BB
            WHERE HDD.MaGV = %s
            ORDER BY D.MaDA DESC
        """, [magv])
        rows = dictfetchall(c)


    return render(request, "phanbien_list.html", {"rows": rows, "q": q})



@login_required
def ChamDiemPhanBien(request, mada):
    magv = _get_magv(request.user)
    if not magv:
        return HttpResponseForbidden("Tài khoản chưa liên kết mã giảng viên.")

    # ✅ Kiểm tra giảng viên có được phân công phản biện không
    with connection.cursor() as c:
        c.execute("""
            SELECT COUNT(*) 
            FROM HUONGDANDOAN
            WHERE MaGV = %s AND MaDA = %s
        """, [magv, mada])
        is_assigned = c.fetchone()[0] > 0

    if not is_assigned:
        return HttpResponseForbidden("Bạn không được phân công phản biện đồ án này.")

    # ✅ Kiểm tra tiến độ của đồ án
    with connection.cursor() as c:
        c.execute("""
            SELECT ISNULL(MAX(TienDoPhanTram), 0)
            FROM TIENDO
            WHERE MaDA = %s AND NguoiKiemTra IS NOT NULL
        """, [mada])
        row = c.fetchone()
        percent_done = int(row[0]) if row else 0

    if percent_done < 100:
        messages.warning(request, f"Tiến độ hiện tại {percent_done}% — chỉ có thể chấm điểm phản biện khi đạt 100%.")
        return redirect(reverse("ds_phan_bien"))

    # ✅ Lấy điểm phản biện hiện tại (nếu có)
    with connection.cursor() as c:
        c.execute("SELECT DiemPhanBien FROM DOAN WHERE MaDA = %s", [mada])
        row = c.fetchone()
        diem_pb = row[0] if row else None

    # ✅ POST — lưu điểm phản biện
    if request.method == "POST":
        diem_raw = (request.POST.get("diem") or "").strip()
        try:
            diem = float(diem_raw)
        except (TypeError, ValueError):
            messages.error(request, "Điểm không hợp lệ (0–10).")
            return redirect(reverse("cham_diem_phan_bien", args=[mada]))

        if not (0.0 <= diem <= 10.0):
            messages.error(request, "Điểm phải nằm trong khoảng 0–10.")
            return redirect(reverse("cham_diem_phan_bien", args=[mada]))

        with connection.cursor() as c:
            # ✅ Cập nhật trực tiếp điểm phản biện vào bảng DOAN
            c.execute("""
                UPDATE DOAN
                SET DiemPhanBien = %s
                WHERE MaDA = %s
            """, [diem, mada])

        messages.success(request, "✅ Đã lưu điểm phản biện thành công.")
        return redirect(reverse("ds_phan_bien"))

    # ✅ GET — hiển thị form nhập điểm
    ctx = {
        "mada": mada,
        "diem_pb": diem_pb,
        "percent_done": percent_done,
        "can_score": percent_done >= 100,
    }
    return render(request, "cham_diem_phan_bien.html", ctx)

def contact(request):
    return render(request, 'registration/contact.html')

def export_doan_giangvien(request, magv):
    giangvien = Giangvien.objects.get(magv=magv)
    doan_list = Doan.objects.filter(magv=giangvien, trangthai=0).order_by('tenda')

    template_path = 'doan_theo_gv.html'
    context = {
        'giangvien': giangvien,
        'doan_list': doan_list,
        'ngay_in': timezone.now().strftime("%d/%m/%Y")
    }

    template = get_template(template_path)
    html_content = template.render(context)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="DoAn_GiangVien_{giangvien.magv}.pdf"'

    HTML(string=html_content, base_url=request.build_absolute_uri()).write_pdf(response)
    return response