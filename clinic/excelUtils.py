from io import BytesIO 
import xlsxwriter
from django.utils.translation import ugettext

def WriteToExcel(excel_data):
    output = BytesIO()
    workbook = xlsxwriter.Workbook(output)
    workbook.encoding='utf-8'
    worksheet_s = workbook.add_worksheet("Summary")

    list_alphabet = ['A', 'B', 'C', 'D', 'E', 'G', 'H', 'I']

    title = workbook.add_format({
        'bold': True,
        'font_size': 18,
        'align': 'center',
        'valign': 'vcenter'
    })

    title_2 = workbook.add_format({
        'bold': True,
        'font_size': 14,
        'align': 'center',
        'valign': 'vcenter'
    })
    header = workbook.add_format({
        'bg_color': '#F7F7F7',
        'color': 'black',
        'align': 'center',
        'valign': 'top',
        'border': 1
    })
    cell = workbook.add_format({
        'align': 'left',
        'valign': 'top',
        'text_wrap': True,
    })
    cell_center = workbook.add_format({
        'align': 'center',
        'valign': 'top',
        'border': 1,
        'text_wrap': True,
    })

    worksheet_s.merge_range('A1:D1', "Phòng Khám Đa Khoa MEDOTIS", cell_center)
    worksheet_s.merge_range('S1:W1', "Mẫu số: C79a-HD", cell_center)
    worksheet_s.merge_range('S2:W3', "Ban hành theo thông tư số 178/2012/TT-BTC ngày 23/10/2012 của Bộ Tài chính)", cell_center)

    worksheet_s.merge_range('A4:W4', "DANH SÁCH NGƯỜI BỆNH BẢO HIỂM Y TẾ KHÁM CHỮA BỆNH NGOẠI TRÚ ĐỀ NGHỊ THANH TOÁN", title)
    # worksheet_s.merge_range('H5:P5', )
    worksheet_s.merge_range('A7:A9', "STT", cell_center)
    worksheet_s.merge_range('B7:B9', "Họ và tên", cell_center)
    worksheet_s.merge_range('C7:D8', "Năm sinh", cell_center)
    worksheet_s.write(8, 2, 'Nam', cell_center)
    worksheet_s.write(8, 3, 'Nữ', cell_center)
    worksheet_s.merge_range('E7:E9', "Mã thẻ BHYT", cell_center)
    worksheet_s.merge_range('F7:F9', "Mã ĐKBĐ", cell_center)
    worksheet_s.merge_range('G7:G9', "Mã bệnh", cell_center)
    worksheet_s.merge_range('I7:T7', "TỔNG CHI PHÍ KHÁM, CHỮA BỆNH BHYT", cell_center)
    worksheet_s.merge_range('I8:I9', "Tổng cộng", cell_center)
    worksheet_s.merge_range('J8:O8', "Không áp dụng tỉ lệ thanh toán", cell_center)
    worksheet_s.merge_range('H7:H9', "Ngày khám", cell_center)
    worksheet_s.write(8, 9, 'Xét nghiệm', cell_center)
    worksheet_s.write(8, 10, 'CĐHA TDCN', cell_center)
    worksheet_s.write(8, 11, 'Thuốc', cell_center)

    worksheet_s.set_row(8, 60) 
    
    worksheet_s.write(8, 12, 'Máu', cell_center)
    worksheet_s.write(8, 13, 'TTPT', cell_center)
    worksheet_s.write(8, 14, 'VTYT', cell_center)
    worksheet_s.merge_range('P8:R8', "Thanh toán theo tỷ lệ", cell_center)
    worksheet_s.write(8, 15, 'DVKT', cell_center)
    worksheet_s.write(8, 16, 'Thuốc', cell_center)
    worksheet_s.write(8, 17, 'VTYT', cell_center)
    worksheet_s.merge_range('S8:S9', "Tiền khám", cell_center)
    worksheet_s.merge_range('T8:T9', "Vận chuyển", cell_center)
    worksheet_s.merge_range('U7:U9', "Người bệnh chi trả", cell_center)
    worksheet_s.merge_range('V7:W7', "Chi phí đề nghị BHXH thanh toán", cell_center)
    worksheet_s.write(8, 21, 'Tổng cộng', cell_center)
    worksheet_s.write(8, 22, 'Trong đó chi phí ngoài quỹ định suất', cell_center)

    for idx, data in enumerate(list_alphabet):
        worksheet_s.write(9, idx, data, cell_center)

    for i in range(15):
        idx = len(list_alphabet) + i
        worksheet_s.write(9, idx, f"({i+1})", cell_center)

    for idx, data in enumerate(excel_data):
        row = 10 + idx
        worksheet_s.write(row, 1, data['benh_nhan'], cell_center)
        if data['gioi_tinh'] == '1':
            worksheet_s.write(row, 2, data['nam_sinh'], cell_center)
            worksheet_s.write(row, 3, '', cell_center)
        elif data['gioi_tinh'] == '2':
            worksheet_s.write(row, 2, '', cell_center)
            worksheet_s.write(row, 3, data['nam_sinh'], cell_center)
        else:
            worksheet_s.write(row, 2, '', cell_center)
            worksheet_s.write(row, 3, '', cell_center)

        worksheet_s.write(row, 4, data['ma_bhyt'], cell_center)
        worksheet_s.write(row, 5, data['ma_dkbd'], cell_center)
        worksheet_s.write(row, 6, data['ma_benh'], cell_center)
        worksheet_s.write(row, 7, data['ngay_kham'], cell_center)
        worksheet_s.write_number(row, 8, data['tong_cong_1'], cell_center)

        worksheet_s.write_number(row, 9, data['xet_nghiem'], cell_center)
        worksheet_s.write_number(row, 10, data['cdha_tdcn'], cell_center)
        worksheet_s.write_number(row, 11, data['thuoc_1'], cell_center)
        worksheet_s.write_number(row, 12, data['mau'], cell_center)
        worksheet_s.write_number(row, 13, data['ttpt'], cell_center)
        worksheet_s.write_number(row, 14, data['vtyt_1'], cell_center)
        worksheet_s.write_number(row, 15, data['dvkt'], cell_center)
        worksheet_s.write_number(row, 16, data['thuoc_2'], cell_center)
        worksheet_s.write_number(row, 17, data['vtyt_2'], cell_center)

        worksheet_s.write_number(row, 18, data['tien_kham'], cell_center)
        worksheet_s.write_number(row, 19, data['van_chuyen'], cell_center)
        worksheet_s.write_number(row, 20, data['tu_chi_tra'], cell_center)
        worksheet_s.write_number(row, 21, data['bao_hiem_tra'], cell_center)
        worksheet_s.write_number(row, 22, data['ngoai_ds'], cell_center)

    row = row + 1
    worksheet_s.write(row, 0, '', cell_center)
    worksheet_s.write(row, 1, 'Tổng cộng', cell_center)
    worksheet_s.write(row, 2, '', cell_center)
    worksheet_s.write(row, 3, '', cell_center)
    worksheet_s.write(row, 4, '', cell_center)
    worksheet_s.write(row, 5, '', cell_center)
    worksheet_s.write(row, 6, '', cell_center)
    worksheet_s.write(row, 7, '', cell_center)
    worksheet_s.write_formula(row, 8, '=SUM({0}{1}:{0}{2})'.format('I', 11, row), cell_center)
    worksheet_s.write(row, 9, '', cell_center)
    worksheet_s.write(row, 10, '', cell_center)
    worksheet_s.write(row, 11, '', cell_center)
    worksheet_s.write(row, 12, '', cell_center)
    worksheet_s.write(row, 13, '', cell_center)
    worksheet_s.write(row, 14, '', cell_center)
    worksheet_s.write(row, 15, '', cell_center)
    worksheet_s.write(row, 16, '', cell_center)
    worksheet_s.write(row, 17, '', cell_center)
    worksheet_s.write_formula(row, 18, '=SUM({0}{1}:{0}{2})'.format('S', 11, row), cell_center)
    worksheet_s.write(row, 19, '', cell_center)
    worksheet_s.write_formula(row, 20, '=SUM({0}{1}:{0}{2})'.format('U', 11, row), cell_center)
    worksheet_s.write_formula(row, 21, '=SUM({0}{1}:{0}{2})'.format('V', 11, row), cell_center)
    worksheet_s.write(row, 22, '', cell_center)

    workbook.close()

    xlsx_data = output.getvalue()
    return xlsx_data

