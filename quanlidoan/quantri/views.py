from django.shortcuts import render
from .models import *
from django.http import JsonResponse, HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
import json

# Create your views here.
@login_required
def home(request):
    if not request.user.is_staff and not request.user.is_superuser:
        return HttpResponseForbidden("Bạn không có quyền truy cập vào trang của admin.")
    return render(request,'home.html')

def normalize(value):
    value = value.strip() if value else None
    return value if value else None

def manage_project(request):
    tenda = normalize(request.GET.get('tenda'))
    trangthai = normalize(request.GET.get('trangthai'))
    mahd = normalize(request.GET.get('mahd'))

    if trangthai: trangthai=int(trangthai)
    if mahd: mahd=int(mahd)

    doans = Doan.doan_list(tenda,trangthai,mahd)
    hoidongs = Hoidong.hoidong_list()

    context = {'doans': doans, 'hoidongs':hoidongs, 'tenda_selected': tenda,'trangthai_selected': trangthai,'mahd_selected': mahd}
    return render(request,'manage_project.html', context)

def doan_create(request):
    if request.method == "POST":
        tenda = request.POST.get('tenda')
        trangthai = request.POST.get('trangthai') or None
        soluongtoida = request.POST.get('soluongtoida') or None
        ngaybd = request.POST.get('ngaybd')
        ngaykt = request.POST.get('ngaykt')
        linhvuc = request.POST.get('linhvuc')
        mota = request.POST.get('mota')
        mahd = request.POST.get('mahd') or None
        file = request.FILES.get('file') or None
        try:
            Doan.doan_create_raw(
                tenda=tenda,
                trangthai=trangthai,
                soluongtoida=soluongtoida,
                ngaybd=ngaybd,
                ngaykt=ngaykt,
                linhvuc=linhvuc,
                mota=mota,
                mahd=mahd,
                file=file
            )
            return JsonResponse({'status': 'success', 'message': 'Thêm đồ án thành công'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    
def doan_update(request):
    if request.method == "POST":
        mada = request.POST.get('mada')
        tenda = request.POST.get('tenda')
        trangthai = request.POST.get('trangthai') or None
        soluongtoida = request.POST.get('soluongtoida') or None
        ngaybd = request.POST.get('ngaybd')
        ngaykt = request.POST.get('ngaykt')
        linhvuc = request.POST.get('linhvuc')
        mota = request.POST.get('mota') or None
        mahd = request.POST.get('mahd') or None
        file = request.FILES.get('file') or None
        try:
            Doan.doan_update_raw(
                mada=mada,
                tenda=tenda,
                trangthai=trangthai,
                soluongtoida=soluongtoida,
                ngaybd=ngaybd,
                ngaykt=ngaykt,
                linhvuc=linhvuc,
                mota=mota,
                mahd=mahd,
                file=file
            )
            return JsonResponse({'status': 'success', 'message': 'Cập nhật đồ án thành công'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

def doan_delete(request):
    if request.method == "POST":
        mada = request.POST.get('mada')
        file = request.POST.get('file')
        try:
            Doan.doan_delete_raw(mada=mada, file=file)
            return JsonResponse({'status': 'success', 'message': 'Xóa đồ án thành công'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
            
def manage_giangvien(request):
    hoten = request.GET.get('hoten')
    email = request.GET.get('email')
    sdt = request.GET.get('sdt')
    donvi = request.GET.get('donvi')
    sort = request.GET.get('sort')
    
    sort_field, sort_dir = None, 'ASC'
    if sort == 'doan_asc':
        sort_field, sort_dir = 'doan', 'ASC'
    elif sort == 'doan_desc':
        sort_field, sort_dir = 'doan', 'DESC'
    elif sort == 'hoidong_asc':
        sort_field, sort_dir = 'hoidong', 'ASC'
    elif sort == 'hoidong_desc':
        sort_field, sort_dir = 'hoidong', 'DESC'

    giangviens = Giangvien.giangvien_list(hoten=hoten, email=email, sdt=sdt, donvi=donvi, sort_field=sort_field, sort_dir=sort_dir)
    context = {'giangviens':giangviens}
    return render(request,'manage_giangvien.html', context)

def giangvien_create(request):
    if request.method == 'POST':
        hoten = request.POST.get('hoten')
        email = request.POST.get('email') or None
        sdt = request.POST.get('sodienthoai') or None
        donvi = request.POST.get('donvi') or None
        username = request.POST.get('username')
        password = request.POST.get('password')
        if User.objects.filter(username=username).exists():
                return JsonResponse({'status': 'error', 'message': 'Tên đăng nhập đã tồn tại'})
        user = User.objects.create_user(username=username, password=password)

        try:
            Giangvien.giangvien_create_raw(hoten=hoten, email=email, sdt=sdt, donvi=donvi, userid=user.id)
            return JsonResponse({'status':'success', 'message':'Thêm giảng viên thành công'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

def giangvien_update(request):
    if request.method == 'POST':
        magv = request.POST.get('magv')
        userid = request.POST.get('userid')
        tengv = request.POST.get('hoten')
        email = request.POST.get('email') or None
        sdt = request.POST.get('sodienthoai') or None
        donvi = request.POST.get('donvi') or None
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = User.objects.filter(id=userid).first()
        try:
            if user:
                if username:
                    if User.objects.filter(username=username).exclude(id=user.id).exists():
                        return JsonResponse({'status': 'error', 'message': 'Tên đăng nhập đã tồn tại'})
                    user.username = username
                if password:
                        user.set_password(password)
                user.save()
            Giangvien.giangvien_update_raw(magv=magv, tengv=tengv, email=email, sdt=sdt, donvi=donvi)
            return JsonResponse({'status':'success', 'message':'Cập nhật giảng viên thành công'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

def giangvien_delete(request):
    if request.method == "POST":
        magv = json.loads(request.body)['magv']
        try:
            Giangvien.giangvien_delete_raw(magv=magv)
            return JsonResponse({'status': 'success', 'message': 'Xóa giảng viên thành công'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

def manage_hocvien(request):
    hocviens = Hocvien.objects.all()
    context = {'hocviens': hocviens}
    return render(request,'manage_hocvien.html', context)

def hocvien_create(request):
    if request.method == 'POST':
        hoten = request.POST.get('hoten')
        email = request.POST.get('email') or None
        sdt = request.POST.get('sodienthoai') or None
        lop = request.POST.get('lop') or None
        username = request.POST.get('username')
        password = request.POST.get('password')
        if User.objects.filter(username=username).exists():
                return JsonResponse({'status': 'error', 'message': 'Tên đăng nhập đã tồn tại'})
        user = User.objects.create_user(username=username, password=password)
        try:
            Hocvien.hocvien_create_raw(hoten=hoten, email=email, sdt=sdt, lop=lop, userid=user.id)
            return JsonResponse({'status':'success', 'message':'Thêm học viên thành công'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

def hocvien_update(request):
    if request.method == 'POST':
        mahv = request.POST.get('mahv')
        userid = request.POST.get('userid')
        tenhv = request.POST.get('hoten')
        email = request.POST.get('email') or None
        sdt = request.POST.get('sodienthoai') or None
        lop = request.POST.get('lop') or None
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = User.objects.filter(id=userid).first()
        try:
            if user:
                if username:
                    if User.objects.filter(username=username).exclude(id=user.id).exists():
                        return JsonResponse({'status': 'error', 'message': 'Tên đăng nhập đã tồn tại'})
                    user.username = username
                if password:
                        user.set_password(password)
                user.save()
            Hocvien.hocvien_update_raw(mahv=mahv, tenhv=tenhv, email=email, sdt=sdt, lop=lop)
            return JsonResponse({'status':'success', 'message':'Cập nhật học viên thành công'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

def hocvien_delete(request):
    if request.method == "POST":
        mahv = json.loads(request.body)['mahv']
        try:
            Hocvien.hocvien_delete_raw(mahv=mahv)
            return JsonResponse({'status': 'success', 'message': 'Xóa học viên thành công'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
        
def manage_hoidong(request):
    hoidongs = Hoidong.objects.all()
    context = {'hoidongs': hoidongs}
    return render(request,'manage_hoidong.html', context)

def hoidong_create(request):
    if request.method == 'POST':
        tenhd = request.POST.get('tenhd')
        ngaythanhlap = request.POST.get('ngaythanhlap') or None
        ngayketthuc = request.POST.get('ngayketthuc') or None
        linhvuc = request.POST.get('linhvuc') or None
        try:
            Hoidong.hoidong_create_raw(tenhd=tenhd, ngaythanhlap=ngaythanhlap, ngayketthuc=ngayketthuc, linhvuc=linhvuc)
            return JsonResponse({'status':'success', 'message':'Thêm hội đồng thành công'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

def hoidong_update(request):
    if request.method == 'POST':
        mahd = request.POST.get('mahd')
        tenhd = request.POST.get('tenhd')
        ngaythanhlap = request.POST.get('ngaythanhlap') or None
        ngayketthuc = request.POST.get('ngayketthuc') or None
        linhvuc = request.POST.get('linhvuc') or None
        try:
            Hoidong.hoidong_update_raw(mahd=mahd, tenhd=tenhd, ngaythanhlap=ngaythanhlap, ngayketthuc=ngayketthuc, linhvuc=linhvuc)
            return JsonResponse({'status':'success', 'message':'Cập nhật hội đồng thành công'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

def hoidong_delete(request):
    if request.method == "POST":
        mahd = json.loads(request.body)['mahd']
        try:
            Hoidong.hoidong_delete_raw(mahd=mahd)
            return JsonResponse({'status': 'success', 'message': 'Xóa hội đồng thành công'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

def thanhvienhoidong_create(request):
    if request.method == 'POST':
        vaitro = request.POST.get('vaitro')
        magv = request.POST.get('magv') 
        mahd = request.POST.get('mahd') 
        try:
            Thanhvienhoidong.thanhvienhoidong_create_raw(vaitro=vaitro, magv=magv, mahd=mahd)
            return JsonResponse({'status':'success', 'message':'Thêm thành viên hội đòng thành công'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
        
def thanhvienhoidong_list(request):
    try:
        mahd = request.GET.get('mahd')
        if not mahd:
            return JsonResponse({'status': 'error', 'message': 'Thiếu mã hội đồng'})

        members = Thanhvienhoidong.objects.filter(mahd=mahd).select_related('magv')

        data = [
            {
                'matv': tv.matv,
                'hoten': tv.magv.hoten if tv.magv else '',
                'vaitro': tv.vaitro or ''
            }
            for tv in members
        ]
        return JsonResponse({'status': 'success', 'data': data})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})

def thanhvienhoidong_delete(request):
    if request.method == "POST":
        matv = json.loads(request.body)['matv']
        try:
            Thanhvienhoidong.thanhvienhoidong_delete_raw(matv=matv)
            return JsonResponse({'status': 'success', 'message': 'Xóa thành viên hội đồng thành công'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
        
def manage_tiendo(request):
    mada = request.GET.get('mada')
    doans = Doan.objects.all()
    so_luong_0_35 = Tiendo.thongke_tiendo(0, 35)
    so_luong_36_70 = Tiendo.thongke_tiendo(36, 70)
    so_luong_71_100 = Tiendo.thongke_tiendo(71, 100)
    if mada:
        tiendos = Tiendo.objects.filter(mada__mada=mada).select_related('mada').order_by('-ngaycapnhat')
    else:
        tiendos = []
    context = {'tiendos': tiendos, 'doans': doans, 'mada_selected': int(mada) if mada else '', 'td0_35':so_luong_0_35, 'td36_70':so_luong_36_70, 'td71_100':so_luong_71_100}
    return render(request, 'manage_tiendo.html', context)

def tiendo_create(request):
    try:
        mada = request.POST.get("mada")
        motacv = request.POST.get("motacv")
        tiendo = request.POST.get("tiendo")
        nguoikiemtra = request.POST.get("nguoikiemtra")
        file = request.FILES.get("file")
        new_id = Tiendo.tiendo_create_raw(mada=mada, motacv=motacv, tiendo=tiendo, nguoikiemtra=nguoikiemtra, file=file)
        return JsonResponse({'status': 'success', 'message': 'Thêm tiến độ thành công', 'matd': new_id})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})
    
def tiendo_update(request):
    try:
        matd = request.POST.get("matd")
        motacv = request.POST.get("motacv")
        tiendo = request.POST.get("tiendo")
        nguoikiemtra = request.POST.get("nguoikiemtra")
        file = request.FILES.get("file")
        Tiendo.tiendo_update_raw(matd=matd, motacv=motacv, tiendo=tiendo, nguoikiemtra=nguoikiemtra, file=file)
        return JsonResponse({'status': 'success', 'message': 'Cập nhật tiến độ thành công'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})
    
def tiendo_delete(request):
    try:
        data = json.loads(request.body)
        matd = data.get("matd")
        Tiendo.tiendo_delete_raw(matd=matd)
        return JsonResponse({'status': 'success', 'message': 'Xóa tiến độ thành công'})

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})

def tiendo_detail(request, matd):
    try:
        data = list(Tiendo.objects.filter(matd=matd).values(
            'matd', 'motacongviec', 'tiendophantram', 'ngaycapnhat', 
            'nguoikiemtra', 'file', 'mada__tenda'
        ))
        if not data:
            return JsonResponse({'status': 'error', 'message': 'Không tìm thấy tiến độ'})
        return JsonResponse({'status': 'success', 'data': data[0]})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})
    
def manage_phancong(request):
    # --- Lấy dữ liệu lọc từ form GET ---
    tenda = normalize(request.GET.get('tenda'))
    linhvuc = normalize(request.GET.get('linhvuc'))

    # --- Gọi stored procedure sp_DanhSachDoAn_TrangThai2 ---
    with connection.cursor() as cursor:
        if tenda or linhvuc:
            # Nếu có tiêu chí lọc → lọc tại Python (proc này chỉ lấy trạng thái = 2)
            cursor.execute("EXEC sp_DanhSachDoAn_DangChoPhanCong")
            columns = [col[0] for col in cursor.description]
            all_doans = [dict(zip(columns, row)) for row in cursor.fetchall()]
            doans = [
                da for da in all_doans
                if (not tenda or tenda.lower() in (da['tenda'] or '').lower())
                and (not linhvuc or linhvuc.lower() in (da['linhvuc'] or '').lower())
            ]
        else:
            # Nếu không có lọc → lấy toàn bộ
            cursor.execute("EXEC sp_DanhSachDoAn_DangChoPhanCong")
            columns = [col[0] for col in cursor.description]
            doans = [dict(zip(columns, row)) for row in cursor.fetchall()]

    # --- Lấy danh sách giảng viên ---
    giangviens = Giangvien.objects.all()

    # --- Truyền context sang template ---
    context = {
        'doans': doans,
        'giangviens': giangviens,
        'tenda_selected': tenda,
        'linhvuc_selected': linhvuc,
    }

    return render(request, 'manage_phancongdoan.html', context)

# ✅ Phân công giảng viên
def phancongdoan_update(request):
    if request.method == 'POST':
        mada = request.POST.get('mada')
        magv = request.POST.get('magv')

        if not mada or not magv:
            return JsonResponse({'status': 'error', 'message': 'Thiếu thông tin đồ án hoặc giảng viên.'})

        try:
            with connection.cursor() as cursor:
                cursor.execute("EXEC sp_PhanCongGiangVien @MaDA=%s, @MaGV=%s", [mada, magv])
                columns = [col[0] for col in cursor.description]
                result = dict(zip(columns, cursor.fetchone()))
            return JsonResponse(result)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': f'Lỗi: {str(e)}'})
    
    return JsonResponse({'status': 'error', 'message': 'Phương thức không hợp lệ.'})


# ✅ Từ chối đăng ký
def phancongdoan_reject(request):
    if request.method == 'POST':
        mada = request.POST.get('mada')

        if not mada:
            return JsonResponse({'status': 'error', 'message': 'Thiếu mã đồ án.'})
        try:
            with connection.cursor() as cursor:
                cursor.execute("EXEC sp_TuChoiDangKy @MaDA=%s", [int(mada)])
                columns = [col[0] for col in cursor.description]
                result = dict(zip(columns, cursor.fetchone()))
            return JsonResponse(result)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': f'Lỗi: {str(e)}'})

    return JsonResponse({'status': 'error', 'message': 'Phương thức không hợp lệ.'})

def manage_dangky(request):
    mada = request.GET.get('mada')   
    doans = Doan.objects.all()
    lop_list = Hocvien.objects.values_list('lop', flat=True).distinct()
    if mada:
        dangkys = Dangky.objects.filter(mada=mada).select_related('mada').order_by('-ngaydk')
    else:
        dangkys = []
    context = {'dangkys': dangkys, 'doans': doans, 'mada_selected': int(mada) if mada else '', 'lop_list': lop_list,}
    return render(request, 'manage_dangky.html', context)

@require_POST
def dangky_create(request):
    try:
        mada = request.POST.get("mada")
        mahv = request.POST.get("mahv")
        ngaydk = request.POST.get("ngaydk")
        trangthai = request.POST.get("trangthai")
        new_id = Dangky.dangky_create_raw(mada=mada, mahv=mahv, ngaydk=ngaydk, trangthai=trangthai)
        return JsonResponse({'status': 'success', 'message': 'Thêm đăng ký thành công', 'madk': new_id})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})

@require_POST
def dangky_update(request):
    try:
        madk = request.POST.get("madk")
        mada = request.POST.get("mada")
        mahv = request.POST.get("mahv")
        ngaydk = request.POST.get("ngaydk")
        trangthai = request.POST.get("trangthai")
        Dangky.dangky_update_raw(madk=madk, mada=mada, mahv=mahv, ngaydk=ngaydk, trangthai=trangthai)
        return JsonResponse({'status': 'success', 'message': 'Cập nhật đăng ký thành công'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})

@require_POST
def dangky_delete(request):
    try:
        data = json.loads(request.body)
        madk = data.get("madk")
        Dangky.dangky_delete_raw(madk)
        return JsonResponse({'status': 'success', 'message': 'Xóa đăng ký thành công'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})
    
def dangky_detail(request, madk):
    try:
        data = list(Dangky.objects.filter(madk=madk).values(
            'madk', 'mahv__hoten', 'ngaydk', 'trangthai', 
            'mahv', 'mada', 'mada__tenda'
        ))
        if not data:
            return JsonResponse({'status': 'error', 'message': 'Không tìm thấy đăng ký nào'})
        return JsonResponse({'status': 'success', 'data': data[0]})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})
    
def hocvien_by_lop(request):
    try:
        lop = request.GET.get("lop")
        if not lop:
            return JsonResponse({'status': 'error', 'message': 'Thiếu tham số lớp'})

        hocviens = Hocvien.objects.filter(lop=lop).values('mahv', 'hoten')
        data = list(hocviens)

        if not data:
            return JsonResponse({'status': 'error', 'message': 'Không có học viên trong lớp này'})
        return JsonResponse({'status': 'success', 'data': data})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})
    
def manage_baove(request):
    mada = request.GET.get('mada')   
    doans = Doan.objects.all()
    if mada:
        bienbans = Bienban.objects.filter(mada=mada).select_related('mada').order_by('-ngaybaove')
    else:
        bienbans = Bienban.objects.all()
    context = {'bienbans': bienbans, 'doans': doans, 'mada_selected': int(mada) if mada else ''}
    return render(request, 'manage_baove.html', context)

def baove_create(request):
    try:
        mada = request.POST.get("mada")
        mahv = request.POST.get("mahv")
        ngaybaove = request.POST.get("ngaybaove") or timezone.now().date()
        diadiem = request.POST.get("diadiem")
        noidung = request.POST.get("noidung")
        ghichu = request.POST.get("ghichu")
        new_id = Bienban.bienban_create_raw(mada=mada, mahv=mahv, ngaybaove=ngaybaove, diadiem=diadiem, noidung=noidung, ghichu=ghichu)
        return JsonResponse({'status': 'success', 'message': 'Thêm biên bản bảo vệ thành công', 'mabb': new_id})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})
    
def baove_update(request):
    try:
        data = json.loads(request.body)
        mabb = data.get("mabb")
        ngaybaove = data.get("ngaybaove")
        diadiem = data.get("diadiem")
        noidung = data.get("noidung")
        ghichu = data.get("ghichu")
        Bienban.bienban_update_raw(mabb=mabb, ngaybaove=ngaybaove, diadiem=diadiem, noidung=noidung, ghichu=ghichu)
        return JsonResponse({'status': 'success', 'message': 'Cập nhật biên bản thành công'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})

def baove_delete(request):
    try:
        data = json.loads(request.body)
        mabb = data.get("mabb")

        Bienban.bienban_delete_raw(mabb)
        return JsonResponse({'status': 'success', 'message': 'Đã xóa biên bản và dữ liệu liên quan'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})

def dangky_by_doan(request):
    try:
        mada = request.GET.get("mada")
        if not mada:
            return JsonResponse({'status': 'error', 'message': 'Thiếu mã đồ án'})

        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT hv.MaHV, hv.HoTen
                FROM DANGKY dk
                JOIN HOCVIEN hv ON dk.MaHV = hv.MaHV
                WHERE dk.MaDA = %s AND dk.TrangThai = 1
            """, [mada]) 
            rows = cursor.fetchall()

        data = [{'mahv': r[0], 'hoten': r[1]} for r in rows]
        if not data:
            return JsonResponse({'status': 'error', 'message': 'Chưa có học viên đăng ký đồ án này'})
        return JsonResponse({'status': 'success', 'data': data})

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})
    
def baove_detail(request, mabb):
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    bb.MaBB, bb.NgayBaoVe, bb.DiaDiem, bb.NoiDung, bb.GhiChu,
                    hv.MaHV, hv.HoTen, hv.Lop, hv.Email,
                    da.MaDA, da.TenDA
                FROM BIENBAN bb
                JOIN HOCVIEN hv ON bb.MaHV = hv.MaHV
                JOIN DOAN da ON bb.MaDA = da.MaDA
                WHERE bb.MaBB = %s
            """, [mabb])
            bb_row = cursor.fetchone()

            if not bb_row:
                return JsonResponse({'status': 'error', 'message': 'Không tìm thấy biên bản bảo vệ'})

            bienban = {
                'mabb': bb_row[0],
                'ngaybaove': bb_row[1].strftime("%d/%m/%Y") if bb_row[1] else None,
                'diadiem': bb_row[2],
                'noidung': bb_row[3],
                'ghichu': bb_row[4],
                'mahv': bb_row[5],
                'hoten': bb_row[6],
                'lop': bb_row[7],
                'email': bb_row[8],
                'mada': bb_row[9],
                'tenda': bb_row[10],
            }

            cursor.execute("""
                SELECT 
                    tvhd.MaTV, gv.HoTen, tvhd.VaiTro, dtv.Diem
                FROM DIEMTHANHVIEN dtv
                JOIN THANHVIENHOIDONG tvhd ON dtv.MaTV = tvhd.MaTV
                JOIN GIANGVIEN gv ON tvhd.MaGV = gv.MaGV
                WHERE dtv.MaBB = %s
            """, [mabb])
            diem_rows = cursor.fetchall()
            diemtv = [
                {
                    'matv': r[0],
                    'hoten': r[1],
                    'vaitro': r[2],
                    'diem': r[3]
                } for r in diem_rows
            ]

            cursor.execute("""
                SELECT Diem, DanhGia, XepLoai
                FROM KETQUABAOVE
                WHERE MaBB = %s
            """, [mabb])
            kq_row = cursor.fetchone()
            ketqua = {
                'diem': kq_row[0] if kq_row else None,
                'danhgia': kq_row[1] if kq_row else None,
                'xeploai': kq_row[2] if kq_row else None,
            }

        data = {
            'mabb': bienban['mabb'],
            'tenda': bienban['tenda'],
            'hoten': bienban['hoten'],
            'lop': bienban['lop'],
            'email': bienban['email'],
            'ngaybaove': bienban['ngaybaove'],
            'diadiem': bienban['diadiem'],
            'noidung': bienban['noidung'],
            'ghichu': bienban['ghichu'],
            'diemtv': diemtv,
            'ketqua': ketqua,
        }

        return JsonResponse({'status': 'success', 'data': data})

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})
    
def baove_update(request):
    try:
        data = json.loads(request.body)
        mabb = data.get("mabb")
        ngaybaove = data.get("ngaybaove")
        diadiem = data.get("diadiem")
        noidung = data.get("noidung")
        ghichu = data.get("ghichu")
        diemtv = data.get("diemtv", [])

        Bienban.bienban_update_raw( mabb=mabb, ngaybaove=ngaybaove, diadiem=diadiem, noidung=noidung, ghichu=ghichu)
        with connection.cursor() as cursor:
            for tv in diemtv:
                Diemthanhvien.diemthanhvien_update_raw(mabb=mabb, diemtv=diemtv)
        return JsonResponse({'status': 'success', 'message': 'Cập nhật biên bản và điểm thành viên thành công'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})

def contact(request):
    return render(request, 'contact.html')

def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html = template.render(context_dict)
    response = HttpResponse(content_type='application/pdf')
    pisa.CreatePDF(html, dest=response)
    return response

def export_doan_theo_hoidong(request, mahd):
    try:
        hoidong = Hoidong.objects.get(mahd=mahd)
        doan_list = Doan.objects.filter(mahd=hoidong)

        context = {
            'hoidong': hoidong,
            'doan_list': doan_list,
            'ngay_in': timezone.now().strftime("%d/%m/%Y"),
        }
        return render_to_pdf('pdf/DsDoAnBaoVe.html', context)

    except Hoidong.DoesNotExist:
        return HttpResponse("Hội đồng không tồn tại.", status=404)