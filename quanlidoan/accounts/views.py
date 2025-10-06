from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from .models import *  # hoặc import theo app
# from home import urls


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            # PHÂN QUYỀN ĐIỀU HƯỚNG
            if hasattr(user, 'hocvien'):
                return redirect('home')
            elif hasattr(user, 'giangvien'):
                return redirect('giangvien')
            elif user.is_superuser or user.is_staff:
                return redirect('/admin/')  # hoặc 'quantri_dashboard'
            else:
                return redirect('default_home')  # fallback
        else:
            return render(request, 'login.html', {'error': 'Sai tài khoản hoặc mật khẩu'})
    
    return render(request, 'login.html')
