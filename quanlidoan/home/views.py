from django.utils import timezone
import json
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from .models import *

# Create your views here.

def home(request):
    return render(request, 'app/home.html')

def topic(request):
    topics = Doan.get_Doan('1')
    context = {
        'topics': topics,
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
    # Handle the registration logic here
    user = request.user
    
    if action == 'register':
        # Register the user for the topic
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