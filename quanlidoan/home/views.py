from django.shortcuts import render
from django.http import HttpResponse
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
    return render(request, 'app/register_topic.html')

def report_progress(request):
    return render(request, 'app/report_progress.html')

def report_detail(request):
    return render(request, 'app/report_detail.html')