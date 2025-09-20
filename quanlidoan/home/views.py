from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.

def home(request):
    return render(request, 'app/home.html')
def topic(request):
    return render(request, 'app/topic.html')
def report_progress(request):
    return render(request, 'app/report_progress.html')