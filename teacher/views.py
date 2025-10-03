from django.shortcuts import render

# Create your views here.

def teacher_home(request):
    return render(request, 'teacher.html')

def ThemDoAn(request):
    return render(request, 'them_do_an.html')

def DanhSachDoAn(request):
    return render(request, 'Danh_sach_do_an.html')

def XoaDoAn(request):
    return render(request, 'xoa_do_an.html')

def SuaDoAn(request):
    return render(request, 'sua_do_an.html')