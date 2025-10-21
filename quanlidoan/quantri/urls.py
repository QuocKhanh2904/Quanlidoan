from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('project',views.manage_project, name='project'),
    path('giangvien',views.manage_giangvien, name='giangvien'),
    path('hocvien',views.manage_hocvien, name='hocvien'),
    path('hoidong',views.manage_hoidong, name='hoidong'),
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
    
]