def writeToExcelDichVu(excel_data):
    output = BytesIO()
    workbook = xlsxwriter.Workbook(output)
    workbook.encoding='utf-8'
    worksheet_s = workbook.add_worksheet("Summary")

    title = workbook.add_format({
        'bold': True,
        'font_size': 14,
        'align': 'center',
        'valign': 'vcenter'
    })

    title_2 = workbook.add_format({
        'bold': True,
        'font_size': 14,
        'align': 'center',
        'valign': 'vcenter'
    })

    header = workbook.add_format({
        'bg_color': '#F7F7F7',
        'color': 'black',
        'align': 'center',
        'valign': 'top',
        'border': 1
    })
    cell = workbook.add_format({
        'align': 'left',
        'valign': 'top',
        'text_wrap': True,
        'border': 1
    })
    cell_center = workbook.add_format({
        'align': 'center',
        'valign': 'top',
        'border': 1,
        'text_wrap': True,
    })

    worksheet_s.merge_range('A1:C1', "Phòng Khám Đa Khoa MEDOTIS", cell)
    worksheet_s.merge_range('E2:H2', "Mẫu số 21/BHYT", cell)
    worksheet_s.merge_range('A4:H4', "THỐNG KÊ DỊCH VỤ KỸ THUẬT THANH TOÁN BHYT", title)
    worksheet_s.merge_range('A5:H5', "Đối với người bệnh BHYT đăng kí ban đầu/ đa tuyến đến", title_2) 

    worksheet_s.merge_range('A8:A9', "STT", cell_center)
    worksheet_s.merge_range('B8:B9', "Mã số theo danh mục BHYT", cell_center)
    worksheet_s.merge_range('C8:C9', "Tên dịch vụ y tế", cell_center)
    worksheet_s.merge_range('D8:E8', "Số lượng", cell_center)

    worksheet_s.write(8, 3, 'Ngoại trú', cell_center)
    worksheet_s.write(8, 4, 'Nội trú', cell_center)

    worksheet_s.merge_range('F8:F9', "Đơn giá (đồng)", cell_center)
    worksheet_s.merge_range('G8:G9', "Thành tiền (đồng)", cell_center)

    for idx, data in enumerate(excel_data):
        row = 9 + idx
        worksheet_s.write(row, 0, data['stt'], cell_center)
        worksheet_s.write(row, 1, data['ma_dvkt'], cell_center)
        worksheet_s.write(row, 2, data['dich_vu_kham__ten_dvkt'], cell_center)
        worksheet_s.write(row, 3, data['dich_vu_kham_count'], cell_center)
        worksheet_s.write(row, 4, '0', cell_center)
        worksheet_s.write(row, 5, data['don_gia'], cell_center)
        worksheet_s.write(row, 6, data['tong_tien'], cell_center)

    row = row + 1

    worksheet_s.write(row, 0, "", cell_center)
    worksheet_s.write(row, 1, "Tổng cộng", cell_center)
    worksheet_s.write(row, 2, "", cell_center)
    worksheet_s.write_formula(row, 3, '=SUM({0}{1}:{0}{2})'.format('D', 10, row), cell_center)
    worksheet_s.write_formula(row, 4, '=SUM({0}{1}:{0}{2})'.format('E', 10, row), cell_center)
    worksheet_s.write(row, 2, "", cell_center)
    worksheet_s.write_formula(row, 6, '=SUM({0}{1}:{0}{2})'.format('G', 10, row), cell_center)

    workbook.close()

    xlsx_data = output.getvalue()
    return xlsx_data

