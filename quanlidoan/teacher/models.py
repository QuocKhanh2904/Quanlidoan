from django.db import connection
from django.core.files.storage import default_storage
from django.db import models
from django.contrib.auth.models import User

class Bienban(models.Model):
    mabb = models.AutoField(db_column='MaBB', primary_key=True)
    ngaybaove = models.DateField(db_column='NgayBaoVe', blank=True, null=True)
    diadiem = models.CharField(db_column='DiaDiem', max_length=100, blank=True, null=True)
    noidung = models.TextField(db_column='NoiDung', blank=True, null=True)
    ghichu = models.TextField(db_column='GhiChu', blank=True, null=True)
    ngaylap = models.DateField(db_column='NgayLap', blank=True, null=True)
    mada = models.ForeignKey('Doan', models.DO_NOTHING, db_column='MaDA', blank=True, null=True)
    mahv = models.ForeignKey('Hocvien', models.DO_NOTHING, db_column='MaHV', blank=True, null=True)
    
    class Meta:
        managed = False
        db_table = 'BIENBAN'


class Dangky(models.Model):
    madk = models.AutoField(db_column='MaDK', primary_key=True)
    ngaydk = models.DateField(db_column='NgayDK', blank=True, null=True)
    trangthai = models.CharField(db_column='TrangThai', max_length=50, blank=True, null=True)
    mada = models.ForeignKey('Doan', models.DO_NOTHING, db_column='MaDA', blank=True, null=True)
    mahv = models.ForeignKey('Hocvien', models.DO_NOTHING, db_column='MaHV', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'DANGKY'


class Diemthanhvien(models.Model):
    matv = models.ForeignKey('Thanhvienhoidong', models.DO_NOTHING, db_column='MaTV')
    mabb = models.ForeignKey(Bienban, models.DO_NOTHING, db_column='MaBB')
    diem = models.FloatField(db_column='Diem', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'DIEMTHANHVIEN'
        unique_together = (('matv', 'mabb'),)

def dictfetchall(cursor):
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]   


class Doan(models.Model):
    mada = models.AutoField(db_column='MaDA', primary_key=True)
    tenda = models.CharField(db_column='TenDA', max_length=200, blank=True, null=True)
    trangthai = models.CharField(db_column='TrangThai', max_length=50, blank=True, null=True)
    soluongtoida = models.IntegerField(db_column='SoLuongToiDa', blank=True, null=True)
    ngaygui = models.DateField(db_column='NgayGui', blank=True, null=True)
    mota = models.TextField(db_column='MoTa', blank=True, null=True)
    linhvuc = models.CharField(db_column='LinhVuc', max_length=100, blank=True, null=True)
    ngaybd = models.DateField(db_column='NgayBD', blank=True, null=True)
    ngaykt = models.DateField(db_column='NgayKT', blank=True, null=True)
    file = models.FileField(db_column='FileDoAn', upload_to='doan/', blank=True, null=True)
    magv = models.ForeignKey('Giangvien', models.DO_NOTHING, db_column='MaGV', blank=True, null=True)
    mahd = models.ForeignKey('Hoidong', models.DO_NOTHING, db_column='MaHD', blank=True, null=True)
    lydo = models.TextField(db_column='LyDo', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'DOAN'


class Giangvien(models.Model):
    magv = models.AutoField(db_column='MaGV', primary_key=True)  # AUTO
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, db_column='UserID')  # ✔️ Liên kết tài khoản
    hoten = models.CharField(db_column='HoTen', max_length=100, blank=True, null=True)
    email = models.CharField(db_column='Email', max_length=100, blank=True, null=True)
    sodienthoai = models.CharField(db_column='SoDienThoai', max_length=20, blank=True, null=True)
    donvicongtac = models.CharField(db_column='DonViCongTac', max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'GIANGVIEN'


class Hocvien(models.Model):
    mahv = models.AutoField(db_column='MaHV', primary_key=True) 
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='+', db_column='UserID')
    hoten = models.CharField(db_column='HoTen', max_length=100, blank=True, null=True)
    email = models.CharField(db_column='Email', max_length=100, blank=True, null=True)
    sodienthoai = models.CharField(db_column='SoDienThoai', max_length=20, blank=True, null=True)
    lop = models.CharField(db_column='Lop', max_length=50, blank=True, null=True)
    manamhoc = models.ForeignKey('NamHoc', models.DO_NOTHING, db_column='MaNamHoc', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'HOCVIEN'

class Hoidong(models.Model):
    mahd = models.AutoField(db_column='MaHD', primary_key=True)
    tenhd = models.CharField(db_column='TenHD', max_length=100, blank=True, null=True)
    ngaythanhlap = models.DateField(db_column='NgayThanhLap', blank=True, null=True)
    ngayketthuc = models.DateField(db_column='NgayKetThuc', blank=True, null=True)
    linhvuc = models.CharField(db_column='LinhVuc', max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'HOIDONG'


class Huongdandoan(models.Model):
    mada = models.ForeignKey(Doan, models.DO_NOTHING, db_column='MaDA')
    magv = models.ForeignKey(Giangvien, models.DO_NOTHING, db_column='MaGV')
    vaitro = models.CharField(db_column='VaiTro', max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'HUONGDANDOAN'
        unique_together = (('mada', 'magv'),)


class Ketquabaove(models.Model):
    makq = models.AutoField(db_column='MaKQ', primary_key=True)
    diem = models.FloatField(db_column='Diem', blank=True, null=True)
    danhgia = models.CharField(db_column='DanhGia', max_length=200, blank=True, null=True)
    xeploai = models.CharField(db_column='XepLoai', max_length=50, blank=True, null=True)
    mabb = models.OneToOneField(Bienban, models.DO_NOTHING, db_column='MaBB', blank=True, null=True)
    
    class Meta:
        managed = False
        db_table = 'KETQUABAOVE'


class Thanhvienhoidong(models.Model):
    matv = models.AutoField(db_column='MaTV', primary_key=True)
    vaitro = models.CharField(db_column='VaiTro', max_length=50, blank=True, null=True)
    magv = models.ForeignKey(Giangvien, models.DO_NOTHING, db_column='MaGV', blank=True, null=True)
    mahd = models.ForeignKey(Hoidong, models.DO_NOTHING, db_column='MaHD', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'THANHVIENHOIDONG'


class Tiendo(models.Model):
    matd = models.AutoField(db_column='MaTD', primary_key=True)
    motacongviec = models.TextField(db_column='MoTaCongViec', blank=True, null=True)
    tiendophantram = models.IntegerField(db_column='TienDoPhanTram', blank=True, null=True)
    ngaycapnhat = models.DateField(db_column='NgayCapNhat', blank=True, null=True)
    nguoikiemtra = models.CharField(db_column='NguoiKiemTra', max_length=100, blank=True, null=True)
    mada = models.ForeignKey(Doan, models.DO_NOTHING, db_column='MaDA', blank=True, null=True)
    file = models.FileField(db_column='File', upload_to='baocao/', blank=True, null=True)
    baocao = models.ImageField(upload_to="baocao/", blank=True, null=True)
        
    class Meta:
        managed = False
        db_table = 'TIENDO'

class Namhoc(models.Model):
    manamhoc = models.AutoField(db_column='MaNamHoc', primary_key=True)
    namhoc = models.IntegerField(db_column='NamHoc', blank=True, null=True)
    handk = models.DateField(db_column='HanDangKy', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'NAMHOC'