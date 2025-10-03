from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('topic/', views.topic, name='topic'),
    path('topic/register_topic/', views.register_topic, name='register_topic'),
    path('report_progress/', views.report_progress, name='report_progress'),
    path('report_progress/report_detail/', views.report_detail, name='report_detail'),
]