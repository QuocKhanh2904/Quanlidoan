from asyncio.windows_events import NULL
from django.contrib import admin
from django.db import connection
import os
from django.utils import timezone
from django.core.files.storage import default_storage
from django.conf import settings
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

    def bienban_create_raw(mada, mahv, ngaybaove=None, diadiem=None, noidung=None, ghichu=None):
        with connection.cursor() as cursor:
            cursor.execute(" INSERT INTO BIENBAN (NgayBaoVe, DiaDiem, NoiDung, GhiChu, NgayLap, MaDA, MaHV) VALUES (%s, %s, %s, %s, %s, %s, %s)", [
                ngaybaove or timezone.now().date(),
                diadiem or None,
                noidung or None,
                ghichu or None,
                timezone.now().date(),
                int(mada),
                int(mahv),
            ])
            cursor.execute("SELECT SCOPE_IDENTITY()")
            new_id = cursor.fetchone()[0]
            return new_id
        
    def bienban_update_raw(mabb, ngaybaove=None, diadiem=None, noidung=None, ghichu=None):
        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE BIENBAN
                SET
                    NgayBaoVe = ISNULL(%s, NgayBaoVe),
                    DiaDiem   = ISNULL(%s, DiaDiem),
                    NoiDung   = ISNULL(%s, NoiDung),
                    GhiChu    = ISNULL(%s, GhiChu)
                WHERE MaBB = %s
            """, [
                ngaybaove or None,
                diadiem or None,
                noidung or None,
                ghichu or None,
                int(mabb),
            ])
        return True

    def bienban_delete_raw(mabb):
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM BIENBAN WHERE MaBB = %s", [int(mabb)])
        return True
   
    class Meta:
        managed = False
        db_table = 'BIENBAN'


class Dangky(models.Model):
    madk = models.AutoField(db_column='MaDK', primary_key=True)
    ngaydk = models.DateField(db_column='NgayDK', blank=True, null=True)
    trangthai = models.CharField(db_column='TrangThai', max_length=50, blank=True, null=True)
    mada = models.ForeignKey('Doan', models.DO_NOTHING, db_column='MaDA', blank=True, null=True)
    mahv = models.ForeignKey('Hocvien', models.DO_NOTHING, db_column='MaHV', blank=True, null=True)

    def dangky_create_raw(mada, mahv, ngaydk=None, trangthai=None):
        with connection.cursor() as cursor:
            cursor.execute(""" INSERT INTO DANGKY (MaDA, MaHV, NgayDK, TrangThai) VALUES (%s, %s, %s, %s)""", [
                int(mada),
                int(mahv),
                ngaydk or timezone.now().date(),
                int(trangthai) if trangthai is not None else 0
            ])
            cursor.execute("SELECT SCOPE_IDENTITY()")
            new_id = cursor.fetchone()[0]
            return new_id
        
    def dangky_update_raw(madk, mada=None, mahv=None, ngaydk=None, trangthai=None):
        with connection.cursor() as cursor:
            cursor.execute(""" UPDATE DANGKY SET MaDA = ISNULL(%s, MaDA), MaHV = ISNULL(%s, MaHV), NgayDK = ISNULL(%s, NgayDK), TrangThai = ISNULL(%s, TrangThai)
                WHERE MaDK = %s
            """, [
                int(mada) if mada else None,
                int(mahv) if mahv else None,
                ngaydk or None,
                int(trangthai) if trangthai is not None else None,
                int(madk)
            ])
        return True

    def dangky_delete_raw(madk):
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM DANGKY WHERE MaDK = %s", [int(madk)])
        return True

    class Meta:
        managed = False
        db_table = 'DANGKY'

class Diemthanhvien(models.Model):
    matv = models.ForeignKey('Thanhvienhoidong', models.DO_NOTHING, db_column='MaTV')
    mabb = models.ForeignKey(Bienban, models.DO_NOTHING, db_column='MaBB')
    diem = models.FloatField(db_column='Diem', blank=True, null=True)

    def diemthanhvien_list(mahv):
        with connection.cursor() as cursor:
            cursor.execute("EXEC sp_GetDiemThanhVienByMaHV @MaHV = %s", [mahv])
            rows = dictfetchall(cursor)
        return rows

    def diemthanhvien_update_raw(mabb, diemtv):
        with connection.cursor() as cursor:
            for tv in diemtv:
                cursor.execute("""
                    UPDATE DIEMTHANHVIEN
                    SET Diem = %s
                    WHERE MaBB = %s AND MaTV = %s
                """, [
                    tv.get("diem"),
                    int(mabb),
                    int(tv.get("matv"))
                ])
        return True

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
    diemhuongdan = models.FloatField(db_column='DiemHuongDan', blank=True, null=True)
    diemphanbien = models.FloatField(db_column='DiemPhanBien', blank=True, null=True)
    file = models.FileField(db_column='FileDoAn', upload_to='doan/', blank=True, null=True)
    magv = models.ForeignKey('Giangvien', models.DO_NOTHING, db_column='MaGV', blank=True, null=True)
    mahd = models.ForeignKey('Hoidong', models.DO_NOTHING, db_column='MaHD', blank=True, null=True)
    lydo = models.TextField(db_column='LyDo', blank=True, null=True)

    def doan_create_raw(
        tenda, trangthai=None, soluongtoida=None,
        ngaybd=None, ngaykt=None, linhvuc=None,
        mota=None, mahd=None, file=None
    ):
        file_path = None
        if file:
            file_path = default_storage.save(f'doan/{file.name}', file)

        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO DOAN (TenDA, TrangThai, SoLuongToiDa, NgayBD, NgayKT, LinhVuc, MoTa, MaHD, FileDoAn)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, [
                tenda,
                int(trangthai) if trangthai else None,
                int(soluongtoida) if soluongtoida else None,
                ngaybd,
                ngaykt,
                linhvuc or None,
                mota or None,
                int(mahd) if mahd else None,
                file_path
            ])
            # Lấy ID vừa tạo (nếu bạn cần trả về)
            cursor.execute("SELECT SCOPE_IDENTITY()")  # nếu dùng SQL Server
            new_id = cursor.fetchone()[0]
            return new_id

    def doan_update_raw(
        mada, tenda, trangthai=None, soluongtoida=None,
        ngaybd=None, ngaykt=None, linhvuc=None,
        mota=None, mahd=None, file=None, lydo=None
    ):
        file_path = None
        if file:
            from django.core.files.storage import default_storage
            file_path = default_storage.save(f'doan/{file.name}', file)

        with connection.cursor() as cursor:
            cursor.execute(""" UPDATE DOAN SET TenDA=%s, TrangThai=%s, SoLuongToiDa=%s, NgayBD=%s, NgayKT=%s, LinhVuc=%s, MoTa=%s, MaHD=%s, FileDoAn=%s, LyDo=%s WHERE MaDA=%s""",
                [
                    tenda,
                    int(trangthai) if trangthai else None,
                    int(soluongtoida) if soluongtoida else None,
                    ngaybd,
                    ngaykt,
                    linhvuc or None,
                    mota or None,
                    int(mahd) if mahd else None,
                    file_path,
                    lydo or None,
                    int(mada)
                ])
            return mada
    
    def doan_delete_raw(mada, file):
        if file:
            full_path = os.path.join(settings.MEDIA_ROOT, file)
            if os.path.isfile(full_path):
                os.remove(full_path)
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM DOAN WHERE MaDA=%s", [int(mada)])
            return mada
    
    def doan_list(tenda=None, trangthai=None, mahd=None):
        with connection.cursor() as cursor:
            cursor.execute("EXEC sp_filter_doan @tenda=%s, @trangthai=%s, @mahd=%s", [tenda, trangthai, mahd]) 
            rows = dictfetchall(cursor)
        return rows

    class Meta:
        managed = False
        db_table = 'DOAN'


class Giangvien(models.Model):
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='+', related_query_name='+', db_column='userid')
    magv = models.AutoField(db_column='MaGV', primary_key=True) #AUTO
    hoten = models.CharField(db_column='HoTen', max_length=100, blank=True, null=True)
    email = models.CharField(db_column='Email', max_length=100, blank=True, null=True)
    sodienthoai = models.CharField(db_column='SoDienThoai', max_length=20, blank=True, null=True)
    donvicongtac = models.CharField(db_column='DonViCongTac', max_length=100, blank=True, null=True)

    def giangvien_list(hoten=None, email=None, sdt=None, donvi=None, sort_field=None, sort_dir='ASC'):
        with connection.cursor() as cursor:
            cursor.execute(""" EXEC sp_GiangVien_ThongKe @HoTen=%s, @Email=%s, @SoDienThoai=%s, @DonViCongTac=%s,@SortField=%s,@SortDirection=%s"""
                           , [hoten, email, sdt, donvi, sort_field, sort_dir])
            rows = dictfetchall(cursor)
            return rows

    def giangvien_create_raw(userid, hoten, email=None, sdt=None, donvi=None):
        with connection.cursor() as cursor:
            cursor.execute("INSERT INTO GIANGVIEN (hoten, email, sodienthoai, donvicongtac, userid) VALUES (%s, %s, %s, %s, %s)",
                [   hoten,
                    email or None,
                    sdt or None,
                    donvi or None,
                    userid ])
            cursor.execute("SELECT SCOPE_IDENTITY()")
            new_id = cursor.fetchone()[0]
            return new_id

    def giangvien_update_raw(magv, tengv, email=None, sdt=None, donvi=None):
        with connection.cursor() as cursor:
            cursor.execute(""" UPDATE GIANGVIEN SET hoten=%s, email=%s, sodienthoai=%s, donvicongtac=%s WHERE MaGV=%s""",
                [   tengv,
                    email or None,
                    sdt or None,
                    donvi or None,
                    int(magv)   ])
            return magv

    def giangvien_delete_raw(magv):
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM GIANGVIEN WHERE MaGV=%s", [int(magv)])
            return magv
            
    class Meta:
        managed = False
        db_table = 'GIANGVIEN'


class Hocvien(models.Model):
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='+', related_query_name='+', db_column='userid')
    mahv = models.AutoField(db_column='MaHV', primary_key=True)
    hoten = models.CharField(db_column='HoTen', max_length=100, blank=True, null=True)
    email = models.CharField(db_column='Email', max_length=100, blank=True, null=True)
    sodienthoai = models.CharField(db_column='SoDienThoai', max_length=20, blank=True, null=True)
    lop = models.CharField(db_column='Lop', max_length=50, blank=True, null=True)
    manamhoc = models.ForeignKey('NamHoc', models.DO_NOTHING, db_column='MaNamHoc', blank=True, null=True)

    def hocvien_create_raw(hoten, userid, manamhoc, email=None, sdt=None, lop=None):
        with connection.cursor() as cursor:
            cursor.execute("INSERT INTO HOCVIEN (hoten, email, sodienthoai, lop, manamhoc, userid) VALUES (%s, %s, %s, %s, %s, %s)",
                [   hoten,
                    email or None,
                    sdt or None,
                    lop or None,
                    manamhoc ,
                    userid   ])
            cursor.execute("SELECT SCOPE_IDENTITY()")
            new_id = cursor.fetchone()[0]
            return new_id
    
    def hocvien_update_raw(mahv, tenhv, email=None, sdt=None, lop=None, manamhoc=None):
        with connection.cursor() as cursor:
            cursor.execute(""" UPDATE HOCVIEN SET hoten=%s, email=%s, sodienthoai=%s, lop=%s, manamhoc=%s WHERE mahv=%s""",
                [   tenhv,
                    email or None,
                    sdt or None,
                    lop or None,
                    manamhoc or None,
                    int(mahv)   ])
            return mahv
    
    def hocvien_delete_raw(mahv):
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM HOCVIEN WHERE MaHV=%s", [int(mahv)])
            return mahv

    class Meta:
        managed = False
        db_table = 'HOCVIEN'


class Hoidong(models.Model):
    mahd = models.AutoField(db_column='MaHD', primary_key=True)
    tenhd = models.CharField(db_column='TenHD', max_length=100, blank=True, null=True)
    ngaythanhlap = models.DateField(db_column='NgayThanhLap', blank=True, null=True)
    ngayketthuc = models.DateField(db_column='NgayKetThuc', blank=True, null=True)
    linhvuc = models.CharField(db_column='LinhVuc', max_length=100, blank=True, null=True)

    def hoidong_list():
        with connection.cursor() as cursor:
            cursor.execute('''SELECT MaHD as mahd, TenHD as tenhd, ngaythanhlap as ngaythanhlap, ngayketthuc as ngayketthuc, linhvuc as linhvuc FROM HOIDONG''')
            return dictfetchall(cursor)
        
    def hoidong_create_raw(tenhd, ngaythanhlap=None, ngayketthuc=None, linhvuc=None):
        with connection.cursor() as cursor:
            cursor.execute("INSERT INTO HOIDONG (tenhd, ngaythanhlap, ngayketthuc, linhvuc) VALUES (%s, %s, %s, %s)",
                [   tenhd,
                    ngaythanhlap or None,
                    ngayketthuc or None,
                    linhvuc or None   ])
            cursor.execute("SELECT SCOPE_IDENTITY()")
            new_id = cursor.fetchone()[0]
            return new_id
        
    def hoidong_update_raw(mahd, tenhd, ngaythanhlap=None, ngayketthuc=None, linhvuc=None):
        with connection.cursor() as cursor:
            cursor.execute(""" UPDATE HOIDONG SET tenhd=%s, ngaythanhlap=%s, ngayketthuc=%s, linhvuc=%s WHERE mahd=%s""",
                [   tenhd,
                    ngaythanhlap or None,
                    ngayketthuc or None,
                    linhvuc or None,
                    int(mahd)   ])
            return mahd
        
    def hoidong_delete_raw(mahd):
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM HOIDONG WHERE MaHD=%s", [int(mahd)])
            return mahd

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

    def thanhvienhoidong_create_raw(vaitro, magv, mahd):
        with connection.cursor() as cursor:
            cursor.execute("INSERT INTO THANHVIENHOIDONG (vaitro, magv, mahd ) VALUES (%s, %s, %s)",
                [   vaitro,
                    magv ,
                    mahd 
                    ])
            cursor.execute("SELECT SCOPE_IDENTITY()")
            new_id = cursor.fetchone()[0]
            return new_id
    
    def thanhvienhoidong_delete_raw(matv):
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM THANHVIENHOIDONG WHERE MaTV=%s", [int(matv)])
            return matv
    
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

    def thongke_tiendo(min_value, max_value):
        with connection.cursor() as cursor:
            cursor.execute("SELECT dbo.fn_SoLuongDoAn_TheoTienDo(%s, %s)", [min_value, max_value])
            result = cursor.fetchone()[0]
        return result

    def tiendo_list(mada=None):
        with connection.cursor() as cursor:
            if mada:
                cursor.execute("""
                    SELECT 
                        t.MaTD, t.MoTaCongViec, t.TienDoPhanTram, 
                        t.NgayCapNhat, t.NguoiKiemTra, t.File, 
                        d.MaDA, d.TenDA
                    FROM TIENDO t
                    JOIN DOAN d ON t.MaDA = d.MaDA
                    WHERE t.MaDA = %s
                    ORDER BY t.NgayCapNhat DESC
                """, [mada])
            else:
                cursor.execute("""
                    SELECT 
                        t.MaTD as matd, t.MoTaCongViec as motacongviec, t.TienDoPhanTram as tiendophantram, 
                        t.NgayCapNhat as ngaycapnhat, t.NguoiKiemTra as nguoikiemtra, t.File as file, 
                        d.MaDA as mada, d.TenDA as tenda
                    FROM TIENDO t
                    JOIN DOAN d ON t.MaDA = d.MaDA
                    ORDER BY t.NgayCapNhat DESC
                """)
            rows = cursor.fetchall()
        return rows
    
    def tiendo_create_raw(mada, motacv, tiendo, nguoikiemtra=None, file=None):
        file_path = None
        if file:
            file_path = default_storage.save(f'tiendo/{file.name}', file)

        with connection.cursor() as cursor:
            cursor.execute(""" INSERT INTO TIENDO (MaDA, MoTaCongViec, TienDoPhanTram, NgayCapNhat, NguoiKiemTra, [File]) VALUES (%s, %s, %s, %s, %s, %s)""", [
                int(mada),
                motacv,
                int(tiendo) if tiendo else 0,
                timezone.now(),
                nguoikiemtra or None,
                file_path
            ])
            cursor.execute("SELECT SCOPE_IDENTITY()")
            new_id = cursor.fetchone()[0]
        return new_id

    def tiendo_update_raw(matd, motacv=None, tiendo=None, nguoikiemtra=None, file=None):
        old_file = None
        with connection.cursor() as cursor:
            cursor.execute("SELECT [File] FROM TIENDO WHERE MaTD = %s", [matd])
            row = cursor.fetchone()
            if row:
                old_file = row[0]

        file_path = old_file
        if file:
            file_path = default_storage.save(f'tiendo/{file.name}', file)

        with connection.cursor() as cursor:
            cursor.execute("UPDATE TIENDO SET MoTaCongViec = %s, TienDoPhanTram = %s, NgayCapNhat = %s, NguoiKiemTra = %s, [File] = %s WHERE MaTD = %s", [
                motacv,
                int(tiendo) if tiendo else None,
                timezone.now(),
                nguoikiemtra or None,
                file_path,
                int(matd)
            ])
        return True

    def tiendo_delete_raw(matd):
        with connection.cursor() as cursor:
            cursor.execute("SELECT [File] FROM TIENDO WHERE MaTD = %s", [matd])
            row = cursor.fetchone()
            file_path = row[0] if row else None
            cursor.execute("DELETE FROM TIENDO WHERE MaTD = %s", [matd])
        if file_path:
            full_path = os.path.join(settings.MEDIA_ROOT, file_path)
            if os.path.exists(full_path):
                os.remove(full_path)
        return True

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