def writeToExcelThuoc(excel_data):
    output = BytesIO()
    workbook = xlsxwriter.Workbook(output)
    workbook.encoding='utf-8'
    worksheet_s = workbook.add_worksheet("Summary")

    title = workbook.add_format({
        'bold': True,
        'font_size': 14,
        'align': 'center',
        'valign': 'vcenter'
    })

    title_2 = workbook.add_format({
        'bold': True,
        'font_size': 14,
        'align': 'center',
        'valign': 'vcenter'
    })

    header = workbook.add_format({
        'bg_color': '#F7F7F7',
        'color': 'black',
        'align': 'center',
        'valign': 'top',
        'border': 1
    })
    cell = workbook.add_format({
        'align': 'left',
        'valign': 'top',
        'text_wrap': True,
        'border': 1
    })
    cell_center = workbook.add_format({
        'align': 'center',
        'valign': 'top',
        'border': 1,
        'text_wrap': True,
    })

    worksheet_s.merge_range('A1:D1', "Phòng Khám Đa Khoa MEDOTIS", cell)
    worksheet_s.merge_range('J2:M2', "Mẫu số 20/BHYT", cell)
    worksheet_s.merge_range('A4:M4', "THỐNG KÊ THUỐC THANH TOÁN BHYT", title)

    worksheet_s.merge_range('A7:A8', "STT", cell_center)
    worksheet_s.merge_range('B7:B8', "STT theo DMT của BHYT", cell_center)
    worksheet_s.merge_range('C7:C8', "Tên hoạt chất", cell_center)
    worksheet_s.merge_range('D7:D8', "Tên thuốc thành phẩm", cell_center)
    worksheet_s.merge_range('E7:E8', "Đường dùng, dạng bào chế", cell_center)
    worksheet_s.merge_range('F7:F8', "Nồng độ/ hàm lượng", cell_center)
    worksheet_s.merge_range('G7:G8', "Số đăng ký hoặc số GPNK", cell_center)
    worksheet_s.merge_range('H7:H8', "Đơn vị tính", cell_center)
    worksheet_s.merge_range('I7:J7', "Số lượng", cell_center)

    worksheet_s.write(7, 8, 'Ngoại trú', cell_center)
    worksheet_s.write(7, 9, 'Nội trú', cell_center)

    worksheet_s.merge_range('K7:K8', "Đơn giá (đồng)", cell_center)
    worksheet_s.merge_range('L7:L8', "Thành tiền (đồng)", cell_center)

    for idx, data in enumerate(excel_data):
        row = 8 + idx
        worksheet_s.write(row, 0, "", cell_center)
        worksheet_s.write(row, 1, data['ma_thuoc'], cell_center)
        worksheet_s.write(row, 2, data['ten_hoat_chat'], cell_center)
        worksheet_s.write(row, 3, data['thuoc__ten_thuoc'], cell_center)
        worksheet_s.write(row, 4, data['duong_dung'], cell_center)
        worksheet_s.write(row, 5, data['ham_luong'], cell_center)
        worksheet_s.write(row, 6, data['so_dang_ky'], cell_center)
        worksheet_s.write(row, 7, data['don_vi_tinh'], cell_center)
        worksheet_s.write(row, 8, data['thuoc_count'], cell_center)
        worksheet_s.write(row, 9, "0", cell_center)
        worksheet_s.write(row, 10, data['don_gia'], cell_center)
        worksheet_s.write(row, 11, data['tong_tien'], cell_center)

    workbook.close()

    xlsx_data = output.getvalue()
    return xlsx_data

