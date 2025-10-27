from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='admin_home'),
    path('project',views.manage_project, name='project'),
    path('giangvien',views.manage_giangvien, name='giangvien'),
    path('hocvien',views.manage_hocvien, name='hocvien'),
    path('hoidong',views.manage_hoidong, name='hoidong'),
    path('tiendo/',views.manage_tiendo, name='tiendo'),
    path('dangky/',views.manage_dangky, name='dangky'),
    path('baove/',views.manage_baove, name='baove'),
    path("tiendo/create/", views.tiendo_create, name="tiendo_create"),
    path("tiendo/update/", views.tiendo_update, name="tiendo_update"),
    path("tiendo/delete/", views.tiendo_delete, name="tiendo_delete"),
    path("tiendo/detail/<int:matd>/", views.tiendo_detail, name="tiendo_detail"),

    path('phancongdoan',views.manage_phancong, name='phancongdoan'),
    path('phancongdoan/update/',views.phancongdoan_update, name='phancongdoan_update'),
    path('phancongdoan/reject/',views.phancongdoan_reject, name='phancongdoan_reject'),

    path("baove/create/", views.baove_create, name="baove_create"),
    path("baove/update/", views.baove_update, name="baove_update"),
    path("baove/delete/", views.baove_delete, name="baove_delete"),
    path("dangky/by_doan/", views.dangky_by_doan, name="dangky_by_doan"),
    path("baove/detail/<int:mabb>/", views.baove_detail, name="baove_detail"),

    path("dangky/create/", views.dangky_create, name="dangky_create"),
    path("dangky/detail/<int:madk>/", views.dangky_detail, name="dangky_detail"),
    path("dangky/delete/", views.dangky_delete, name="dangky_delete"),
    path("dangky/update/", views.dangky_update, name="dangky_update"),
    path("hocvien/by_lop/", views.hocvien_by_lop, name="hocvien_by_lop"),

    path('doan/create/', views.doan_create, name='doan_create'),
    path('doan/update/', views.doan_update, name='doan_update'),
    path('doan/delete/', views.doan_delete, name='doan_delete'),
    path('giangvien/create/', views.giangvien_create, name='giangvien_create'),
    path('giangvien/update/', views.giangvien_update, name='giangvien_update'),
    path('giangvien/delete/', views.giangvien_delete, name='giangvien_delete'),
    path('hocvien/create/', views.hocvien_create, name='hocvien_create'),
    path('hocvien/update/', views.hocvien_update, name='hocvien_update'),
    path('hocvien/delete/', views.hocvien_delete, name='hocvien_delete'),
    path('hoidong/create/', views.hoidong_create, name='hoidong_create'),
    path('hoidong/update/', views.hoidong_update, name='hoidong_update'),
    path('thanhvienhoidong/addmember/', views.thanhvienhoidong_create, name='thanhvienhoidong_create'),
    path('thanhvienhoidong/list/', views.thanhvienhoidong_list, name='thanhvienhoidong_list'),
    path('hoidong/delete/', views.hoidong_delete, name='hoidong_delete'),
    path('thanhvienhoidong/delete/', views.thanhvienhoidong_delete, name='thanhvienhoidong_delete'),
    path('contact/', views.contact, name='quantri_contact'),

    path('export/doan-theo-hoidong/<int:mahd>/', views.export_doan_theo_hoidong, name='export_doan_theo_hoidong'),
]