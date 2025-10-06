from django.contrib import admin
from django.db import connection
from django.db import models
from django.contrib.auth.models import User

class Giangvien(models.Model):
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='+', db_column='magv')
    magv = models.AutoField(db_column='MaGV', primary_key=True) #AUTO
    hoten = models.CharField(db_column='HoTen', max_length=100, blank=True, null=True)
    email = models.CharField(db_column='Email', max_length=100, blank=True, null=True)
    sodienthoai = models.CharField(db_column='SoDienThoai', max_length=20, blank=True, null=True)
    donvicongtac = models.CharField(db_column='DonViCongTac', max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'GIANGVIEN'


class Hocvien(models.Model):
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='+', db_column='mahv')
    mahv = models.AutoField(db_column='MaHV', primary_key=True)
    hoten = models.CharField(db_column='HoTen', max_length=100, blank=True, null=True)
    email = models.CharField(db_column='Email', max_length=100, blank=True, null=True)
    sodienthoai = models.CharField(db_column='SoDienThoai', max_length=20, blank=True, null=True)
    lop = models.CharField(db_column='Lop', max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'HOCVIEN'