def ExportExcelBaoCaoXNTThuoc(excel_data=None):
    output = BytesIO()
    workbook = xlsxwriter.Workbook(output)
    workbook.encoding='utf-8'
    worksheet_s = workbook.add_worksheet("Tổng Hợp")

    title = workbook.add_format({
        'bold': True,
        'font_size': 14,
        'align': 'center',
        'valign': 'vcenter'
    })

    title_2 = workbook.add_format({
        'bold': True,
        'font_size': 14,
        'align': 'center',
        'valign': 'vcenter'
    })

    header = workbook.add_format({
        'bg_color': '#F7F7F7',
        'color': 'black',
        'align': 'center',
        'valign': 'top',
        'border': 1
    })
    cell = workbook.add_format({
        'align': 'left',
        'valign': 'top',
        'text_wrap': True,
        'border': 1
    })
    cell_center = workbook.add_format({
        'align': 'center',
        'valign': 'top',
        'border': 1,
        'text_wrap': True,
    })

    worksheet_s.merge_range('B1:S1', "THỐNG KÊ XUẤT NHẬP TỒN THUỐC", cell_center)
    worksheet_s.merge_range('B2:S2', "", cell_center)
    worksheet_s.merge_range('B4:B5', "STT", cell_center)
    worksheet_s.merge_range('C4:C5', "Mã thuốc", cell_center)
    worksheet_s.merge_range('D4:D5', "Tên thuốc", cell_center)
    worksheet_s.merge_range('E4:E5', "Hoạt chất", cell_center)
    worksheet_s.merge_range('F4:F5', "Hàm lượng", cell_center)
    worksheet_s.merge_range('G4:G5', "Đơn vị tính", cell_center)
    worksheet_s.merge_range('H4:H5', "Hãng sản xuất", cell_center)
    worksheet_s.merge_range('I4:I5', "Nước sản xuất", cell_center)
    worksheet_s.merge_range('J4:J5', "Số lô", cell_center)
    worksheet_s.merge_range('K4:K5', "Hạn sử dụng", cell_center)
    worksheet_s.merge_range('L4:L5', "Tồn đầu kỳ", cell_center)
    worksheet_s.merge_range('M4:O4', "Nhập", cell_center)
    worksheet_s.merge_range('P4:R4', "Xuất", cell_center)
    worksheet_s.merge_range('S4:S5', "Tồn cuối kỳ", cell_center)

    worksheet_s.write(4, 12, 'Số lượng', cell_center)
    worksheet_s.write(4, 13, 'Giá nhập', cell_center)
    worksheet_s.write(4, 14, 'Thành tiền', cell_center)
    worksheet_s.write(4, 15, 'Số lượng', cell_center)
    worksheet_s.write(4, 16, 'Giá xuất', cell_center)
    worksheet_s.write(4, 17, 'Thành tiền', cell_center)

    for idx, data in enumerate(excel_data):
        row = 5 + idx
        worksheet_s.write(row, 1, idx, cell_center)
        if data['ma_thuoc'] is not None or data['ma_thuoc'] != '':
            worksheet_s.write(row, 2, data['ma_thuoc'], cell_center)
        else:
            worksheet_s.write(row, 2, '-', cell_center)

        worksheet_s.write(row, 3, data['ten_thuoc'], cell_center)
        worksheet_s.write(row, 4, data['ten_hoat_chat'], cell_center)
        worksheet_s.write(row, 5, data['ham_luong'], cell_center)
        worksheet_s.write(row, 6, data['don_vi_tinh'], cell_center)
        worksheet_s.write(row, 7, data['cong_ty__ten_cong_ty'], cell_center)
        worksheet_s.write(row, 8, data['nuoc_sx'], cell_center)

        if data['so_lo'] is not None or data['so_lo'] != '':
            worksheet_s.write(row, 9, data['so_lo'], cell_center)
        else:
            worksheet_s.write(row, 9, '-', cell_center)

        if data['han_su_dung'] is not None:
            worksheet_s.write(row, 10, data['han_su_dung'], cell_center)
        else:
            worksheet_s.write(row, 10, '-', cell_center)

        if data['ton_dau_ky'] is not None:
            worksheet_s.write_number(row, 11, data['ton_dau_ky'], cell_center)
        else:
            worksheet_s.write(row, 11, '-', cell_center)

        if data['so_luong_nhap'] is not None:
            worksheet_s.write_number(row, 12, data['so_luong_nhap'], cell_center)
        else:
            worksheet_s.write(row, 12, '-', cell_center)

        if data['don_gia'] is not None or data['don_gia'] != '':
            worksheet_s.write_number(row, 13, data['don_gia'], cell_center)
        else:
            worksheet_s.write(row, 13, '-', cell_center)

        if data['thanh_tien_nhap'] is not None:
            worksheet_s.write_number(row, 14, data['thanh_tien_nhap'], cell_center)
        else:
            worksheet_s.write(row, 14, '-', cell_center)

        if data['so_luong_xuat'] is not None:
            worksheet_s.write_number(row, 15, data['so_luong_xuat'], cell_center)
        else:
            worksheet_s.write(row, 15, '-', cell_center)

        if data['don_gia_tt'] is not None or data['don_gia_tt'] != '':
            worksheet_s.write_number(row, 16, data['don_gia_tt'], cell_center)
        else:
            worksheet_s.write(row, 16, '-', cell_center)

        if data['thanh_tien_xuat'] is not None:
            worksheet_s.write_number(row, 17, data['thanh_tien_xuat'], cell_center)
        else:
            worksheet_s.write(row, 17, '-', cell_center)

        if data['ton_cuoi_ky'] is not None:
            worksheet_s.write_number(row, 18, data['ton_cuoi_ky'], cell_center)
        else:
            worksheet_s.write(row, 18, '-', cell_center)

    workbook.close()

    xlsx_data = output.getvalue()
    return xlsx_data


