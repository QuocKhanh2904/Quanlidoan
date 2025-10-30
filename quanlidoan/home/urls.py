from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('topic/', views.topic, name='topic'),
    path('topic/register_topic/', views.register_topic, name='register_topic'),
    path('topic/regist_topic/', views.regist_topic, name='regist_topic'),
    path('cancel-register/<int:mada>/', views.cancel_register, name='cancel_register'),
    path('report_progress/', views.report_progress, name='report_progress'),
    path('submit_report/', views.submit_report, name='submit_report'),
    path('submit_topic/', views.submit_topic, name='submit_topic'),
    path('update_topic/', views.update_topic, name='update_topic'),
    path('result/', views.result, name='result'),
    path('contact/', views.contact, name='contact'),
    path('change_password/', views.change_password, name='change_password'),
]