from django.utils import timezone
import json
from django.db.models import F
from django.contrib import messages
from django.shortcuts import render, redirect
from django.http import  JsonResponse
from django.contrib.auth.forms import PasswordChangeForm
from .models import *
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout, update_session_auth_hash
from django.http import HttpResponseForbidden

# Create your views here.
@login_required
def home(request):
    if not hasattr(request.user, 'hocvien'):
        return HttpResponseForbidden("Bạn không có quyền truy cập")
    
    hocvien = request.user.hocvien
    context = {'hocvien': hocvien}
    return render(request, 'app/home.html', context)

def logout_view(request):
    logout(request)
    return redirect('login')

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

    topics = Doan.objects.all()
    fields = topics.values_list('linhvuc', flat=True).distinct()

    if tenda:
        topics = topics.filter(tenda__icontains=tenda)
    if linhvuc:
        topics = topics.filter(linhvuc__iexact=linhvuc)
    context = {
        'topics': topics,
        'fields': fields,
        'userTopic': userTopic,
    }
    return render(request, 'app/topic.html', context)

def register_topic(request):
    topic_id = request.GET.get('topic_id')
    # Handle the registration logic here
    topic = (
    Doan.objects.filter(mada=topic_id)
    .values("mada", "tenda", "linhvuc", "magv__hoten", "mota")
    .first()
    if topic_id else None
)
    context = {'topic': topic}
    return render(request, 'app/register_topic.html', context)

def regist_topic(request):
    data = json.loads(request.body)
    topicId = data['topicId']
    action = data['action']
    topic = Doan.objects.get(mada=topicId)
    user = request.user
    if action == 'register':
        try:
            Dangky.objects.create(
                mada=topic,
                mahv=user.hocvien,
                ngaydk=timezone.now(),
                trangthai='1'
            )
            return JsonResponse({"status": "success", "message": "Đăng ký thành công!"})
        except Exception as e:
            return JsonResponse({"status": "error", "message": f"Đăng ký thất bại: {str(e)}"})

def report_progress(request):
    user = request.user
    doan = Doan.objects.filter(dangky__mahv=user.hocvien).first()
    tiendos = Tiendo.objects.filter(mada=doan).order_by('ngaycapnhat') if doan else []
    context = {'doan': doan, 'tiendos': tiendos}
    return render(request, 'app/report_progress.html', context)

def submit_report(request):
    mota = request.POST.get('motacongviec', '').strip()
    filebaocao = request.FILES.get('filebaocao')
    user = request.user
    doan = Doan.objects.filter(dangky__mahv=user.hocvien).first()
    
    if doan:
        try:
            Tiendo.objects.create(
                mada=doan,
                file=filebaocao,
                motacongviec=mota,
                ngaycapnhat=timezone.now()
            )
            return JsonResponse({"status": "success", "message": "Báo cáo đã được gửi!"})
        except Exception as e:
            return JsonResponse({"status": "error", "message": f"Gửi báo cáo thất bại: {str(e)}"})
    else:
        return JsonResponse({"status": "error", "message": "Bạn chưa đăng ký đề tài nào."})

def submit_topic(request):
    doan = Doan.objects.filter(dangky__mahv=request.user.hocvien).first()
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
    user = request.user
    diemthanhvien = (Diemthanhvien.objects
                        .filter(mabb__mahv=user.hocvien.mahv)  
                        .select_related("matv__magv")    
                        .values(
                            hoten=F("matv__magv__hoten"),        
                            vaitro=F("matv__vaitro"),           
                            diemso=F("diem")
                        )
    )
    ketqua = Ketquabaove.objects.filter(mabb__mahv=user.hocvien).first()
    thongtindoan = (
    Dangky.objects
        .filter(mahv=user.hocvien.mahv)
        .select_related("mahv", "mada__mahd")
        .values(
            hoten=F("mahv__hoten"), 
            tenda=F("mada__tenda"),
            tenhd=F("mada__mahd__tenhd"), 
        ).first()
    )
    context = {'diemthanhvien': diemthanhvien, 'thongtindoan': thongtindoan, 'ketqua': ketqua}
    return render(request, 'app/result.html', context)

def contact(request):
    return render(request, 'app/contact.html')
