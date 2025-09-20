from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('topic/', views.topic, name='topic'),
    path('report_progress/', views.report_progress, name='report_progress'),
]