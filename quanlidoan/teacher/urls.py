from django.urls import path
from django.views.generic import RedirectView
from . import views

urlpatterns = [
    path("", views.teacher_home, name="teacher_home"),

    # Đồ án
    path("danhsach/", views.DanhSachDoAn, name="danh_sach_do_an"),
    path("danhsach/them/", views.ThemDoAn, name="them_do_an"),
    path("danhsach/chitiet/<int:mada>/", views.ChiTietDoAn, name="chi_tiet_do_an"),
    path("danhsach/sua/<int:mada>/", views.SuaDoAn, name="sua_do_an"),
    path("danhsach/xoa/<int:mada>/", views.XoaDoAn, name="xoa_do_an"),

    # Báo cáo
    path("baocao/dangky/", views.BaoCaoDangKy, name="baocao_dangky"),

    # === Hội đồng của tôi ===
    path("hoi-dong-cua-toi/", views.hoi_dong_cua_toi, name="hoi_dong_cua_toi"),
    path("hoi-dong/<int:mada>/cham-diem/<int:mahv>/", views.ChamDiemHoiDong, name="cham_diem_hoi_dong"),



    # Đồ án GV hướng dẫn
    path("huongdan/", views.DanhSachHuongDan, name="ds_huong_dan"),
    path("huongdan/<int:mada>/tien-do/", views.HD_XemTienDo, name="hd_xem_tiendo"),
    path("huongdan/tiendo/<int:matd>/danh-gia/", views.HD_DanhGiaTienDo, name="hd_danh_gia_tiendo"),
    path("huongdan/tiendo/<int:matd>/huy-duyet/",views.HD_HuyDuyetTienDo,name="hd_huy_duyet_tiendo"),
    path("huongdan/<int:mada>/cham-diem/", views.HD_ChamDiem, name="hd_cham_diem"),
    path("huongdan/<int:mada>/cham-diem-huongdan/", views.ChamDiemHuongDan, name="cham_diem_huongdan"),

    path("phan-bien/", views.DanhSachPhanBien, name="ds_phan_bien"),
    path("phan-bien/<int:mada>/cham-diem/", views.ChamDiemPhanBien, name="cham_diem_phan_bien"),

    path('contact/', views.contact, name='teacher_contact'),
    path('export-doan-gv/<int:magv>/', views.export_doan_giangvien, name='export_doan_giangvien'),

]


