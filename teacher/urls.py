from django.urls import path
from . import views

urlpatterns = [
    path('', views.teacher_home, name='teacher_home'),
    path('danhsach/', views.DanhSachDoAn, name='danh_sach_do_an'),
    path('them/', views.ThemDoAn, name='them_do_an'),
    path('sua/', views.SuaDoAn, name='sua_do_an'),
    path('xoa/', views.XoaDoAn, name='xoa_do_an'),
]
