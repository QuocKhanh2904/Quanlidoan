from django.utils import timezone
import json
from django.shortcuts import render, redirect
from django.http import  JsonResponse
from .models import *
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.http import HttpResponseForbidden

# Create your views here.
@login_required
def home(request):
    if not hasattr(request.user, 'hocvien'):
        return HttpResponseForbidden("Bạn không có quyền truy cập")
    
    hocvien = request.user.hocvien
    context = {'hocvien': hocvien}
    return render(request, 'app/home.html', context)

def change_password(request):
    if request.method == 'POST':
        current_password = request.POST.get('currentPassword')
        new_password = request.POST.get('newPassword')
        confirm_password = request.POST.get('confirmNewPassword')

        user = request.user
        if not user.check_password(current_password):
            return JsonResponse({'status': 'danger', 'message': 'Mật khẩu hiện tại không đúng.'})
            
        if new_password != confirm_password:
            return JsonResponse({'status':'danger', 'message': 'Mật khẩu mới không khớp.'})

        user.set_password(new_password)
        user.save()
        update_session_auth_hash(request, user)

        return JsonResponse({'status':'success', 'message':'Mật khẩu đã được thay đổi thành công'})

def topic(request):
    userTopic = Doan.objects.filter(dangky__mahv=request.user.hocvien).first() if request.user.is_authenticated else None

    tenda = request.GET.get('tenda', '').strip()
    linhvuc = request.GET.get('linhvuc', '').strip()
    doans = Doan.objects.all()
    topics = Doan.doan_list(mada=None,tenda=tenda, linhvuc=linhvuc)
    fields = doans.values_list('linhvuc', flat=True).distinct()
    context = {
        'topics': topics,
        'fields': fields,
        'userTopic': userTopic,
    }
    return render(request, 'app/topic.html', context)

def register_topic(request):
    topic_id = request.GET.get('topic_id')
    # Handle the registration logic here
    gvhds = Huongdandoan.gvhd_list(mada=topic_id)
    hvdk = Dangky.hvdk_list(mada=topic_id)
    topic = Doan.doan_list(mada=topic_id)[0]
    context = {'topic': topic, 'gvhds':gvhds, 'hvdk':hvdk}
    return render(request, 'app/register_topic.html', context)

def regist_topic(request):
    data = json.loads(request.body)
    topicId = data.get('topicId')
    user = request.user.hocvien.mahv
    try:
        Dangky.dangky_create_raw(mada=topicId, mahv=user, trangthai='1', ngaydk=timezone.now())
        return JsonResponse({"status": "success", "message": "Đăng ký thành công!"})
    except Exception as e:
        return JsonResponse({"status": "error", "message": f"Đăng ký thất bại: {str(e)}"})

def report_progress(request):
    doans = Dangky.dangky_list(mahv=request.user.hocvien.mahv)
    doan = doans[0] if doans else None
    tiendos = Tiendo.tiendo_list(mada=doan['mada']) if doan else []
    context = {'doan': doan, 'tiendos': tiendos}
    return render(request, 'app/report_progress.html', context)

def submit_report(request):
    if request.method == 'POST':
        mota = request.POST.get('motacongviec', '').strip()
        filebaocao = request.FILES.get('filebaocao')
        user = request.user.hocvien
        doan = Dangky.dangky_list(mahv=user.mahv)[0]
        
        if doan:
            try:
                Tiendo.tiendo_create_raw(mada=doan['mada'], file=filebaocao, mota=mota, ngaycapnhat=timezone.now())
                return JsonResponse({"status": "success", "message": "Báo cáo đã được gửi!"})
            except Exception as e:
                return JsonResponse({"status": "error", "message": f"Gửi báo cáo thất bại: {str(e)}"})
        else:
            return JsonResponse({"status": "error", "message": "Bạn chưa đăng ký đề tài nào."})

def submit_topic(request):
    doans = Dangky.dangky_list(mahv=request.user.hocvien.mahv)
    doan = doans[0] if doans else None
    context = {'doan': doan}
    return render(request, 'app/submit_topic.html', context)

def update_topic(request):
    action = request.POST.get('action')
    if action == 'submit':
        filedoan = request.FILES.get('filedoan')
        doan = Doan.objects.filter(dangky__mahv=request.user.hocvien).first()
        if doan:
            try:
                doan.file = filedoan
                doan.save()
                return JsonResponse({"status": "success", "message": "Đã nộp đồ án thành công!"})
            except Exception as e:
                return JsonResponse({"status": "error", "message": f"Đã xảy ra lỗi: {str(e)}"})
        else:
            return JsonResponse({"status": "error", "message": "Bạn chưa đăng ký đề tài nào."})

def result(request):
    mahv = request.user.hocvien.mahv
    diemthanhvien = Diemthanhvien.diemthanhvien_list(mahv)
    ketquas = Ketquabaove.ketqua_list(mahv)
    ketqua = ketquas[0] if ketquas else None
    thongtindoans = Dangky.dangky_list(mahv)
    thongtindoan = thongtindoans[0] if thongtindoans else None
    context = {'diemthanhvien': diemthanhvien, 'thongtindoan': thongtindoan, 'ketqua': ketqua}
    return render(request, 'app/result.html', context)

def contact(request):
    return render(request, 'app/contact.html')
