from django.shortcuts import render, get_object_or_404
from .models import *
from django.http import JsonResponse
from datetime import datetime
import json

# Create your views here.
def home(request):
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

    context = {'doans': doans, 'hoidongs':hoidongs, 'tenda_selected': tenda,'trangthai_selected': trangthai,'mahd_selected': mahd,}
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
        try:
            Giangvien.giangvien_create_raw(hoten=hoten, email=email, sdt=sdt, donvi=donvi)
            return JsonResponse({'status':'success', 'message':'Thêm giảng viên thành công'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

def giangvien_update(request):
    if request.method == 'POST':
        magv = request.POST.get('magv')
        tengv = request.POST.get('hoten')
        email = request.POST.get('email') or None
        sdt = request.POST.get('sodienthoai') or None
        donvi = request.POST.get('donvi') or None
        try:
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
        try:
            Hocvien.hocvien_create_raw(hoten=hoten, email=email, sdt=sdt, lop=lop)
            return JsonResponse({'status':'success', 'message':'Thêm học viên thành công'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

def hocvien_update(request):
    if request.method == 'POST':
        mahv = request.POST.get('mahv')
        tenhv = request.POST.get('hoten')
        email = request.POST.get('email') or None
        sdt = request.POST.get('sodienthoai') or None
        lop = request.POST.get('lop') or None
        try:
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
        magv = request.POST.get('magv') 
        vaitro = request.POST.get('vaitro') 
        try:
            Hoidong.hoidong_update_raw(mahd=mahd, tenhd=tenhd, ngaythanhlap=ngaythanhlap, ngayketthuc=ngayketthuc, linhvuc=linhvuc)
            # Thanhvienhoidong.thanhvienhoidong_create_raw(vaitro=vaitro,magv=magv,mahd=mahd)
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