def ExportExcelDSThuocSapHetDate(excel_data=None):
    output = BytesIO()
    workbook = xlsxwriter.Workbook(output)
    workbook.encoding='utf-8'
    worksheet_s = workbook.add_worksheet("Tổng Hợp")

    title = workbook.add_format({
        'bold': True,
        'font_size': 14,
        'align': 'center',
        'valign': 'vcenter'
    })

    title_2 = workbook.add_format({
        'bold': True,
        'font_size': 14,
        'align': 'center',
        'valign': 'vcenter'
    })

    header = workbook.add_format({
        'bg_color': '#F7F7F7',
        'color': 'black',
        'align': 'center',
        'valign': 'top',
        'border': 1
    })
    cell = workbook.add_format({
        'align': 'left',
        'valign': 'top',
        'text_wrap': True,
        'border': 1
    })
    cell_center = workbook.add_format({
        'align': 'center',
        'valign': 'top',
        'border': 1,
        'text_wrap': True,
    })

    worksheet_s.merge_range('B1:S1', "THỐNG KÊ DANH SÁCH THUỐC SẮP HẾT DATE", cell_center)
    worksheet_s.merge_range('B2:S2', "", cell_center)
    worksheet_s.merge_range('B4:B5', "STT", cell_center)
    worksheet_s.merge_range('C4:C5', "Mã thuốc", cell_center)
    worksheet_s.merge_range('D4:D5', "Tên thuốc", cell_center)
    worksheet_s.merge_range('E4:E5', "Hoạt chất", cell_center)
    worksheet_s.merge_range('F4:F5', "Hàm lượng", cell_center)
    worksheet_s.merge_range('G4:G5', "Đơn vị tính", cell_center)
    worksheet_s.merge_range('H4:H5', "Hãng sản xuất", cell_center)
    worksheet_s.merge_range('I4:I5', "Nước sản xuất", cell_center)
    worksheet_s.merge_range('J4:J5', "Số lô", cell_center)
    worksheet_s.merge_range('K4:K5', "Hạn sử dụng", cell_center)
    
    for idx, data in enumerate(excel_data):
        row = 5 + idx
        worksheet_s.write(row, 1, idx, cell_center)
        if data['ma_thuoc'] is not None or data['ma_thuoc'] != '':
            worksheet_s.write(row, 2, data['ma_thuoc'], cell_center)
        else:
            worksheet_s.write(row, 2, '-', cell_center)

        worksheet_s.write(row, 3, data['ten_thuoc'], cell_center)
        worksheet_s.write(row, 4, data['ten_hoat_chat'], cell_center)
        worksheet_s.write(row, 5, data['ham_luong'], cell_center)
        worksheet_s.write(row, 6, data['don_vi_tinh'], cell_center)
        worksheet_s.write(row, 7, data['cong_ty']['ten_cong_ty'], cell_center)
        worksheet_s.write(row, 8, data['nuoc_sx'], cell_center)

        if data['so_lo'] is not None or data['so_lo'] != '':
            worksheet_s.write(row, 9, data['so_lo'], cell_center)
        else:
            worksheet_s.write(row, 9, '-', cell_center)

        if data['han_su_dung'] is not None:
            worksheet_s.write(row, 10, data['han_su_dung'], cell_center)
        else:
            worksheet_s.write(row, 10, '-', cell_center)

    workbook.close()

    xlsx_data = output.getvalue()
    return xlsx_data