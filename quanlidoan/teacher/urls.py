from django.urls import path
from . import views

urlpatterns = [
    path('', views.teacher_home, name='teacher_home'),
    path('danhsach/', views.DanhSachDoAn, name='danh_sach_do_an'),
    path('danhsach/them/', views.ThemDoAn, name='them_do_an'),
    path("danhsach/chitiet/<int:mada>/", views.ChiTietDoAn, name="chi_tiet_do_an"),
    path('danhsach/sua/<int:mada>/', views.SuaDoAn, name='sua_do_an'),
    path('danhsach/xoa/<int:mada>/', views.XoaDoAn, name='xoa_do_an'),
    path("baocao/dangky/", views.BaoCaoDangKy, name="baocao_dangky"),

]
