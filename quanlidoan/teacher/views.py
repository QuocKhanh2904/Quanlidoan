from django.shortcuts import render, redirect
from datetime import date, datetime
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from .models import *

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


def get_magv(request):
    """
    Ưu tiên map theo email → GIANGVIEN.Email
    Fallback: session hoặc querystring 'magv' (cho dev).
    """
    user = getattr(request, "user", None)

    # 1) map theo email đăng nhập
    if user and user.is_authenticated and user.email:
        with connection.cursor() as c:
            # TOP 1 cho SQL Server
            c.execute("SELECT TOP 1 MaGV FROM GIANGVIEN WHERE LOWER(Email) = LOWER(%s)", [user.email])
            row = c.fetchone()
            if row:
                return row[0]

    # 2) fallback: session (tự set khi login hoặc tạm thời)
    magv = request.session.get("magv")
    if magv:
        return magv

    # 3) fallback: ?magv=... (chỉ nên dùng cho dev/test)
    magv_qs = request.GET.get("magv")
    return int(magv_qs) if magv_qs else None


def TienDo_DoAn(request, mada):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                D.MaDA, D.TenDA, D.LinhVuc, D.MoTa, D.NgayGui, D.TrangThai,
                G.HoTen AS TenGV,
                ISNULL(AVG(T.TienDoPhanTram), 0) AS TienDoTB
            FROM DOAN D
            LEFT JOIN GIANGVIEN G ON G.MaGV = D.MaGV
            LEFT JOIN TIENDO T ON T.MaDA = D.MaDA
            WHERE D.MaDA = %s
            GROUP BY D.MaDA, D.TenDA, D.LinhVuc, D.MoTa, D.NgayGui, D.TrangThai, G.HoTen
        """, [mada])
        da = dictfetchall(cursor)
    if not da:
        return redirect("danh_sach_do_an")
    da = da[0]

    # Lấy lịch sử tiến độ
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT MaTD, MoTaCongViec, TienDoPhanTram, NgayCapNhat, NguoiKiemTra
            FROM TIENDO
            WHERE MaDA = %s
            ORDER BY NgayCapNhat DESC, MaTD DESC
        """, [mada])
        tiendos = dictfetchall(cursor)

    ctx = {"da": da, "tiendos": tiendos}
    return render(request, "tiendo_do_an.html", ctx)

def DanhSachDoAn(request):
    magv = request.user.giangvien.magv

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                D.MaDA      AS mada,
                D.TenDA     AS tenda,
                D.LinhVuc   AS linhvuc,
                D.TrangThai AS trangthai,
                D.MoTa      AS mota,
                D.NgayGui   AS ngaygui,
                D.MaGV      AS magv,
                G.HoTen     AS giangvien,
                ISNULL(Tlatest.TienDoPhanTram, 0) AS tiendo,
                Tlatest.NgayCapNhat AS ngaytiendo
            FROM DOAN D
            LEFT JOIN GIANGVIEN G ON D.MaGV = G.MaGV
            OUTER APPLY (
                SELECT TOP 1 T.TienDoPhanTram, T.NgayCapNhat
                FROM TIENDO T
                WHERE T.MaDA = D.MaDA
                ORDER BY T.NgayCapNhat DESC, T.MaTD DESC
            ) AS Tlatest
            WHERE D.MaGV = %s
            ORDER BY D.NgayGui DESC, D.MaDA DESC;
        """, [magv])
        doans = dictfetchall(cursor)

    # 🧩 Thống kê
    tong_so_do_an = len(doans)
    so_dang_thuc_hien = sum(1 for d in doans if str(d["trangthai"]) in {"2", "3"})
    so_hoan_thanh = sum(1 for d in doans if str(d["trangthai"]) == "4")
    so_bao_ve = sum(1 for d in doans if str(d["trangthai"]) == "5")

    ctx = {
        "doans": doans,
        "tong_so_do_an": tong_so_do_an,
        "so_dang_thuc_hien": so_dang_thuc_hien,
        "so_hoan_thanh": so_hoan_thanh,
        "so_bao_ve": so_bao_ve,
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
    if request.method == "POST":
        tenda    = request.POST.get("tenda", "").strip()
        linhvuc  = request.POST.get("linhvuc", "").strip() or None
        trangthai = request.POST.get("trangthai") or None
        soluong  = request.POST.get("soluong") or None
        mota     = request.POST.get("mota", "").strip() or None
        ngaybd   = _parse_date(request.POST.get("ngaybd"))
        ngaykt   = _parse_date(request.POST.get("ngaykt"))
        ngaygui  = _parse_date(request.POST.get("ngaygui"))   # CHO SỬA cả NgayGui
        magv     = request.POST.get("magv") or None

        if not tenda:
            # trả lại form với thông báo lỗi + dữ liệu đã nhập
            form = request.POST.copy()
            form["mada"] = mada
            return render(request, "sua_do_an.html", {
                "error": "Tên đồ án là bắt buộc.",
                "doan": form
            })

        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE DOAN
                SET TenDA=%s, LinhVuc=%s, TrangThai=%s, SoLuongToiDa=%s,
                    NgayGui=%s, MoTa=%s, NgayBD=%s, NgayKT=%s, MaGV=%s
                WHERE MaDA=%s
            """, [tenda, linhvuc, trangthai, soluong, ngaygui, mota, ngaybd, ngaykt, magv, mada])

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
    return render(request, "sua_do_an.html", {"doan": doan})

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
