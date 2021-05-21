from django.db.models.expressions import Func, OuterRef, Subquery
from django.db.models import Exists, OuterRef
from clinic.pagination import CustomPagination, PaginationHandlerMixin
from finance.models import (
    HoaDonChuoiKham, 
    HoaDonThuoc, 
    HoaDonLamSang,
    NhapHang
)
from finance.serializers import HoaDonChuoiKhamSerializer
from json import dump
from rest_framework.parsers import FileUploadParser
from rest_framework.parsers import MultiPartParser
import json
from medicine.models import CongTy, DonThuoc, KeDonThuoc, NhomThuoc, Thuoc, TrangThaiDonThuoc, VatTu
from django.http.response import Http404, HttpResponse, JsonResponse
from rest_framework import views
from rest_framework.views import APIView
from clinic.models import (
    BaiDang,
    ChiSoXetNghiem, 
    DichVuKham, District, 
    FileKetQua, 
    KetQuaTongQuat, 
    LichHenKham, MauPhieu,
    NhomChiSoXetNghiem, 
    PhanKhoaKham, 
    PhongChucNang, 
    PhongKham, Province, 
    TrangThaiChuoiKham, 
    TrangThaiKhoaKham, 
    TrangThaiLichHen, 
    ChuoiKham, 
    KetQuaChuyenKhoa, 
    BacSi, Ward
)
from rest_framework import viewsets
from django.contrib.auth import authenticate, get_user_model
from .serializers import (BaiDangSerializer, BookLichHenKhamSerializer, ChiSoXetNghiemSerializer,DangKiSerializer, DanhSachDonThuocSerializer, DanhSachKetQuaChuoiKhamSerializer, DanhSachPhanKhoaSerializer, DanhSachPhongKhamSerializer,DichVuKhamSerializer, DichVuKhamSerializerFormatted, DichVuKhamSerializerSimple, DistrictSerializer, DonThuocSerializer, FileKetQuaSerializer, FilterChuoiKhamSerializer, FilterDichVuKhamBaoHiemSerializer, FilterDichVuSerializer, FilterDonThuocSerializer, FilterHoaDonChuoiKhamBaoHiemSerializer, GroupSerializer,HoaDonChuoiKhamSerializerSimple, HoaDonLamSangSerializerFormatted, HoaDonThuocSerializer,HoaDonThuocSerializerSimple, KetQuaTongQuatSerializer, KetQuaXetNghiemSerializer,LichHenKhamSerializer, LichHenKhamSerializerSimple, LichHenKhamUserSerializer, MauPhieuSerializer, NhomChiSoTieuChuanSerializer,PhanKhoaKhamDichVuSerializer, PhanKhoaKhamSerializer, PhieuKetQuaSerializer,PhongChucNangSerializer, PhongChucNangSerializerSimple, PhongKhamSerializer,ProfilePhongChucNangSerializer, StaffUserSerializer, TatCaLichHenSerializer, TrangThaiLichHenSerializer,UserLoginSerializer, UserSerializer, ChuoiKhamSerializer,UserUpdateInfoSerializer, UserUpdateInfoRequestSerializer,UploadAvatarSerializer, AppointmentUpdateDetailSerializer,UpdateLichHenKhamSerializer, DichVuKhamHoaDonSerializer,HoaDonChuoiKhamThanhToanSerializer, KetQuaChuyenKhoaSerializer,  ChuoiKhamSerializerSimple, UserSerializerSimple, VatTuSerializer,DanhSachDichVuSerializer, HoaDonLamSangSerializer, DanhSachBacSiSerializer, DanhSachThuocSerializerSimple, WardSerializer)
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.request import Request
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.conf import settings
from datetime import datetime, timedelta
from django.utils import timezone
from datetime import datetime, timedelta
from django.db.models.functions import TruncDay
from django.db.models import Count, F, Sum, Q
from django.db import models
from medicine.serializers import (
    CongTySerializer,
    DanhSachThuocSerializer, 
    KeDonThuocSerializer,
    ThuocSerializer
)
from rest_framework import pagination
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from rest_framework import generics
from django.contrib.auth.models import Group
from rest_framework import generics
from datetime import date, datetime
from dateutil.relativedelta import relativedelta

User = get_user_model()

class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer

    def list(self, request):
        user = User.objects.all()
        serializer = UserSerializer(user, many=True, context={"request": request})

        user_data = serializer.data

        ds_user_moi = []

        for user in user_data:
            child_user = User.objects.filter(parent = user['id'])
            child_user_serializer = UserSerializer(child_user, many=True)
            user['child'] = child_user_serializer.data
            ds_user_moi.append(user)

        response = {
            "error": False,
            "status": status.HTTP_200_OK,
            "message": "Danh sach Nguoi dung",
            "data": ds_user_moi,
        }
        return Response(response)

    def create(self, request):
        try:
            user_serializer = UserSerializer(data=request.data, context={"request": request})
            user_serializer.is_valid(raise_exception=True)
            user_serializer.save()
        
            response = {
                "error": False,
                "status": status.HTTP_201_CREATED,
                "message" : "Them Nguoi Dung Thanh Cong",
            }
        except:
            response = {
                "error": True,
                "status": status.HTTP_409_CONFLICT,
                "message": "Khong The Them Moi Nguoi Dung",
            }

        return Response(response)

    # def retrieve(self, request: Request, pk=None):
    #     queryset = User.objects.all()
    #     user = get_object_or_404(queryset, pk=pk)
    #     serializer = UserSerializer(user, context={"request": request})

    #     user_data = serializer.data

    #     return Response({"error":False, "status": status.HTTP_200_OK, "message":"Single Data Fetch", "data":user_data})
    
    def retrieve(self, request: Request, *args, **kwargs):
        if kwargs.get('pk') == 'me':
            return Response(self.get_serializer(request.user).data)
        else:
            queryset = User.objects.all()
            user = get_object_or_404(queryset, pk=kwargs.get('pk'))
            serializer = UserSerializer(user, context={"request": request})
            user_data = serializer.data
            return Response({"error":False, "status": status.HTTP_200_OK, "message":"Single Data Fetch", "data":user_data})
        return super().retrieve(request, **kwargs)

    # TODO set quyền cho người dùng, chỉ có admin mới thấy được chi tiết của từng người dùng, còn lại mỗi người dùng chỉ thấy được chi tiết của họ

    def update(self, request, pk=None):
        queryset = User.objects.all()
        user = get_object_or_404(queryset, pk=pk)
        
        serialzer = UserSerializer(user, data=request.data, context={"request": request})
        serialzer.is_valid()
        serialzer.save()

        # for child_user_data in request.data["parent"]:
        #     print(child_user_data)

        # try:
        #     for child_user_data in request.data["parent"]:
        #         if child_user_data["id"] == 0:
        #             # tao moi 1 tai khoan con

        #             del child_user_data["id"]
        #             child_user_data["parent"] = serialzer.data["id"]
        #             child_user_serializer = UserSerializer(data=child_user_data, context={"request": request})
        #             child_user_serializer.is_valid()
        #             child_user_serializer.save()
        #         else:
        #             # update tai khoan con
        #             queryset2 = User.objects.all()
        #             child_user = get_object_or_404(queryset2, pk=child_user_data["id"])
        #             del child_user_data["id"]
        #             child_user_serializer = UserSerializer(child_user, data=child_user_data, context={"request": request})
        #             child_user_serializer.is_valid()
        #             child_user_serializer.save()
            
        #     return Response({"error": True, "message": child_user_serializer.error_messages})
        # except:
        # return Response({"error": True, "message": serialzer.error_messages})
        return Response({"error": False, "status": status.HTTP_200_OK, "message": "Cap Nhat Du Lieu Thanh Cong"})

    # TODO create JWT authentication

class DangNhapAPI(views.APIView):
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = authenticate(
                request,
                so_dien_thoai = serializer.validated_data['so_dien_thoai'],
                password = serializer.validated_data['password']
            )
            try:
                u = User.objects.get(so_dien_thoai=serializer.validated_data['so_dien_thoai'])
            except:
                return Response({
                    "error_message": "Số Điện Thoại Hoặc Mật Khẩu Không Đúng",
                    'error_code': 400,
                }, status=status.HTTP_400_BAD_REQUEST)
        
            user_serializer = UserSerializerSimple(u, context={'request': request})
            if user:
                refresh = TokenObtainPairSerializer.get_token(user)
                data = {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    'access_expires': int(settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'].total_seconds()),
                    'refresh_expires': int(settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'].total_seconds()),
                    'user_id': u.id,
                    'user_data': user_serializer.data
                }
                return Response(data, status=status.HTTP_200_OK)
            return Response({
                "error_message": "Số Điện Thoại Hoặc Mật Khẩu Không Đúng",
                'error_code': 400,
            },status=status.HTTP_400_BAD_REQUEST)
        return Response({
            "error_message": serializer.errors,
            "error_code": 400
        }, status=status.HTTP_400_BAD_REQUEST)

class DangKiAPI(generics.GenericAPIView):
    serializer_class = DangKiSerializer
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            "user": UserSerializer(user, context=self.get_serializer_context()).data,
            "status": status.HTTP_201_CREATED,
            "message": "Đăng Kí Tài Khoản Thành Công"
        })

class DichVuKhamViewSet(viewsets.ViewSet):

    def list(self, request):
        dich_vu_kham = DichVuKham.objects.all()
        serializer = DichVuKhamSerializerFormatted(dich_vu_kham, many=True, context={"request": request})
        response = {
            "error": False,
            "status": status.HTTP_200_OK,
            "message": "Danh Sach Dich Vu Kham",
            "data": serializer.data
        }
        return Response(response)

    def create(self, request):
        try:
            serializer = DichVuKhamSerializerFormatted(data=request.data, context={"request": request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            response = {
                "error": False, 
                "status": status.HTTP_201_CREATED,
                "message": "Them Dich Vu Kham Thanh Cong"
            }
        except:
            response = {
                "error": True, 
                "status": status.HTTP_409_CONFLICT,
                "message": "Khong The Them Dich Vu Kham"
            }
        return Response(response)

    def retrieve(self, request, pk=None):
        queryset = DichVuKham.objects.all()
        dich_vu_kham = get_object_or_404(queryset, pk=pk)
        serializer = DichVuKhamSerializerFormatted(dich_vu_kham, context={"request": request})
        data = serializer.data
        response = {
            "error": False, 
            "status": status.HTTP_200_OK,
            "message": f"Dich Vu: {dich_vu_kham.ten_dich_vu}",
            "data": data
        }
        return Response(response)   

    def update(self, request, pk=None):
        try:
            queryset = DichVuKham.objects.all()
            dich_vu_kham = get_object_or_404(queryset, pk=pk)
            serializer = DichVuKhamSerializerFormatted(dich_vu_kham, data=request.data, context={"request": request})
            serializer.is_valid()
            serializer.save()
            response = {
                "error": False, 
                "status": status.HTTP_200_OK,
                "message": f"Cap Nhat Dich Vu {dich_vu_kham.ten_dich_vu} Thanh Cong",
                "data": serializer.data
            }
        except:
            response = {
                "error": True, 
                "status": status.HTTP_409_CONFLICT,
                "message": "Khong The Cap Nhat Dich Vu",
            }
        return Response(response)

    def destroy(self, request, pk=None):
        queryset = DichVuKham.objects.all()
        dich_vu_kham = get_object_or_404(queryset, pk=pk)
        dich_vu_kham.delete()
        return Response({
            "error": False, 
            "status": status.HTTP_204_NO_CONTENT,
            "message": f"Xoa Dich Vu {dich_vu_kham.ten_dich_vu} Thanh Cong"
        })

class DichVuKhamListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = DichVuKhamSerializerFormatted
    pagination_class = CustomPagination

    def get_queryset(self):
        queryset = DichVuKham.objects.all()

        term = self.request.query_params.get('query[search]')
        if term is not None:
            queryset = queryset.filter(ten_dvkt__icontains=term)
        
        return queryset 

class ThuocListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = ThuocSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        queryset = Thuoc.objects.all()

        term = self.request.query_params.get('query[search]')
        id_nhom_thuoc = self.request.query_params.get('query[id_nhom_thuoc]')
        bao_hiem = self.request.query_params.get('query[bao_hiem]')

        if term is not None:
            queryset = queryset.filter(Q(ten_thuoc__icontains=term) | Q(ten_hoat_chat__icontains=term) | Q(duong_dung__icontains=term) | Q(don_vi_tinh__icontains=term))

        if id_nhom_thuoc is not None:
            queryset = queryset.filter(nhom_thuoc__id=id_nhom_thuoc)

        if bao_hiem is not None:
            if bao_hiem == 'True':
                bh = True
            else:
                bh = False
            queryset = queryset.filter(bao_hiem = bh)

        return queryset

class PhongChucNangViewSet(viewsets.ModelViewSet):
    def list(self, request):
        phong_chuc_nang = PhongChucNang.objects.all()
        serializer = PhongChucNangSerializer(phong_chuc_nang, many=True, context={"request": request})
        response = {
            "error": False,
            "status": status.HTTP_200_OK,
            "message": "Danh Sach Phong Chuc Nang",
            "data": serializer.data
        }
        return Response(response)

    def create(self, request):
        try:
            serializer = PhongChucNangSerializer(data=request.data, context={"request": request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            response = {
                "error": False, 
                "status": status.HTTP_201_CREATED,
                "message": "Them Phong Chuc Nang Thanh Cong"
            }
        except:
            response = {
                "error": True, 
                "status": status.HTTP_409_CONFLICT,
                "message": "Khong The Them Phong Chuc Nang"
            }
        return Response(response)

    def retrieve(self, request, pk=None):
        queryset = PhongChucNang.objects.all()
        phong_chuc_nang = get_object_or_404(queryset, pk=pk)
        serializer = PhongChucNangSerializer(phong_chuc_nang, context={"request": request})
        data = serializer.data
        response = {
            "error": False, 
            "status": status.HTTP_200_OK,
            "message": f"Phong Chuc Nang: {phong_chuc_nang.ten_phong_chuc_nang}",
            "data": data
        }
        return Response(response)   

    def update(self, request, pk=None):
        try:
            queryset = PhongChucNang.objects.all()
            phong_chuc_nang = get_object_or_404(queryset, pk=pk)
            serializer = PhongChucNangSerializer(phong_chuc_nang, data=request.data, context={"request": request})
            serializer.is_valid()
            serializer.save()
            response = {
                "error": False, 
                "status": status.HTTP_200_OK,
                "message": f"Cap Nhat Phong Chuc Nang {phong_chuc_nang.ten_phong_chuc_nang} Thanh Cong",
                "data": serializer.data
            }
        except:
            response = {
                "error": True, 
                "status": status.HTTP_409_CONFLICT,
                "message": "Khong The Cap Nhat Phong Chuc Nang",
            }
        return Response(response)

    def destroy(self, request, pk=None):
        queryset = PhongChucNang.objects.all()
        phong_chuc_nang = get_object_or_404(queryset, pk=pk)
        phong_chuc_nang.delete()
        return Response({
            "error": False, 
            "status": status.HTTP_204_NO_CONTENT,
            "message": f"Xóa Phòng Chức Năng {phong_chuc_nang.ten_phong_chuc_nang} Thành Công"
        })

class LichHenKhamViewSet(viewsets.ModelViewSet):
    serializer_class = LichHenKhamSerializer

    def list(self, request):
        # trang_thai = TrangThaiLichHen.objects.filter(Q(ten_trang_thai="Thanh Toán Lâm Sàng") | Q(ten_trang_thai = "Chờ Thanh Toán"))
        trang_thai = TrangThaiLichHen.objects.get_or_create(ten_trang_thai = "Đã Thanh Toán Lâm Sàng")[0] 
        now = timezone.localtime(timezone.now())
        tomorrow = now + timedelta(1)
        today_end = tomorrow.replace(hour=0, minute=0, second=0)

        lich_hen = LichHenKham.objects.filter(trang_thai=trang_thai, thoi_gian_bat_dau__lte=today_end)
        # lich_hen = LichHenKham.objects.filter(trang_thai = trang_thai).annotate(relevance=models.Case(
        #     models.When(thoi_gian_bat_dau__gte=now, then=1),
        #     models.When(thoi_gian_bat_dau__lt=now, then=2),
        #     output_field=models.IntegerField(),
        # )).annotate(
        # timediff=models.Case(
        #     models.When(thoi_gian_bat_dau__gte=now, then= F('thoi_gian_bat_dau') - now),
        #     models.When(thoi_gian_bat_dau__lt=now, then=now - F('thoi_gian_bat_dau')),
        #     # models.When(thoi_gian_bat_dau__lte=today_end - F('thoi_gian_bat_dau')),
        #     output_field=models.DurationField(),
        # )).order_by('relevance', 'timediff')
        # upcoming_events = []
        # for lich in lich_hen:
        #     if lich.relevance == 1:
        #         upcoming_events.append(lich)

        serializer = LichHenKhamSerializer(lich_hen, many=True, context={"request": request})
        response = {
            "error": False,
            "status": status.HTTP_200_OK,
            "message": "Danh Sach Lich Hen Kham",
            "data": serializer.data        
        }
        return Response(response)

    def create(self, request):
        try:
            serializer = LichHenKhamSerializer(data=request.data, context={"request": request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            response = {
                "error": False, 
                "status": status.HTTP_201_CREATED,
                "message": "Them Lich Hen Thanh Cong"
            }
        except:
            response = {
                "error": True, 
                "status": status.HTTP_409_CONFLICT,
                "message": "Khong The Them Lich Hen"
            }
        return Response(response)

    def retrieve(self, request: Request, *args, **kwargs):
        if kwargs.get('pk') == 'me':
            queryset = LichHenKham.objects.filter(benh_nhan=request.user)
            serializer = LichHenKhamSerializer(queryset, many=True, context={"request": request})
            return Response(serializer.data)
        else:
            queryset = LichHenKham.objects.all()
            lich_hen = get_object_or_404(queryset, pk=kwargs.get('pk'))
            serializer = LichHenKhamSerializer(lich_hen, context={"request": request})
            data = serializer.data
            response = {
                "error": False, 
                "status": status.HTTP_200_OK,
                "message": "Lich Hen",
                "data": data
            }
            return Response(response)
        return super().retrieve(*args, **kwargs)

    def update(self, request, pk=None):
        try:
            queryset = LichHenKham.objects.all()
            lich_hen = get_object_or_404(queryset, pk=pk)
            serializer = LichHenKhamSerializer(lich_hen, data=request.data, context={"request": request})
            serializer.is_valid()
            serializer.save()
            response = {
                "error": False, 
                "status": status.HTTP_200_OK,
                "message": "Cap Nhat Lich Hen Thanh Cong",
                "data": serializer.data
            }
        except:
            response = {
                "error": True, 
                "status": status.HTTP_409_CONFLICT,
                "message": "Khong The Cap Nhat Lich Hen",
            }
        return Response(response)

    def destroy(self, request, pk=None):
        queryset = LichHenKham.objects.all()
        lich_hen = get_object_or_404(queryset, pk=pk)
        lich_hen.delete()
        return Response({
            "error": False, 
            "status": status.HTTP_204_NO_CONTENT,
            "message": "Xoa Lich Hen Thanh Cong"
        })

    # NOTE: khi lễ tân cập nhật lịch hẹn, sẽ tự động cập nhật trường nguoi_phu_trach
    # def perform_update(self, serializer):
    #     serializer.save(nguoi_phu_trach=self.request.user)

class TrangThaiLichHenViewSet(viewsets.ModelViewSet):
    def list(self, request):
        trang_thai_lich_hen = TrangThaiLichHen.objects.all()
        serializer = TrangThaiLichHenSerializer(trang_thai_lich_hen, many=True, context={"request": request})
        response = {
            "error": False,
            "status": status.HTTP_200_OK,
            "message": "Danh Sach Trang Thai Lich Hen",
            "data": serializer.data        
        }
        return Response(response)

    def create(self, request):
        try:
            serializer = TrangThaiLichHenSerializer(data=request.data, context={"request": request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            response = {
                "error": False, 
                "status": status.HTTP_201_CREATED,
                "message": f"Them Trang Thai Lich Hen Thanh Cong"
            }
        except:
            response = {
                "error": True, 
                "status": status.HTTP_409_CONFLICT,
                "message": "Khong The Them Trang Thai Lich Hen"
            }
        return Response(response)

    def retrieve(self, request, pk=None):
        queryset = TrangThaiLichHen.objects.all()
        trang_thai_lich_hen = get_object_or_404(queryset, pk=pk)
        serializer = TrangThaiLichHenSerializer(trang_thai_lich_hen, context={"request": request})
        data = serializer.data
        response = {
            "error": False, 
            "status": status.HTTP_200_OK,
            "message": "Lich Hen",
            "data": data
        }
        return Response(response)   

    def update(self, request, pk=None):
        try:
            queryset = TrangThaiLichHen.objects.all()
            trang_thai_lich_hen = get_object_or_404(queryset, pk=pk)
            serializer = TrangThaiLichHenSerializer(trang_thai_lich_hen, data=request.data, context={"request": request})
            serializer.is_valid()
            serializer.save()
            response = {
                "error": False, 
                "status": status.HTTP_200_OK,
                "message": "Cap Nhat Lich Hen Thanh Cong",
                "data": serializer.data
            }
        except:
            response = {
                "error": True, 
                "status": status.HTTP_409_CONFLICT,
                "message": "Khong The Cap Nhat Lich Hen",
            }
        return Response(response)

    def destroy(self, request, pk=None):
        queryset = TrangThaiLichHen.objects.all()
        trang_thai_lich_hen = get_object_or_404(queryset, pk=pk)
        trang_thai_lich_hen.delete()
        return Response({
            "error": False, 
            "status": status.HTTP_204_NO_CONTENT,
            "message": "Xoa Lich Hen Thanh Cong"
        })

class ChuoiKhamViewSet(viewsets.ModelViewSet):
    queryset = ChuoiKham.objects.all()
    serializer_class = ChuoiKhamSerializer

    def get_queryset(self):
        if self.action == 'retrieve': 
            return self.queryset.filter(benh_nhan=self.request.user)
        return self.queryset

    def list(self, request):
        chuoi_kham = ChuoiKham.objects.select_related('benh_nhan').all().order_by("-thoi_gian_tao")
        serializer = ChuoiKhamSerializer(chuoi_kham, many=True, context={"request": request})
        response = {
            "error": False,
            "status": status.HTTP_200_OK,
            "message": "Danh Sach Chuoi Kham",
            "data": serializer.data        
        }
        return Response(response)

    def create(self, request):
        try:
            serializer = ChuoiKhamSerializer(data=request.data, context={"request": request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            response = {
                "error": False, 
                "status": status.HTTP_201_CREATED,
                "message": f"Them Chuoi Kham Thanh Cong"
            }
        except:
            response = {
                "error": True, 
                "status": status.HTTP_409_CONFLICT,
                "message": "Khong The Them Chuoi Kham"
            }
        return Response(response)

    def retrieve(self, request, *args, **kwargs):
        if kwargs.get('pk') == 'me':
            chuoi_kham = ChuoiKham.objects.filter(benh_nhan=request.user.id)
            serializer = ChuoiKhamSerializer(chuoi_kham, many=True, context={"request": request})
            return Response(serializer.data)
        else:
            queryset = ChuoiKham.objects.all()
            chuoi_kham = get_object_or_404(queryset, pk=kwargs.get('pk'))

            serializer = ChuoiKhamSerializer(chuoi_kham, context={"request": request})
            data = serializer.data
            response = {
                "error": False, 
                "status": status.HTTP_200_OK,
                "message": "Chuoi Kham",
                "data": data
            }
            return Response(response)   

    def update(self, request, pk=None):
        try:
            queryset = ChuoiKham.objects.all()
            chuoi_kham = get_object_or_404(queryset, pk=pk)
            serializer = ChuoiKhamSerializer(chuoi_kham, data=request.data, context={"request": request})
            serializer.is_valid()
            serializer.save()
            response = {
                "error": False, 
                "status": status.HTTP_200_OK,
                "message": "Cap Nhat Chuoi Kham Thanh Cong",
                "data": serializer.data
            }
        except:
            response = {
                "error": True, 
                "status": status.HTTP_409_CONFLICT,
                "message": "Khong The Cap Nhat Chuoi Kham"
            }
        return Response(response)

    def destroy(self, request, pk=None):
        queryset = ChuoiKham.objects.all()
        chuoi_kham = get_object_or_404(queryset, pk=pk)
        chuoi_kham.delete()
        return Response({
            "error": False, 
            "status": status.HTTP_204_NO_CONTENT,
            "message": "Xoa Chuoi Kham Thanh Cong"
        })

    # TODO chuỗi khám sẽ query theo user, từng user sẽ có 1 list các chuỗi khám
    
    # TODO điều phối khám cho bệnh nhân 

class KetQuaTongQuatViewSet(viewsets.ModelViewSet):
    def list(self, request):
        ket_qua_tong_quat = KetQuaTongQuat.objects.all()
        serializer = KetQuaTongQuatSerializer(ket_qua_tong_quat, many=True, context={"request": request})
        response = {
            "error": False,
            "status": status.HTTP_200_OK,
            "message": "Danh Sach Ket Qua Tong Quat",
            "data": serializer.data        
        }
        return Response(response)

    def create(self, request):
        try:
            serializer = KetQuaTongQuatSerializer(data=request.data, context={"request": request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            response = {
                "error": False, 
                "status": status.HTTP_201_CREATED,
                "message": f"Them Ket Qua Tong Quat Thanh Cong"
            }
        except:
            response = {
                "error": True, 
                "status": status.HTTP_409_CONFLICT,
                "message": "Khong The Them Ket Qua Tong Quat"
            }
        return Response(response)

    def retrieve(self, request, pk=None):
        queryset = KetQuaTongQuat.objects.all()
        ket_qua_tong_quat = get_object_or_404(queryset, pk=pk)
        serializer = KetQuaTongQuatSerializer(ket_qua_tong_quat, context={"request": request})
        data = serializer.data
        response = {
            "error": False, 
            "status": status.HTTP_200_OK,
            "message": "Ket Qua Tong Quat",
            "data": data
        }
        return Response(response)   

    def update(self, request, pk=None):
        try:
            queryset = KetQuaTongQuat.objects.all()
            ket_qua_tong_quat = get_object_or_404(queryset, pk=pk)
            serializer = KetQuaTongQuatSerializer(ket_qua_tong_quat, data=request.data, context={"request": request})
            serializer.is_valid()
            serializer.save()
            response = {
                "error": False, 
                "status": status.HTTP_200_OK,
                "message": "Cap Nhat Ket Qua Tong Quat Thanh Cong",
                "data": serializer.data
            }
        except:
            response = {
                "error": True, 
                "status": status.HTTP_409_CONFLICT,
                "message": "Khong The Cap Nhat Ket Qua Tong Quat",
            }
        return Response(response)

    def destroy(self, request, pk=None):
        queryset = KetQuaTongQuat.objects.all()
        ket_qua_tong_quat = get_object_or_404(queryset, pk=pk)
        ket_qua_tong_quat.delete()
        return Response({
            "error": False, 
            "status": status.HTTP_204_NO_CONTENT,
            "message": "Xoa Ket Qua Tong Quat Thanh Cong"
        })
    
    # TODO kết quả tổng quát sẽ query theo chuỗi khám, mỗi chuỗi khám sẽ có một kết quả tổng quát

class KetQuaChuyenKhoaViewSet(viewsets.ModelViewSet):
    def list(self, request):
        ket_qua_chuyen_khoa = KetQuaChuyenKhoa.objects.all()
        serializer = KetQuaChuyenKhoaSerializer(ket_qua_chuyen_khoa, many=True, context={"request": request})
        response = {
            "error": False,
            "status": status.HTTP_200_OK,
            "message": "Danh Sach Ket Qua Chuyen Khoa",
            "data": serializer.data        
        }
        return Response(response)

    def create(self, request):
        try:
            serializer = KetQuaChuyenKhoaSerializer(data=request.data, context={"request": request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            response = {
                "error": False, 
                "status": status.HTTP_201_CREATED,
                "message": f"Them Ket Qua Chuyen Khoa Thanh Cong"
            }
        except:
            response = {
                "error": True, 
                "status": status.HTTP_409_CONFLICT,
                "message": "Khong The Them Ket Qua Chuyen Khoa"
            }
        return Response(response)

    def retrieve(self, request, pk=None):
        queryset = KetQuaChuyenKhoa.objects.all()
        ket_qua_chuyen_khoa = get_object_or_404(queryset, pk=pk)
        serializer = KetQuaChuyenKhoaSerializer(ket_qua_chuyen_khoa, context={"request": request})
        data = serializer.data
        response = {
            "error": False, 
            "status": status.HTTP_200_OK,
            "message": "Ket Qua Chuyen Khoa",
            "data": data
        }
        return Response(response)   

    def update(self, request, pk=None):
        try:
            queryset = KetQuaChuyenKhoa.objects.all()
            ket_qua_chuyen_khoa = get_object_or_404(queryset, pk=pk)
            serializer = KetQuaChuyenKhoaSerializer(ket_qua_chuyen_khoa, data=request.data, context={"request": request})
            serializer.is_valid()
            serializer.save()
            response = {
                "error": False, 
                "status": status.HTTP_200_OK,
                "message": "Cap Nhat Ket Qua Chuyen Khoa Thanh Cong",
                "data": serializer.data
            }
        except:
            response = {
                "error": True, 
                "status": status.HTTP_409_CONFLICT,
                "message": "Khong The Cap Nhat Ket Qua Chuyen Khoa",
            }
        return Response(response)

    def destroy(self, request, pk=None):
        queryset = KetQuaChuyenKhoa.objects.all()
        ket_qua_chuyen_khoa = get_object_or_404(queryset, pk=pk)
        ket_qua_chuyen_khoa.delete()
        return Response({
            "error": False, 
            "status": status.HTTP_204_NO_CONTENT,
            "message": "Xoa Ket Qua Chuyen Khoa Thanh Cong"
        })
    
    # TODO kết quả chuyên khoa sẽ query theo kết quả tổng quát, mỗi kết quả tổng quát sẽ có nhiều kết quả chuyên khoa

class DieuPhoiPhongChucNangView(views.APIView):

    def get_object(self, pk):
        try:
            return PhongChucNang.objects.get(pk=pk)
        except PhongChucNang.DoesNotExist:
            raise Http404
    
    def get(self, request, pk, format=None):
        phong_chuc_nang = self.get_object(pk=pk)
        dich_vu_kham = phong_chuc_nang.dich_vu_kham
        chuoi_kham = dich_vu_kham.dich_vu_kham.all()
        serializer = ChuoiKhamSerializerSimple(chuoi_kham, many=True, context={"request": request})
        return Response(serializer.data)

class FileKetQuaViewSet(viewsets.ModelViewSet):
    serializer_class = FileKetQuaSerializer
    queryset = FileKetQua.objects.all()


class ListNguoiDungDangKiKham(APIView):
    def get(self, request, format=None):
        queryset = LichHenKham.objects.select_related('benh_nhan').filter(trang_thai=4)
        serializer = LichHenKhamSerializer(queryset, many=True, context={'request': request})
        response = {
            "error": False,
            "status": status.HTTP_200_OK,
            "data": serializer.data
        }
        return Response(response)

class ChuoiKhamNguoiDung(APIView):
    def get(self, request, format=None):
        user_id = self.request.query_params.get('user_id', None)
        if user_id:
            chuoi_kham = ChuoiKham.objects.select_related('benh_nhan').filter(benh_nhan=user_id)
            serializer = ChuoiKhamSerializerSimple(chuoi_kham, many=True, context={"request": request})
            response = {
                "error": False,
                "status": status.HTTP_200_OK,
                "data": serializer.data
            }
            return Response(response)

class DanhSachThuocTheoCongTy(APIView):
    def get(self, request, format=None):
        id_cong_ty = self.request.query_params.get('id_cong_ty', None)
        if id_cong_ty:
            thuoc = Thuoc.objects.select_related('cong_ty').filter(cong_ty = id_cong_ty)
            serializer = ThuocSerializer(thuoc, many=True, context={"request":request})
            response = {
                "error" : False,
                "status" : status.HTTP_200_OK,
                "data" : serializer.data
            }
            return Response(response)
class DanhSachBenhNhanTheoPhong(APIView):
    def get(self, request, format=None):
        id_phong = self.request.query_params.get('id_phong', None)
        if id_phong:
            phong_chuc_nang = get_object_or_404(PhongChucNang, id=id_phong)
            # dich_vu_kham = 
            chuyen_khoa_kham = phong_chuc_nang.dich_vu_kham
            ds_phan_khoa_by_users = chuyen_khoa_kham.dich_vu_kham.all()
            serializer = PhanKhoaKhamSerializer(ds_phan_khoa_by_users, many=True, context={'request': request})
            response_data = {
                "error": False,
                "status": status.HTTP_200_OK,
                "data": serializer.data
            }
            return Response(response_data)
        # return Response({'key': serializer.data}, status=status.HTTP_200_OK)

# TODO Danh sách bệnh nhân theo phòng: nếu trạng thái chuỗi khám và phân khoa khám của bệnh nhân trở thành "Dừng Lại" thì sẽ filter exclude trạng thái "Dừng Lại"

class DanhSachDichVuKhamTheoPhong(APIView):
    def get(self, request, format=None):
        ten_phong_chuc_nang = self.request.query_params.get('ten_phong_chuc_nang')
        phong_chuc_nang = PhongChucNang.objects.filter(ten_phong_chuc_nang=ten_phong_chuc_nang)
        # dich_vu_kham = 
        danh_sach = PhanKhoaKham.objects.filter(dich_vu_kham__phong_chuc_nang_theo_dich_vu__ten_phong_chuc_nang=ten_phong_chuc_nang).distinct()

        serializer = PhanKhoaKhamSerializer(danh_sach, many=True, context={'request': request})
        # serializer = PhongChucNangSerializer(phong_chuc_nang, many=True, context={'request': request})
        response = {
            'data': serializer.data
        }
        return Response(response)

class DanhSachPhongChucNang(APIView):
    def get(self, request, format=None):
        phong_chuc_nang = PhongChucNang.objects.all()
        serializer = PhongChucNangSerializerSimple(phong_chuc_nang, many=True, context={"request": request})
        phong_chuc_nang_data = serializer.data
        return Response({"error":False, "message": "Danh Sach Phong Chuc Nang", "data": phong_chuc_nang_data})

        
class PhongChucNangTheoDichVu(APIView):
    def get(self, request, format=None):
        id_dich_vu = self.request.query_params.get('id_dich_vu', None)
        if id_dich_vu:
            dich_vu = get_object_or_404(DichVuKham, id=id_dich_vu)
            phong_chuc_nang = dich_vu.phong_chuc_nang_theo_dich_vu.all()
            data_phong = phong_chuc_nang[0]
            profile_phong_chuc_nang = data_phong.profile_phong_chuc_nang
            serializer = ProfilePhongChucNangSerializer(profile_phong_chuc_nang, context={'request': request})
            data = serializer.data
            # print(data)
            response_data = {
                'ten_phong_chuc_nang': data['phong_chuc_nang']['ten_phong_chuc_nang'],
                'so_luong_cho': data['so_luong_cho'],
                'thoi_gian_cho': data['thoi_gian_trung_binh'],
            }

            return Response(response_data)



class DanhSachHoaDonDichVu(generics.ListCreateAPIView):

    serializer_class = HoaDonChuoiKhamSerializerSimple
    pagination_class = CustomPagination

    def get_queryset(self):
        now = timezone.localtime(timezone.now())
        tomorrow = now + timedelta(1)
        today_start = now.replace(hour=0, minute=0, second=0)
        today_end = tomorrow.replace(hour=0, minute=0, second=0)
        queryset = ChuoiKham.objects.select_related('benh_nhan').filter(thoi_gian_tao__lt=today_end, thoi_gian_tao__gte=today_start).order_by('-id')

        term = self.request.query_params.get('query[search]')
        trang_thai = self.request.query_params.get('query[trang_thai_thanh_toan]')
        list_da_thanh_toan = []
        list_cho_thanh_toan = []

        for i in queryset:
            if i.check_thanh_toan():
                list_da_thanh_toan.append(i)
            else:
                list_cho_thanh_toan.append(i)

        if term is not None:
            queryset = queryset.filter(Q(benh_nhan__ho_ten__icontains=term)).order_by('-id')

        if trang_thai == "True":
            queryset = list_da_thanh_toan
        elif trang_thai == "False":
            queryset = list_cho_thanh_toan

        return queryset

class DanhSachHoaDonThuoc(generics.ListCreateAPIView):
    serializer_class = HoaDonThuocSerializerSimple
    pagination_class = CustomPagination

    def get_queryset(self):
        now = timezone.localtime(timezone.now())
        tomorrow = now + timedelta(1)
        today_start = now.replace(hour=0, minute=0, second=0)
        today_end = tomorrow.replace(hour=0, minute=0, second=0)

        queryset = DonThuoc.objects.select_related('benh_nhan').filter(thoi_gian_tao__gte=today_start, thoi_gian_tao__lt=today_end)

        term = self.request.query_params.get('query[search]')
        trang_thai = self.request.query_params.get('query[trang_thai_thanh_toan]')

        list_cho_thanh_toan = []
        list_da_thanh_toan = []

        for don_thuoc in queryset:
            if don_thuoc.check_thanh_toan():
                list_da_thanh_toan.append(don_thuoc)
            else:
                list_cho_thanh_toan.append(don_thuoc)

        if term is not None:
            queryset = queryset.filter(Q(benh_nhan__ho_ten__icontains=term) | Q(benh_nhan__so_dien_thoai__icontains=term))

        if trang_thai is not None:
            if trang_thai == 'True':
                queryset = list_da_thanh_toan
            else:
                queryset = list_cho_thanh_toan

        return queryset
        
class DanhSachDonThuocPhongThuoc(generics.ListCreateAPIView):
    serializer_class = HoaDonThuocSerializerSimple
    pagination_class = CustomPagination

    def get_queryset(self):
        now = timezone.localtime(timezone.now())
        tomorrow = now + timedelta(1)
        today_start = now.replace(hour=0, minute=0, second=0)
        today_end = tomorrow.replace(hour=0, minute=0, second=0)

        queryset = DonThuoc.objects.filter(thoi_gian_tao__gte=today_start, thoi_gian_tao__lt=today_end)

        term = self.request.query_params.get('query[search]')
        flag = self.request.query_params.get('query[trang_thai]')

        if term is not None:
            queryset = queryset.filter(Q(benh_nhan__ho_ten__icontains=term) | Q(benh_nhan_vang_lai__icontains=term) | Q(benh_nhan__so_dien_thoai__icontains=term))

        if flag is not None:
            trang_thai = TrangThaiDonThuoc.objects.get(id=flag)
            queryset = queryset.filter(trang_thai = trang_thai)

        return queryset

class DanhSachDonThuocDaKe(APIView):
    def get(self, request, format=None):
        trang_thai = TrangThaiDonThuoc.objects.get_or_create(trang_thai="Chờ Thanh Toán")[0]
        danh_sach_don_thuoc = DonThuoc.objects.select_related('benh_nhan').filter(trang_thai=trang_thai)
        serializer = HoaDonThuocSerializerSimple(danh_sach_don_thuoc, many=True, context={'request': request})
        data = serializer.data
        response_data = {
            'error': False, 
            'data': data
        }
        return Response(response_data)

class DanhSachThanhToanLamSang(generics.ListCreateAPIView):
    serializer_class = LichHenKhamSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        now = timezone.localtime(timezone.now())
        tomorrow = now + timedelta(1)
        today_start = now.replace(hour=0, minute=0, second=0)
        today_end = tomorrow.replace(hour=0, minute=0, second=0)
        queryset = LichHenKham.objects.select_related('benh_nhan').filter(thoi_gian_tao__gte=today_start, thoi_gian_tao__lt=today_end).order_by('-id')
        
        flag = self.request.query_params.get('query[trang_thai_thanh_toan]')
        term = self.request.query_params.get('query[search]')
        
        list_data_cho_thanh_toan = []
        list_data_da_thanh_toan = []

        for lich_hen in queryset:
            if lich_hen.check_thanh_toan():
                list_data_da_thanh_toan.append(lich_hen)
            else:
                list_data_cho_thanh_toan.append(lich_hen)

        if term is not None:
            queryset = queryset.filter(Q(ma_lich_hen__contains=term) | Q(benh_nhan__ho_ten__icontains=term))

        if flag is not None:
            if flag == "True":
                queryset = list_data_da_thanh_toan
            elif flag == "False":
                queryset = list_data_cho_thanh_toan

        return queryset

class ThongTinPhongChucNang(APIView):
    def get(self, request, format=None):
        id_dich_vu = self.request.query_params.get('id_dich_vu', None)
        if id_dich_vu:
            dich_vu = get_object_or_404(DichVuKham, id=id_dich_vu)
            phong_chuc_nang = dich_vu.phong_chuc_nang_theo_dich_vu.all()
            if len(phong_chuc_nang) == 0:
                response = {
                    'status': 400,
                    'message': "Không Tìm Thấy Thông Tin"
                }
                return Response(response)
            trang_thai_cho = TrangThaiKhoaKham.objects.get_or_create(trang_thai_khoa_kham='Đang chờ')[0]
            trang_thai_thuc_hien = TrangThaiKhoaKham.objects.get_or_create(trang_thai_khoa_kham='Đang Thực Hiện')[0]
            ds_benh_nhan = dich_vu.dich_vu_kham.select_related().filter(Q(trang_thai=trang_thai_cho) | Q(trang_thai=trang_thai_thuc_hien))
            ds_benh_nhan_dang_cho = dich_vu.dich_vu_kham.select_related().filter(trang_thai=trang_thai_cho)
            ds_benh_nhan_dang_thuc_hien = dich_vu.dich_vu_kham.select_related().filter(trang_thai=trang_thai_thuc_hien)
            if len(ds_benh_nhan) == 0:
                response = {
                    'status': 400,
                    'message': "Không Tìm Thấy Thông Tin"
                }
                return Response(response)
            so_luong = ds_benh_nhan.count()
            so_luong_cho = ds_benh_nhan_dang_cho.count()
            so_luong_thuc_hien = ds_benh_nhan_dang_thuc_hien.count()
            data_phong = phong_chuc_nang[0]
            open_div = "<div class='text-left'>"
            close_div = "</div>"
            html_ten_phong = f"<span class='head'>Phòng : </span><span>{data_phong.ten_phong_chuc_nang}</span><br/>"
            html_so_luong = f"<span class='head'>Tổng Số Người : </span><span>{so_luong}</span><br/>"
            html_so_luong_dang_cho = f"<span class='head'>Đang Chờ : </span><span>{so_luong_cho}</span><br/>"
            html_so_luong_dang_thuc_hien = f"<span class='head'>Đang Thực Hiện : </span><span>{so_luong_thuc_hien}</span><br/>"
            html = open_div + html_ten_phong + html_so_luong + html_so_luong_dang_cho + html_so_luong_dang_thuc_hien + close_div
            response_data = {
                'status': 200,
                'html': str(html)
            }
            
            return Response(response_data)

class DanhSachKhamTrongNgay(generics.ListCreateAPIView):
    serializer_class = ChuoiKhamSerializerSimple
    pagination_class = CustomPagination

    def get_queryset(self):
        now = timezone.localtime(timezone.now())
        tomorrow = now + timedelta(1)
        today_start = now.replace(hour=0, minute=0, second=0)
        today_end = tomorrow.replace(hour=0, minute=0, second=0)

        queryset = ChuoiKham.objects.select_related('benh_nhan').filter(thoi_gian_tao__gte=today_start, thoi_gian_tao__lt=today_end).order_by('-id')
        term = self.request.query_params.get('query[search]')
        flag = self.request.query_params.get('query[trang_thai]')

        if term is not None:
            queryset = queryset.filter(Q(benh_nhan__ho_ten__icontains=term) | Q(benh_nhan__so_dien_thoai__icontains=term)).order_by('-id')
    
        if flag is not None:
            trang_thai = TrangThaiChuoiKham.objects.get(id=flag)
            queryset = queryset.filter(trang_thai=trang_thai).order_by('-id')

        return queryset

class DanhSachPhongChucNang(APIView):
    def get(self, request, format=None):

        phong_chuc_nang = PhongChucNang.objects.all()
        serializer = PhongChucNangSerializerSimple(phong_chuc_nang, many=True, context={"request": request})
        phong_chuc_nang_data = serializer.data
        return Response({"error":False, "message": "Danh Sach Phong Chuc Nang", "data": phong_chuc_nang_data})
        
# UPDATE NGAY 4/1
# class DanhSachDoanhThuDichVu(APIView):
#     def get(self, request, format=None):
#         range_start = self.request.query_params.get('range_start', None)
#         range_end   = self.request.query_params.get('range_end', None)

#         start = datetime.strptime(range_start, "%d-%m-%Y")
#         tomorrow_start = start + timedelta(1)
        
#         if range_end == '':
#             danh_sach_dich_vu = HoaDonChuoiKham.objects.filter(Q(thoi_gian_tao__lt=tomorrow_start, thoi_gian_tao__gte=start) | Q(thoi_gian_tao__lt=tomorrow_start, thoi_gian_tao__gte=start))

#             serializer = HoaDonChuoiKhamSerializer(danh_sach_dich_vu, many=True, context={'request': request})
#             data = serializer.data

#             return Response(data)
#         else: 
#             end = datetime.strptime(range_end, "%d-%m-%Y")
#             tomorrow_end = end + timedelta(1)

#             danh_sach_dich_vu = HoaDonChuoiKham.objects.filter(Q(thoi_gian_tao__lt=tomorrow_end, thoi_gian_tao__gte=start) | Q(thoi_gian_tao__lt=end, thoi_gian_tao__gte=start))

#             serializer = HoaDonChuoiKhamSerializer(danh_sach_dich_vu, many=True, context={'request': request})
#             data = serializer.data

#             return Response(data)

class DanhSachDoanhThuDichVu(APIView):
    def get(self, request, format=None):
        range_start = self.request.query_params.get('range_start', None)
        range_end   = self.request.query_params.get('range_end', None)

        today_start = datetime.strptime(range_start, "%d-%m-%Y")
        
        list_dich_vu = []
        if range_end == '':       
            today_end = today_start + timedelta(1)
        else: 
            today_end = datetime.strptime(range_end, "%d-%m-%Y")
            if range_start == range_end:
                today_end = today_end + timedelta(1)
            
        hoa_don_chuoi_kham = HoaDonChuoiKham.objects.filter(thoi_gian_tao__lt=today_end, thoi_gian_tao__gte=today_start).exclude(Q(tong_tien__isnull=True) | Q(tong_tien=0.000)).values_list('chuoi_kham__phan_khoa_kham')
        list_id = [item for t in list(hoa_don_chuoi_kham) for item in t]
        
        danh_sach_dich_vu = PhanKhoaKham.objects.filter(pk__in=list_id).values('dich_vu_kham__ten_dvkt').annotate(tong_tien=Sum('dich_vu_kham__don_gia')).order_by('dich_vu_kham__ten_dvkt').annotate(dich_vu_kham_count = Count('dich_vu_kham__ten_dvkt'))
            
        # danh_sach_dich_vu = PhanKhoaKham.objects.filter(Q(thoi_gian_tao__lt=tomorrow_start, thoi_gian_tao__gte=start) | Q(thoi_gian_tao__lt=end, thoi_gian_tao__gte=start)).values('dich_vu_kham__phong_chuc_nang__ten_phong_chuc_nang').annotate(tong_tien=Sum('dich_vu_kham__don_gia')).order_by('dich_vu_kham__phong_chuc_nang__ten_phong_chuc_nang').annotate(dich_vu_kham_count = Count('dich_vu_kham__phong_chuc_nang__ten_phong_chuc_nang'))

        # list_tong_tien_without_format = [i['tong_tien'] for i in danh_sach_dich_vu]
        list_tong_tien_formatted = ["{:,}".format(int(i['tong_tien'])) for i in danh_sach_dich_vu]

        list_dich_vu = []
        for idx, val in enumerate(danh_sach_dich_vu):
            val['tong_tien'] = list_tong_tien_formatted[idx]
            list_dich_vu.append(val)
        
        response = {
            'data' : list_dich_vu,
        }
        return Response(response)

class DanhSachNguonCung(APIView):
    def get(self, request, format=None):
        nguon_cung = CongTy.objects.all()

        serializer = CongTySerializer(nguon_cung, many=True, context = {'request' : request})
        data = serializer.data
        
        response = {
            'data': data
        }
        return Response(response)

class DanhSachDoanhThuLamSang(APIView):
    def get(self, request, format=None):
        range_start = self.request.query_params.get('range_start', None)
        range_end   = self.request.query_params.get('range_end', None)

        start = datetime.strptime(range_start, "%d-%m-%Y")
        tomorrow_start = start + timedelta(1)
        
        if range_end == '':
            danh_sach_hoa_don = HoaDonLamSang.objects.filter(thoi_gian_tao__lt=tomorrow_start, thoi_gian_tao__gte=start)

            serializer = HoaDonLamSangSerializerFormatted(danh_sach_hoa_don, many=True, context={'request': request})
            data = serializer.data

            return Response(data)
        else: 
            end = datetime.strptime(range_end, "%d-%m-%Y")
            tomorrow_end = end + timedelta(1)

            danh_sach_hoa_don = HoaDonLamSang.objects.filter(Q(thoi_gian_tao__lt=tomorrow_end, thoi_gian_tao__gte=start) | Q(thoi_gian_tao__lt=end, thoi_gian_tao__gte=start))

            serializer = HoaDonLamSangSerializerFormatted(danh_sach_hoa_don, many=True, context={'request': request})
            data = serializer.data

            return Response(data)

class DanhSachDoanhThuThuoc(APIView):
    def get(self, request, format=None):
        range_start = self.request.query_params.get('range_start', None)
        range_end   = self.request.query_params.get('range_end', None)

        start = datetime.strptime(range_start, "%d-%m-%Y")
        
        if range_end == '':
            end = start + timedelta(1)
        else: 
            end = datetime.strptime(range_end, "%d-%m-%Y")
            if range_start == range_end:
                end = end + timedelta(1)
        danh_sach_hoa_don_thuoc = HoaDonThuoc.objects.filter(thoi_gian_tao__lt=end, thoi_gian_tao__gte=start)

        serializer = HoaDonThuocSerializer(danh_sach_hoa_don_thuoc, many=True, context={'request': request})
        data = serializer.data

        return Response(data)
       
    # END UPDATE 
class DanhSachBenhNhan(APIView):
    def get(self, request, format=None):
        danh_sach_benh_nhan = User.objects.filter(chuc_nang = 1)
        
        serializer = UserSerializer(danh_sach_benh_nhan, many=True, context={'request': request})
        data = serializer.data
        
        return Response(data)
    
class DanhSachBenhNhanListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = UserSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        queryset = User.objects.filter(chuc_nang=1)

        term = self.request.query_params.get('query[search]')
        sort_field = self.request.query_params.get('sort[field]')
        sort_type = self.request.query_params.get('sort[sort]')

        if term is not None:
            term = term.upper()
            queryset = queryset.filter(Q(ho_ten__icontains=term) | Q(so_dien_thoai__icontains=term) | Q(cmnd_cccd__contains=term))
        
        if sort_field is not None and sort_type is not None:
            if sort_type == "asc":
                queryset = queryset.order_by(f'{sort_field}')
            elif sort_type == "desc":
                queryset = queryset.order_by(f'-{sort_field}')  

        return queryset

from datetime import datetime, timedelta

class ThongTinBenhNhanTheoMa(APIView):
    def get(self, request, format = None):
        ma_benh_nhan = self.request.query_params.get('ma_benh_nhan')
        thong_tin_theo_ma = User.objects.get(id = ma_benh_nhan)

        serializer = UserSerializer(thong_tin_theo_ma, context={'request': request})

        data = {
            'thong_tin_theo_ma': serializer.data
        }

        return HttpResponse(json.dumps(data), content_type="application/json, charset=utf-8")
        # serializer = UserSerializer()


class DanhSachLichHenTheoBenhNhan(generics.ListCreateAPIView):
    serializer_class = LichHenKhamSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        range_start = self.request.query_params.get('range_start', None)
        range_end   = self.request.query_params.get('range_end', None)

        term = self.request.query_params.get('query[search]')
        sort_field = self.request.query_params.get('sort[field]')
        sort_type = self.request.query_params.get('sort[sort]')
        status = self.request.query_params.get('query[trang_thai]')

        start = datetime.strptime(range_start, "%d-%m-%Y")
        if range_end == '':
            end = start + timedelta(1)
        else:
            end = datetime.strptime(range_end, "%d-%m-%Y")
            if range_start == range_end:
                end = start + timedelta(1)

        queryset = LichHenKham.objects.select_related('benh_nhan').filter(thoi_gian_tao__gte=start, thoi_gian_tao__lt=end).order_by('-id')
        
        if term is not None:
            term = term.upper()
            queryset = queryset.filter(benh_nhan__ho_ten__icontains=term).order_by('-id')

        if status is not None:
            queryset = queryset.filter(trang_thai__id=status).order_by('-id')

        if sort_field is not None and sort_type is not None:
            if sort_type == 'asc':
                queryset = queryset.order_by(f'{sort_field}')
            elif sort_type == 'desc': 
                queryset = queryset.order_by(f'-{sort_field}')

        return queryset
    # def get(self, request, format=None):
    #     range_start = self.request.query_params.get('range_start', None)
    #     range_end   = self.request.query_params.get('range_end', None)

    #     start = datetime.strptime(range_start, "%d-%m-%Y")
    #     tomorrow_start = start + timedelta(1)

    #     if range_end == '':
    #         lich_hen = LichHenKham.objects.select_related('benh_nhan').filter(Q(thoi_gian_bat_dau__lt=tomorrow_start, thoi_gian_ket_thuc__gte=start) | Q(thoi_gian_bat_dau__lt=tomorrow_start, thoi_gian_bat_dau__gte=start))

    #     else:
    #         end = datetime.strptime(range_end, "%d-%m-%Y")
    #         tomorrow_end = end + timedelta(1)
    #         lich_hen = LichHenKham.objects.select_related('benh_nhan').filter(Q(thoi_gian_bat_dau__lt=end, thoi_gian_ket_thuc__gte=start) | Q(thoi_gian_bat_dau__lt=tomorrow_end, thoi_gian_bat_dau__gte=start))
            
    #     serializer = LichHenKhamSerializer(lich_hen, many=True, context={'request': request})

    #     data = serializer.data
    #     return Response(data)

class DanhSachDoanhThuTheoThoiGian(APIView):
    def get(self, request, format=None):
        range_start = self.request.query_params.get('range_start', None)
        range_end   = self.request.query_params.get('range_end', None)

        start = datetime.strptime(range_start, "%d-%m-%Y")

        if range_end == '':
            end = start + timedelta(1)
        else:
            end = datetime.strptime(range_end, "%d-%m-%Y")
            if range_start == range_end:
                end = end + timedelta(1)

        tong_tien_hoa_don_chuoi_kham_theo_thoi_gian = HoaDonChuoiKham.objects.filter(thoi_gian_tao__gt=start, thoi_gian_tao__lt=end).exclude(Q(tong_tien__isnull=True) | Q(tong_tien=0.000)).annotate(day=TruncDay("thoi_gian_tao")).values("day").annotate(c=Count("id")).annotate(total_spent=Sum(F("tong_tien")))

        list_tong_tien = [x['total_spent'] for x in tong_tien_hoa_don_chuoi_kham_theo_thoi_gian]
        tong_tien_dich_vu_kham = sum(list_tong_tien)
        
        tong_tien_lam_sang_theo_thoi_gian = HoaDonLamSang.objects.filter(thoi_gian_tao__gt=start, thoi_gian_tao__lt=end).exclude(tong_tien__isnull=True).annotate(day=TruncDay("thoi_gian_tao")).values("day").annotate(c=Count("id")).annotate(total_spent=Sum(F("tong_tien")))
        list_tong_tien_lam_sang = [x['total_spent'] for x in tong_tien_lam_sang_theo_thoi_gian]
        tong_tien_lam_sang = sum(list_tong_tien_lam_sang)

        tong_tien_dich_vu = tong_tien_dich_vu_kham + tong_tien_lam_sang
        tong_tien_dich_vu_formatted = "{:,}".format(int(tong_tien_dich_vu))

        tong_tien_hoa_don_thuoc_theo_thoi_gian = HoaDonThuoc.objects.filter( thoi_gian_tao__gt=start, thoi_gian_tao__lt=end).exclude(tong_tien__isnull=True).annotate(day=TruncDay("thoi_gian_tao")).values("day").annotate(c=Count("id")).annotate(total_spent=Sum(F("tong_tien")))
        list_tong_tien_don_thuoc = [x['total_spent'] for x in tong_tien_hoa_don_thuoc_theo_thoi_gian]

        tong_tien_don_thuoc = sum(list_tong_tien_don_thuoc)
        tong_tien_don_thuoc_formatted = "{:,}".format(int(tong_tien_don_thuoc))

        tong_doanh_thu = tong_tien_dich_vu + tong_tien_don_thuoc
        tong_doanh_thu_formatted = "{:,}".format(int(tong_doanh_thu))

        hoa_don_chuoi_kham = HoaDonChuoiKham.objects.filter(thoi_gian_tao__lt=end, thoi_gian_tao__gte=start).exclude(Q(tong_tien__isnull=True) | Q(tong_tien=0.000)).values_list('chuoi_kham__phan_khoa_kham')
        list_id = [item for t in list(hoa_don_chuoi_kham) for item in t]
        danh_sach_dich_vu = PhanKhoaKham.objects.filter(pk__in=list_id).values('dich_vu_kham__phong_chuc_nang__ten_phong_chuc_nang').annotate(tong_tien=Sum('dich_vu_kham__don_gia')).order_by('dich_vu_kham__phong_chuc_nang__ten_phong_chuc_nang').annotate(dich_vu_kham_count = Count('dich_vu_kham__phong_chuc_nang__ten_phong_chuc_nang'))
        list_tong_tien_without_format = [i['tong_tien'] for i in danh_sach_dich_vu]
        tong_tien_theo_phong = sum(list_tong_tien_without_format)
        tong_tien_theo_phong_formatted = "{:,}".format(int(tong_tien_theo_phong))

        response = [
            {   
                'type': 'tong_doanh_thu',
                'loai_doanh_thu': 'Tổng Doanh Thu',
                'thoi_gian_bat_dau': start,
                'thoi_gian_ket_thuc': end,
                'tong_tien': tong_doanh_thu_formatted
            },
            {   
                'type': 'doanh_thu_dich_vu',
                'loai_doanh_thu': 'Tổng Doanh Thu Dịch Vụ',
                'thoi_gian_bat_dau': start,
                'thoi_gian_ket_thuc': end,
                'tong_tien': tong_tien_dich_vu_formatted
            },
            {
                'type': 'doanh_thu_thuoc',
                'loai_doanh_thu': 'Tổng Doanh Thu Thuốc',
                'thoi_gian_bat_dau': start,
                'thoi_gian_ket_thuc': end,
                'tong_tien': tong_tien_don_thuoc_formatted
            },
            {
                'type': 'doanh_thu_phong_chuc_nang',
                'loai_doanh_thu': 'Tổng Doanh Thu Phòng Chức Năng',
                'thoi_gian_bat_dau': start,
                'thoi_gian_ket_thuc': end,
                'tong_tien': tong_tien_theo_phong_formatted
            },
            
        ]
        
        return Response(response)
       
class DoanhThuTheoPhongChucNang(APIView):
    def get(self, request, format=None):
        range_start = self.request.query_params.get('range_start', None)
        range_end   = self.request.query_params.get('range_end', None)

        start = datetime.strptime(range_start, "%d-%m-%Y")

        if range_end == '':
            end = start + timedelta(1)
        else: 
            end = datetime.strptime(range_end, "%d-%m-%Y")
            if range_start == range_end:
                end = end + timedelta(1)
        
        hoa_don_chuoi_kham = HoaDonChuoiKham.objects.filter(thoi_gian_tao__lt=end, thoi_gian_tao__gte=start).exclude(Q(tong_tien__isnull=True) | Q(tong_tien=0.000)).values_list('chuoi_kham__phan_khoa_kham')
        list_id = [item for t in list(hoa_don_chuoi_kham) for item in t]
        danh_sach_phong = PhanKhoaKham.objects.filter(pk__in=list_id).values('dich_vu_kham__phong_chuc_nang__ten_phong_chuc_nang').annotate(tong_tien=Sum('dich_vu_kham__don_gia')).order_by('dich_vu_kham__phong_chuc_nang__ten_phong_chuc_nang').annotate(dich_vu_kham_count = Count('dich_vu_kham__phong_chuc_nang__ten_phong_chuc_nang'))

        list_tong_tien_formatted = ["{:,}".format(int(i['tong_tien'])) for i in danh_sach_phong]

        list_phong = []
        for idx, val in enumerate(danh_sach_phong):
            val['tong_tien'] = list_tong_tien_formatted[idx]
            list_phong.append(val)
        
        response = {
            'data' : list_phong,
        }
        return Response(response)


class SetChoThanhToan(APIView):
    def get(self, request, format=None):
        id = self.request.query_params.get('id', None)
        user = request.user
        lich_hen = LichHenKham.objects.filter(id = id)[0]
        trang_thai = TrangThaiLichHen.objects.get_or_create(ten_trang_thai = "Chờ Thanh Toán Lâm Sàng")[0]

        lich_hen.trang_thai = trang_thai
        lich_hen.nguoi_phu_trach = user
        lich_hen.save()

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"first_process_user_{lich_hen.benh_nhan.id}", {
                'type':'first_process_notification',
            }
        )

        data = {
            "message" : "Thay đổi trạng thái thành công!"
        }

        return HttpResponse(json.dumps(data), content_type="application/json, charset=utf-8")

class SetXacNhanKham(APIView):
    def get(self, request, format=None):
        id = self.request.query_params.get('id', None)
        user = request.user
        lich_hen = LichHenKham.objects.filter(id = id)[0]
        trang_thai = TrangThaiLichHen.objects.get_or_create(ten_trang_thai = "Xác Nhận")[0]

        lich_hen.trang_thai = trang_thai
        lich_hen.nguoi_phu_trach = user
        lich_hen.save()

        data = {
            "message" : "Thay đổi trạng thái thành công"
        }

        return HttpResponse(json.dumps(data), content_type="application/json, charset=utf-8")

# class DanhSachKetQuaKhamChuyenKhoa(APIView):
#     def get(self, request, format=None):
#         id = self.request.query_params.get('id', None)

#         ket_qua_chuyen_khoa = KetQuaChuyenKhoa.objects.get(id)
        
# class HoaDonTongTheoNguoiDung(APIView):
#     def get(self, request, format = None)
#         benh_nhan
class PhanKhoaKhamBenhNhan(APIView):
    def get(self, request, format=None):
        user_id = self.request.query_params.get('user_id')
        now = timezone.localtime(timezone.now())
        tomorrow = now + timedelta(1)
        today_start = now.replace(hour=0, minute=0, second=0)
        today_end = tomorrow.replace(hour=0, minute=0, second=0)
        user = User.objects.get(id=user_id)
        
        chuoi_kham = ChuoiKham.objects.filter(benh_nhan=user, thoi_gian_tao__lt=today_end, thoi_gian_tao__gte=today_start).order_by('-thoi_gian_tao').first()
        if chuoi_kham:
            danh_sach_phan_khoa = chuoi_kham.phan_khoa_kham.all()
            # serializer = DanhSachPhanKhoaSerializer(danh_sach_phan_khoa, many=True, context={'request': request})
            serializer = DanhSachPhanKhoaSerializer(danh_sach_phan_khoa, many=True, context={'request': request})
            data = serializer.data
            response = {
                'benh_nhan': user_id,
                'data': data
            }
            return Response(response)
        else:
            response = {
                'benh_nhan': user_id,
                'data': []
              
            }
            return Response(response)
 
class DanhSachChuoiKhamBenhNhan(APIView):
    def get(self, request, format=None):
        user_id = self.request.query_params.get('user_id')
        user = User.objects.get(id=user_id)
        danh_sach_lich_hen = user.benh_nhan_hen_kham.all()
        serializer = LichHenKhamUserSerializer(danh_sach_lich_hen, many=True, context={'request': request})
        response = {
            'benh_nhan': user_id,
            'data': serializer.data
        }
        return Response(response)

class DanhSachKetQuaChuoiKhamBenhNhan(APIView):
    def get(self, request, format=None):
        user_id = self.request.query_params.get('user_id')
        user = User.objects.get(id=user_id)
        danh_sach_lich_hen = user.chuoi_kham.all()
        serializer = DanhSachKetQuaChuoiKhamSerializer(danh_sach_lich_hen, many=True, context={'request': request})
        response = {
            'benh_nhan': user_id,
            'data': serializer.data
        }
        return Response(response)

class ChuoiKhamGanNhat(APIView):
    def get(self, request, format=None):
        user_id = self.request.query_params.get('user_id')
        now = timezone.localtime(timezone.now())
        tomorrow = now + timedelta(1)
        today_start = now.replace(hour=0, minute=0, second=0)
        today_end = tomorrow.replace(hour=0, minute=0, second=0)
        user = User.objects.get(id=user_id)
        
        chuoi_kham = ChuoiKham.objects.filter(benh_nhan=user, thoi_gian_tao__lt=today_end, thoi_gian_tao__gte=today_start).order_by('-thoi_gian_tao').first()
        if chuoi_kham:
            serializer = ChuoiKhamSerializerSimple(chuoi_kham, context={'request': request})

            response = {
                "data": serializer.data,
            }
            return Response(response)
        else:
            response = {
                "data": '',
            }
            return Response(response)
        # return Response({'message': 'Loi'})
 
class KetQuaChuoiKhamBenhNhan(APIView):
    def get(self, request, format=None):
        chuoi_kham_id = self.request.query_params.get('id_chuoi_kham')
        chuoi_kham = ChuoiKham.objects.get(id=chuoi_kham_id)
        ket_qua_tong_quat = chuoi_kham.ket_qua_tong_quat.all()
        serializer = KetQuaTongQuatSerializer(ket_qua_tong_quat, many=True, context={'request': request})
        response = {
            'chuoi_kham': chuoi_kham_id,
            'data': serializer.data
        }
        return Response(response)

class KetQuaChuoiKhamBenhNhan2(APIView):
    def get(self, request, format=None):
        chuoi_kham_id = self.request.query_params.get('id_chuoi_kham')
        chuoi_kham = ChuoiKham.objects.filter(id=chuoi_kham_id).first()
        ket_qua_tong_quat = chuoi_kham.ket_qua_tong_quat.all().first()

        if ket_qua_tong_quat is not None:
            ket_qua_chuyen_khoa = ket_qua_tong_quat.ket_qua_chuyen_khoa.all()
            serializer = KetQuaChuyenKhoaSerializer(ket_qua_chuyen_khoa, many=True, context={'request': request})
            response = {
                'chuoi_kham': chuoi_kham_id,
                'data': serializer.data
            }
        else:
            response = {
                'chuoi_kham': chuoi_kham_id,
                'data': ''
            }
        return Response(response)
 
class DanhSachDonThuocBenhNhan(APIView):
    def get(self, request, format=None):
        user_id = self.request.query_params.get('user_id')
        user = User.objects.get(id = user_id)
        danh_sach_don_thuoc = user.don_thuoc.all()
        serializer = DanhSachDonThuocSerializer(danh_sach_don_thuoc, many=True, context={'request': request})
        response = {
            'benh_nhan': user_id,
            'data': serializer.data
        }
        return Response(response)

class DanhSachThuocBenhNhan(APIView):
    def get(self, request, format=None):
        don_thuoc_id = self.request.query_params.get('don_thuoc_id')
        don_thuoc = DonThuoc.objects.get(id=don_thuoc_id)
        danh_sach_thuoc = don_thuoc.ke_don.all()
        serializer = KeDonThuocSerializer(danh_sach_thuoc, many=True, context={'request': request})
        response = {
            'don_thuoc': int(don_thuoc_id),
            'data': serializer.data
        }
        return Response(response)
        # return HttpResponse(json.dumps(response, cls=UUIDEncoder))
 
# class DichVuKhamTheoPhongChucNang(APIView):
#     def get(request, self, format=None):
#         phong_chuc_nang = PhongChucNangSerializerSimple()
#         dich_vu_kham = DichVuKham.objects.all()

class DanhSachThuocHienTai(APIView):
    def get(self, request, format=None):
        user_id = self.request.query_params.get('user_id')
        now = timezone.localtime(timezone.now())
        tomorrow = now + timedelta(1)
        today_start = now.replace(hour=0, minute=0, second=0)
        today_end = tomorrow.replace(hour=0, minute=0, second=0)
        user = User.objects.get(id=user_id)
        don_thuoc = DonThuoc.objects.filter(benh_nhan=user, thoi_gian_tao__lt=today_end, thoi_gian_tao__gte=today_start).order_by("-thoi_gian_tao").first()
        if don_thuoc:
            danh_sach_thuoc = don_thuoc.ke_don.all()
            serializer = KeDonThuocSerializer(danh_sach_thuoc, many=True, context={'request': request})
            response = {
                'don_thuoc': don_thuoc.id,
                'data': serializer.data
            }
        else:
            response = {
                'don_thuoc': "",
                'data': []
            }
        return Response(response)

class DanhSachBenhNhanTheoPhongChucNang(generics.ListCreateAPIView):
    serializer_class = PhanKhoaKhamSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        now = timezone.localtime(timezone.now())
        tomorrow = now + timedelta(1)
        today_start = now.replace(hour=0, minute=0, second=0)
        today_end = tomorrow.replace(hour=0, minute=0, second=0)

        id_phong = self.request.query_params.get('id')
        phong = PhongChucNang.objects.get(id=id_phong)

        queryset = PhanKhoaKham.objects.filter(dich_vu_kham__phong_chuc_nang = phong, thoi_gian_tao__gte=today_start, thoi_gian_tao__lt=today_end).order_by('-id')
    
        term = self.request.query_params.get('query[search]')
        flag = self.request.query_params.get('query[trang_thai]')

        if term is not None:
            queryset = queryset.filter(Q(benh_nhan__ho_ten__icontains=term) | Q(dich_vu_kham__ten_dvkt__icontains=term) | Q(benh_nhan__so_dien_thoai__icontains=term)).order_by('-id')

        if flag is not None:
            trang_thai = TrangThaiKhoaKham.objects.get(id=flag)
            queryset = queryset.filter(trang_thai=trang_thai).order_by('-id')

        return queryset
                
class DanhSachDichVuTheoPhongChucNang(APIView):
    def get(self, request, format=None):
        id_phong_chuc_nang = self.request.query_params.get('id_phong_chuc_nang', None)
        if id_phong_chuc_nang:
            dich_vu_kham = DichVuKham.objects.select_related('phong_chuc_nang').filter(phong_chuc_nang = id_phong_chuc_nang)
            serializer = DichVuKhamSerializer(dich_vu_kham, many=True, context={"request":request})
            response = {
                "error" : False,
                "status": status.HTTP_200_OK,
                "data"  : serializer.data
            }
            return Response(response)
        
class LichHenKhamSapToi(APIView):
    def get(self, request, format=None):
        user_id = self.request.query_params.get('user_id')
        user = User.objects.get(id=user_id)
        now = timezone.now()
        trang_thai = TrangThaiLichHen.objects.get_or_create(ten_trang_thai="Xác Nhận")[0]
        try:
            lich_hen_kham = LichHenKham.objects.filter(benh_nhan=user).filter(trang_thai=trang_thai).annotate(timediff=F('thoi_gian_bat_dau')).order_by('timediff')[0]
            
            if lich_hen_kham:
                # print(lich_hen_kham.thoi_gian_bat_dau)
                # if lich_hen_kham.thoi_gian_bat_dau <= now:
                #    return Response({'data': []})
                serializer = LichHenKhamSerializer(lich_hen_kham, context={'request': request})
                response = {
                    'data': serializer.data
                }
                return Response(response)
            else:
                response = {
                    'data': []
                }
                return Response(response)
        except :
            return Response({'data': []})
        
class DonThuocGanNhat(APIView):
    def get(self, request, format=None):
        user_id = self.request.query_params.get("user_id")
        user = User.objects.get(id=user_id)
        now = timezone.localtime(timezone.now())
        tomorrow = now + timedelta(1)
        today_start = now.replace(hour=0, minute=0, second=0)
        today_end = tomorrow.replace(hour=0, minute=0, second=0)
        user = User.objects.get(id=user_id)
        
        
        don_thuoc = DonThuoc.objects.filter(benh_nhan=user, thoi_gian_tao__lt=today_end, thoi_gian_tao__gte=today_start).order_by("-thoi_gian_tao").first()
        if don_thuoc:
            serializer = DonThuocSerializer(don_thuoc, context={'request': request})
            response = {
                'data': serializer.data
            }
            return Response(response)
        else:
            response = {
                'data': ''
            }
            return Response(response)

class TatCaLichHenBenhNhan(APIView):
    def get(self, request, format=None):
        user_id = self.request.query_params.get('user_id')
        user = User.objects.get(id=user_id)
        now = timezone.localtime(timezone.now())
        trang_thai = TrangThaiLichHen.objects.get_or_create(
            ten_trang_thai='Xác Nhận')[0]
        trang_thai_dat_truoc = TrangThaiLichHen.objects.get_or_create(
            ten_trang_thai='Đã Đặt Trước')[0]

        lich_hen = LichHenKham.objects.filter(benh_nhan=user).filter(Q(trang_thai=trang_thai) | Q(trang_thai=trang_thai_dat_truoc)).annotate(relevance=models.Case(
            models.When(thoi_gian_bat_dau__gte=now, then=1),
            models.When(thoi_gian_bat_dau__lt=now, then=2),
            output_field=models.IntegerField(),
        )).annotate(
            timediff=models.Case(
                models.When(thoi_gian_bat_dau__gte=now,
                            then=F('thoi_gian_bat_dau') - now),
                models.When(thoi_gian_bat_dau__lt=now,
                            then=now - F('thoi_gian_bat_dau')),
                # models.When(thoi_gian_bat_dau__lte=today_end - F('thoi_gian_bat_dau')),
                output_field=models.DurationField(),
            )).order_by('relevance', 'timediff')

        upcoming_events = []
        past_events = []
        for lich in lich_hen:
            if lich.relevance == 1:
                upcoming_events.append(lich)
            elif lich.relevance == 2:
                past_events.append(lich)

        serializer_1 = LichHenKhamSerializer(
            upcoming_events, many=True, context={'request': request})
        serializer_2 = LichHenKhamSerializer(
            past_events, many=True, context={'request': request})
        response = {
            'benh_nhan': user_id,
            'upcoming': serializer_1.data,
            'past': serializer_2.data,
        }

        return Response(response)

class DangKiLichHen(APIView):
    def post(self, request, format=None):
        serializer = BookLichHenKhamSerializer(data=request.data)

        if serializer.is_valid():
            user_id = serializer.validated_data['benh_nhan']
            thoi_gian_bat_dau = serializer.validated_data['thoi_gian_bat_dau']
            loai_dich_vu = serializer.validated_data['loai_dich_vu']
            ly_do = serializer.validated_data['ly_do']

            user = User.objects.get(id=user_id)
            date_time_str = datetime.strptime(thoi_gian_bat_dau, '%Y-%m-%d %H:%M:%S')
            trang_thai = TrangThaiLichHen.objects.get_or_create(ten_trang_thai='Đã Đặt Trước')[0]
            lich_hen = LichHenKham.objects.create(
                benh_nhan=user,
                thoi_gian_bat_dau=date_time_str, 
                trang_thai=trang_thai,
                loai_dich_vu=loai_dich_vu,
                ly_do=ly_do,
                
            )
            serializer_1 = LichHenKhamSerializerSimple(lich_hen, context={'request': request})
            serializer_2 = UserSerializer(user, context={'request': request})
            response = {
                'benh_nhan': serializer_2.data,
                'lich_hen': serializer_1.data,
            }
        else:
            response = {
                'status': status.HTTP_500_INTERNAL_SERVER_ERROR,
                'benh_nhan': "",
                'lich_hen': ''
            }
        return Response(response)

class UserInfor(APIView):
    def get(self, request, format=None):
        user_id = self.request.query_params.get('user_id')
        user = User.objects.get(id=user_id)
        serializer = UserSerializer(user, context={'request': request})
        response = {
            'user': serializer.data
        }
        return Response(response)

class DanhSachBacSi(APIView):
    def get(self, request, format=None):
        danh_sach_bac_si = User.objects.filter(Q(chuc_nang = 4) | Q(chuc_nang = 3))
        if len(danh_sach_bac_si) == 0: 
            response = {
            'data': []
        }
        else:
            serializer = UserSerializer(danh_sach_bac_si, many=True, context={'request': request})
            response = {
                'data': serializer.data
            }
        return Response(response)


class DanhSachBaiDang(generics.ListCreateAPIView):
    serializer_class = BaiDangSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        queryset = BaiDang.objects.all()

        term = self.request.query_params.get('query[search]')
        sort_field = self.request.query_params.get('sort[field]')
        sort_type = self.request.query_params.get('sort[sort]')

        if term is not None:
            queryset = queryset.filter(Q(tieu_de__icontains=term) | Q(tieu_de__icontains=term.upper()))

        if sort_field is not None and sort_type is not None:
            if sort_type == 'asc':
                queryset = queryset.order_by(f'{sort_field}')
            elif sort_type == 'desc':
                queryset = queryset.order_by(f'-{sort_field}')
            
        return queryset
    
class DanhSachDichVu(APIView):
    def get(self, request, format=None):
        danh_sach_dich_vu = DichVuKham.objects.all()
        serializer = DichVuKhamSerializer(danh_sach_dich_vu, many=True, context={'request': request})
        return Response(serializer.data)

class DichVuKhamPagination(pagination.PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 1000

# class PaginatedDichVuKhamListView(generics.ListAPIView):
#     queryset = DichVuKham.objects.all()
#     serializer_class = DichVuKhamSerializerSimple
#     pagination_class = DichVuKhamPagination

class DanhSachPhongChucNang(APIView):
    def get(self, request, format=None):   
        ds = PhongChucNang.objects.all()
        serializer = PhongChucNangSerializerSimple(ds, many=True, context={'request': request})
        response = {
            'data': serializer.data
        }
        return Response(response)
        
class DanhSachVatTu(APIView):
    def get(self, request, format=None):
        vat_tu = VatTu.objects.all()
        serializer = VatTuSerializer(vat_tu, many=True, context={'request': request})
        response = {
            'data' : serializer.data
        }
        return Response(response)

class UserUpdateInfo(APIView):
    def get(self, request, format=None):
        user_id = self.request.query_params.get("user_id")
        try:
            user = User.objects.get(id=user_id)
            serializer = UserUpdateInfoSerializer(
                user, context={'request': request})
            data = serializer.data
            response = {
                'status': status.HTTP_200_OK,
                'data': data
            }
        except:
            response = {
                'status': status.HTTP_404_NOT_FOUND,
                'data': ''
            }
        return Response(response)


class UserUpdateInfoRequest(APIView):
    def patch(self, request, format=None):
        serializer = UserUpdateInfoRequestSerializer(data=request.data)
        if serializer.is_valid():
            user_id = serializer.validated_data['benh_nhan']
            ho_ten = serializer.validated_data['ho_ten']
            so_dien_thoai = serializer.validated_data['so_dien_thoai']
            email = serializer.validated_data['email']
            cmnd_cccd = serializer.validated_data['cmnd_cccd']
            ngay_sinh = serializer.validated_data['ngay_sinh']
            gioi_tinh = serializer.validated_data['gioi_tinh']
            dia_chi = serializer.validated_data['dia_chi']
            dan_toc = serializer.validated_data['dan_toc']
            ma_so_bao_hiem = serializer.validated_data['ma_so_bao_hiem']
            try:
                user = User.objects.get(id=user_id)
                user.ho_ten = ho_ten
                user.so_dien_thoai = so_dien_thoai
                user.email = email
                user.cmnd_cccd = cmnd_cccd
                user.ngay_sinh = ngay_sinh
                user.gioi_tinh = gioi_tinh
                user.dia_chi = dia_chi
                user.dan_toc = dan_toc
                user.ma_so_bao_hiem = ma_so_bao_hiem
                user.save()

                response = {
                    'status': status.HTTP_200_OK,
                    'message': "Cập Nhật Thông Tin Cá Nhân Thành Công"
                }

            except User.DoesNotExist:
                response = {
                    'status': status.HTTP_404_NOT_FOUND,
                    'message': "Người Dùng Không Tồn Tại"
                }
        else:
            response = {
                'status': status.HTTP_500_INTERNAL_SERVER_ERROR,
                'message': "Bạn Vui Lòng Nhập Đầy Đủ Thông Tin"
            }
        return Response(response)


class ImageUploadParser(FileUploadParser):
    media_type = 'image/*'


class UploadAvatarView(APIView):
    parser_classes = (MultiPartParser,)

    def put(self, request, format=None):
        id = request.GET.get('id')
        file = request.FILES.get('file')

        user = User.objects.get(id=id)
        user.anh_dai_dien = file
        user.save()

        return Response({'message': "oke"})


class UpdateAppointmentDetail(APIView):
    def get(self, request, format=None):
        appointment_id = self.request.query_params.get('appointment_id')

        try:
            lich_hen = LichHenKham.objects.get(id=appointment_id)
            serializer = AppointmentUpdateDetailSerializer(
                lich_hen, context={'request': request})
            response = {
                'status': status.HTTP_200_OK,
                'message': 'Thông Tin Lịch Khám',
                'data': serializer.data,
            }
        except LichHenKham.DoesNotExist:
            response = {
                'status': status.HTTP_404_NOT_FOUND,
                'message': 'Lịch Hẹn Không Tồn Tại',
                'data': '',
            }
        return Response(response)


class CapNhatLichHen(APIView):
    def post(self, request, format=None):
        serializer = UpdateLichHenKhamSerializer(data=request.data)

        if serializer.is_valid():
            lich_hen_id = serializer.validated_data['appointment_id']
            thoi_gian_bat_dau = serializer.validated_data['thoi_gian_bat_dau']
            loai_dich_vu = serializer.validated_data['loai_dich_vu']
            ly_do = serializer.validated_data['ly_do']
            dia_diem = serializer.validated_data['dia_diem']

            date_time_str = datetime.strptime(
                thoi_gian_bat_dau, '%Y-%m-%d %H:%M:%S')
            try:
                lich_hen = LichHenKham.objects.get(id=lich_hen_id)
                lich_hen.loai_dich_vu = loai_dich_vu
                lich_hen.ly_do = ly_do
                lich_hen.dia_diem = dia_diem
                lich_hen.thoi_gian_bat_dau = date_time_str
                lich_hen.save()

                response = {
                    'status': status.HTTP_200_OK,
                    'message': 'Cập Nhật Lịch Hẹn Thành Công',
                }
            except LichHenKham.DoesNotExist:
                response = {
                    'status': status.HTTP_404_NOT_FOUND,
                    'message': 'Không Tìm Thấy Lịch Hẹn',
                }
        else:
            response = {
                'status': status.HTTP_500_INTERNAL_SERVER_ERROR,
                'message': 'Bạn Vui Lòng Xem Lại',
            }
        return Response(response)


class HoaDonChuoiKhamNguoiDung(APIView):
    def get(self, request, format=None):
        chuoi_kham_id = self.request.query_params.get('id_chuoi_kham')
        chuoi_kham = ChuoiKham.objects.get(id=chuoi_kham_id)
        hoa_don_dich_vu = chuoi_kham.hoa_don_dich_vu
        phan_khoa_kham = chuoi_kham.phan_khoa_kham.all()
        tong_tien = []
        for khoa_kham in phan_khoa_kham:
            if khoa_kham.bao_hiem:
                # gia = khoa_kham.dich_vu_kham.don_gia * decimal.Decimal((1 - (khoa_kham.dich_vu_kham.bao_hiem_dich_vu_kham.dang_bao_hiem)/100))
                gia = khoa_kham.dich_vu_kham.don_gia
            else:
                gia = khoa_kham.dich_vu_kham.don_gia
            tong_tien.append(gia)
        total_spent = sum(tong_tien)
        tong_tien.clear()


class HoaDonChuoiKhamCanThanhToan(APIView):
    def get(self, request, format=None):
        user_id = self.request.query_params.get('user_id')
        now = timezone.localtime(timezone.now())
        tomorrow = now + timedelta(1)
        today_start = now.replace(hour=0, minute=0, second=0)
        today_end = tomorrow.replace(hour=0, minute=0, second=0)
        user = User.objects.get(id=user_id)

        try:
            chuoi_kham = ChuoiKham.objects.filter(
                benh_nhan=user, thoi_gian_tao__lt=today_end, thoi_gian_tao__gte=today_start).order_by('-thoi_gian_tao').first()

            danh_sach_phan_khoa = chuoi_kham.phan_khoa_kham.all()
            tong_tien = []
            bao_hiem = []
            for khoa_kham in danh_sach_phan_khoa:
                if khoa_kham.bao_hiem:
                    # gia = khoa_kham.dich_vu_kham.don_gia * decimal.Decimal((1 - (khoa_kham.dich_vu_kham.bao_hiem_dich_vu_kham.dang_bao_hiem)/100))
                    gia = khoa_kham.dich_vu_kham.don_gia
                    bao_hiem.append(gia)
                else:
                    gia = khoa_kham.dich_vu_kham.don_gia
                tong_tien.append(gia)
            total_spent = sum(tong_tien)
            tong_bao_hiem = sum(bao_hiem)
            thanh_tien = total_spent - tong_bao_hiem
            tong_tien.clear()
            bao_hiem.clear()
            serializer = HoaDonChuoiKhamThanhToanSerializer(
                danh_sach_phan_khoa, many=True, context={'request': request})
            response = {
                'tong_tien': float(total_spent),
                'ap_dung_bao_hiem': float(tong_bao_hiem),
                'thanh_tien': float(thanh_tien),
                'data': serializer.data,
            }
        except:
            response = {
                'tong_tien': '',
                'ap_dung_bao_hiem': '',
                'thanh_tien': '',
                'data': [],
            }

        return Response(response)


class HoaDonThuocCanThanhToan(APIView):
    def get(self, request, format=None):

        user_id = self.request.query_params.get("user_id")
        now = timezone.localtime(timezone.now())
        tomorrow = now + timedelta(1)
        today_start = now.replace(hour=0, minute=0, second=0)
        today_end = tomorrow.replace(hour=0, minute=0, second=0)
        user = User.objects.get(id=user_id)
        try:
            don_thuoc = DonThuoc.objects.filter(
                benh_nhan=user, thoi_gian_tao__lt=today_end, thoi_gian_tao__gte=today_start).order_by('-thoi_gian_tao').first()

            danh_sach_thuoc = don_thuoc.ke_don.all()
            bao_hiem = []
            tong_tien = []
            for thuoc_instance in danh_sach_thuoc:
                if thuoc_instance.bao_hiem:
                    gia = int(thuoc_instance.thuoc.don_gia_tt) * \
                        thuoc_instance.so_luong
                    bao_hiem.append(gia)
                else:
                    gia = int(thuoc_instance.thuoc.don_gia_tt) * \
                        thuoc_instance.so_luong
                tong_tien.append(gia)

            total_spent = sum(tong_tien)
            tong_bao_hiem = sum(bao_hiem)
            thanh_tien = total_spent - tong_bao_hiem
            bao_hiem.clear()
            tong_tien.clear()
            serializer = DanhSachThuocSerializer(danh_sach_thuoc, many=True, context={'request': request})
            response = {
                'tong_tien': int(total_spent),
                'ap_dung_bao_hiem': int(tong_bao_hiem),
                'thanh_tien': int(thanh_tien),
                'data': serializer.data,
            }
        except:
            response = {
                'tong_tien': '',
                'ap_dung_bao_hiem': '',
                'thanh_tien': '',
                'data': [],
            }
        return Response(response)
        
# * update themm

class DichVuTheoPhongChucNang(APIView):
    def get(self, request, format=None):
        id_phong_chuc_nang = self.request.query_params.get('id_phong')
        try:
            phong_chuc_nang = PhongChucNang.objects.get(id=id_phong_chuc_nang)
            danh_sach_dich_vu = phong_chuc_nang.dich_vu_kham_theo_phong.all()
            serializer = DanhSachDichVuSerializer(danh_sach_dich_vu, many=True, context={'request': request})
            response = {
                'status': status.HTTP_200_OK,
                'message': 'Danh Sách Dịch Vụ Khám Theo Phòng Chức Năng',
                'data': serializer.data,
            }
        except PhongChucNang.DoesNotExist:
            response = {
                'status': status.HTTP_404_NOT_FOUND,
                'message': 'Không Có Dữ Liệu',
                'data': [],
            }
        return Response(response)
        
#* update 25/12

class DonThuocCuaChuoiKham(APIView):
    def get(self, request, format=None):
        id_chuoi_kham = self.request.query_params.get('id_chuoi_kham')
        try:
            chuoi_kham = ChuoiKham.objects.get(id=id_chuoi_kham)
            don_thuoc = chuoi_kham.don_thuoc_chuoi_kham.all().last()
            danh_sach_thuoc = don_thuoc.ke_don.all()
    
            serializer = KeDonThuocSerializer(danh_sach_thuoc, many=True, context={'request': request})
            response = {
                'don_thuoc': don_thuoc.id,
                'data': serializer.data
            }
        except ChuoiKham.DoesNotExist:
            response = {
                'don_thuoc': "",
                'data': []
            }
        return Response(response)
        
class HoaDonThuocCuaChuoiKham(APIView):
    def get(self, request, format = None):
        id_chuoi_kham = self.request.query_params.get('id_chuoi_kham')
        try:
            chuoi_kham = ChuoiKham.objects.get(id=id_chuoi_kham)
            don_thuoc = chuoi_kham.don_thuoc_chuoi_kham.all()[0]

            danh_sach_thuoc = don_thuoc.ke_don.all()
            bao_hiem = []
            tong_tien = []
            for thuoc_instance in danh_sach_thuoc:
                if thuoc_instance.bao_hiem:
                    gia = int(thuoc_instance.thuoc.don_gia_tt) * \
                        thuoc_instance.so_luong
                    bao_hiem.append(gia)
                else:
                    gia = int(thuoc_instance.thuoc.don_gia_tt) * \
                        thuoc_instance.so_luong
                tong_tien.append(gia)

            total_spent = sum(tong_tien)
            tong_bao_hiem = sum(bao_hiem)
            thanh_tien = total_spent - tong_bao_hiem
            bao_hiem.clear()
            tong_tien.clear()
            serializer = DanhSachThuocSerializer(danh_sach_thuoc, many=True, context={'request': request})
            response = {
                'tong_tien': total_spent,
                'ap_dung_bao_hiem': tong_bao_hiem,
                'thanh_tien': thanh_tien,
                'data': serializer.data,
            }
        except ChuoiKham.DoesNotExist:
            response = {
                'tong_tien': '',
                'ap_dung_bao_hiem': '',
                'thanh_tien': '',
                'data': [],
            }
        return Response(response)
        
class HoaDonDichVuCuaChuoiKham(APIView):
    def get(self, request, format=None):
        id_chuoi_kham = self.request.query_params.get('id_chuoi_kham')
        try:
            chuoi_kham = ChuoiKham.objects.get(id=id_chuoi_kham)
            danh_sach_phan_khoa = chuoi_kham.phan_khoa_kham.all()
            tong_tien = []
            bao_hiem = []
            for khoa_kham in danh_sach_phan_khoa:
                if khoa_kham.bao_hiem:
                    # gia = khoa_kham.dich_vu_kham.don_gia * decimal.Decimal((1 - (khoa_kham.dich_vu_kham.bao_hiem_dich_vu_kham.dang_bao_hiem)/100))
                    gia = khoa_kham.dich_vu_kham.don_gia
                    bao_hiem.append(gia)
                else:
                    gia = khoa_kham.dich_vu_kham.don_gia
                tong_tien.append(gia)
            total_spent = sum(tong_tien)
            tong_bao_hiem = sum(bao_hiem)
            thanh_tien = total_spent - tong_bao_hiem
            tong_tien.clear()
            bao_hiem.clear()
            serializer = HoaDonChuoiKhamThanhToanSerializer(
                danh_sach_phan_khoa, many=True, context={'request': request})
            response = {
                'tong_tien': float(total_spent),
                'ap_dung_bao_hiem': float(tong_bao_hiem),
                'thanh_tien': float(thanh_tien),
                'data': serializer.data,
            }
        except ChuoiKham.DoesNotExist:
             response = {
                'tong_tien': '',
                'ap_dung_bao_hiem': '',
                'thanh_tien': '',
                'data': [],
            }
        return Response(response)

class HoaDonThuocCuaChuoiKham(APIView):
    def get(self, request, format = None):
        id_chuoi_kham = self.request.query_params.get('id_chuoi_kham')
        try:
            chuoi_kham = ChuoiKham.objects.get(id=id_chuoi_kham)
            don_thuoc = chuoi_kham.don_thuoc_chuoi_kham.all().last()

            danh_sach_thuoc = don_thuoc.ke_don.all()
            bao_hiem = []
            tong_tien = []
            for thuoc_instance in danh_sach_thuoc:
                if thuoc_instance.bao_hiem:
                    gia = int(thuoc_instance.thuoc.don_gia_tt) * \
                        thuoc_instance.so_luong
                    bao_hiem.append(gia)
                else:
                    gia = int(thuoc_instance.thuoc.don_gia_tt) * \
                        thuoc_instance.so_luong
                tong_tien.append(gia)

            total_spent = sum(tong_tien)
            tong_bao_hiem = sum(bao_hiem)
            thanh_tien = total_spent - tong_bao_hiem
            bao_hiem.clear()
            tong_tien.clear()
            serializer = DanhSachThuocSerializer(danh_sach_thuoc, many=True, context={'request': request})
            response = {
                'tong_tien': int(total_spent),
                'ap_dung_bao_hiem': int(tong_bao_hiem),
                'thanh_tien': int(thanh_tien),
                'data': serializer.data,
            }
        except ChuoiKham.DoesNotExist:
            response = {
                'tong_tien': '',
                'ap_dung_bao_hiem': '',
                'thanh_tien': '',
                'data': [],
            }
        return Response(response)

class HoaDonLamSangChuoiKham(APIView):
    def get(self, request, format=None):
        id_lich_hen = self.request.query_params.get('id_lich_hen')
        try:
            lich_hen = LichHenKham.objects.get(id=id_lich_hen)
            hoa_don_lam_sang = lich_hen.hoa_don_lam_sang.all()[0]
            serializer = HoaDonLamSangSerializer(hoa_don_lam_sang, context={'request': request})
            response = {
                'data': serializer.data
            }
        except LichHenKham.DoesNotExist:
            response = {
                'data': []
            }
        return Response(response)
        
class HoaDonLamSangGanNhat(APIView):
    def get(self, request, format=None):
        user_id = self.request.query_params.get("user_id")
        now = timezone.localtime(timezone.now())
        tomorrow = now + timedelta(1)
        today_start = now.replace(hour=0, minute=0, second=0)
        today_end = tomorrow.replace(hour=0, minute=0, second=0)
        user = User.objects.get(id=user_id)
        try:
            lich_hen = LichHenKham.objects.filter(benh_nhan=user, thoi_gian_bat_dau__gt=today_start, thoi_gian_bat_dau__lt=today_end).order_by('-thoi_gian_tao').first()
            hoa_don_lam_sang = lich_hen.hoa_don_lam_sang.all()[0]
            serializer = HoaDonLamSangSerializer(hoa_don_lam_sang, context={'request': request})
            response = {
                'data': serializer.data,
            }
        except:
            response = {
                'data': []
            }
        return Response(response)
        
class DanhSachBacSi1(APIView):
    def get(request, self, format=None):
        danh_sach_bac_si = BacSi.objects.all()

        serializer = DanhSachBacSiSerializer(danh_sach_bac_si, many=True, context={'request': request})
        data = serializer.data
       	response = {
            'data': data
        }
        return Response(response)

class DanhSachHoaDonDichVuBaoHiem(APIView):
    def get(self, request, format=None):
        range_start = self.request.query_params.get('range_start', None)
        range_end   = self.request.query_params.get('range_end', None)
 
        start = datetime.strptime(range_start, "%d-%m-%Y")
        tomorrow_start = start + timedelta(1)
        # hoa_don_phan_khoa = []

        if range_end == '':
            hoa_don_dich_vu = HoaDonChuoiKham.objects.filter(thoi_gian_tao__lt=tomorrow_start, thoi_gian_tao__gte=start)

        else:
            end = datetime.strptime(range_end, "%d-%m-%Y")
            if range_start == range_end:
                end = end + timedelta(1)
            hoa_don_dich_vu = HoaDonChuoiKham.objects.filter(thoi_gian_tao__lt=end, thoi_gian_tao__gte=start)
        
        serializer = HoaDonChuoiKhamSerializer(hoa_don_dich_vu, many=True, context={'request': request})

        response = {
            'data': serializer.data,
        }

        # hoa_don_phan_khoa.clear()
        return Response(response)
        
class DanhSachHoaDonThuocBaoHiem(APIView):
    def get(self, request, format=None):
        range_start = self.request.query_params.get('range_start', None)
        range_end  = self.request.query_params.get('range_end', None)

        start = datetime.strptime(range_start, "%d-%m-%Y")
        tomorrow_start = start + timedelta(1)

        if range_end == '':
            hoa_don_thuoc = HoaDonThuoc.objects.filter(bao_hiem = True).filter(thoi_gian_tao__lte=tomorrow_start, thoi_gian_tao__gt=start)

        else :
            end = datetime.strptime(range_end, "%d-%m-%Y")
            if range_start == range_end:
                end = end + timedelta(1)
            hoa_don_thuoc = HoaDonThuoc.objects.filter(bao_hiem = True).filter(thoi_gian_tao__lte=end, thoi_gian_tao__gt=start)

        serializer = HoaDonThuocSerializer(hoa_don_thuoc, many=True, context = {'request' : request})
        response = {
            'data': serializer.data,
        }

        return Response(response)
class DanhSachBenhNhanChoLamSang(generics.ListCreateAPIView):
    serializer_class = LichHenKhamSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        now = timezone.localtime(timezone.now())
        tomorrow = now + timedelta(1)
        today_start = now.replace(hour=0, minute=0, second=0)
        today_end = tomorrow.replace(hour=0, minute=0, second=0)

        queryset = LichHenKham.objects.filter(thoi_gian_tao__gte=today_start, thoi_gian_tao__lt=today_end).order_by('-id')

        term = self.request.query_params.get('query[search]')
        trang_thai = self.request.query_params.get('query[trang_thai]')

        if term is not None:
            queryset = queryset.filter(Q(benh_nhan__ho_ten__icontains=term) | Q(benh_nhan__so_dien_thoai__icontains=term)).order_by('-id')

        if trang_thai is not None:
            trang_thai_lich_hen = TrangThaiLichHen.objects.get(id=trang_thai)
            queryset = queryset.filter(trang_thai = trang_thai_lich_hen).order_by('-id')

        return queryset
    # def get(self, request, format=None):
    #     trang_thai_lam_sang = TrangThaiLichHen.objects.get_or_create(ten_trang_thai = "Đã Thanh Toán Lâm Sàng")[0] 
    #     trang_thai_dich_vu = TrangThaiLichHen.objects.get_or_create(ten_trang_thai = "Đã Thanh Toán Dịch Vụ")[0] 
    #     trang_thai_phan_khoa = TrangThaiLichHen.objects.get_or_create(ten_trang_thai = "Đã Phân Khoa")[0] 
    #     now = timezone.localtime(timezone.now())
    #     tomorrow = now + timedelta(1)
    #     today_end = tomorrow.replace(hour=0, minute=0, second=0)

    #     lich_hen = LichHenKham.objects.filter(Q(trang_thai=trang_thai_lam_sang)| Q(trang_thai=trang_thai_dich_vu) | Q(trang_thai=trang_thai_phan_khoa)).filter(thoi_gian_bat_dau__lte=today_end)
    #     serializer = LichHenKhamSerializer(lich_hen, many=True, context={'request':request})
    #     response = {
    #         "error": False,
    #         "status": status.HTTP_200_OK,
    #         "message": "Danh Sach Lich Hen Kham",
    #         "data": serializer.data        
    #     }
    #     return Response(response)

# * --- update 6/1/2021 ---

class DanhSachPhongKham(APIView):
    def get(self, request, format=None):
        danh_sach_phong_kham = PhongKham.objects.all()
        serializer = DanhSachPhongKhamSerializer(danh_sach_phong_kham, many=True, context = {'request': request})
        data = serializer.data
        response = {
            'data': data,
        }
        return Response(response)

class ThongTinPhongKham(APIView):
    def get(self, request, format=None):
        phong_kham = PhongKham.objects.all().first()
        serializer = PhongKhamSerializer(phong_kham, context = {'request': request})
        data = serializer.data
        response = {
            'data': data
        }
        return Response(response)

class FilterBaoHiem(APIView):
    def get(self, request, format=None):
        ma_lk = self.request.query_params.get('ma_lk', None)      
        tu_ngay = self.request.query_params.get('tu_ngay', None)
        den_ngay = self.request.query_params.get('den_ngay', None)

        if ma_lk:
            chuoi_kham = ChuoiKham.objects.filter(ma_lk=ma_lk)[0]
            don_thuoc = chuoi_kham.don_thuoc_chuoi_kham.all()[0]
            danh_sach_thuoc = don_thuoc.ke_don.all().filter(bao_hiem=True)
            danh_sach_dich_vu = chuoi_kham.phan_khoa_kham.all().filter(bao_hiem=True)
            danh_sach_chi_so = chuoi_kham.ket_qua_tong_quat.all()[0].ket_qua_chuyen_khoa.all()

            serializer_1 = FilterChuoiKhamSerializer(chuoi_kham, context={'request': request})
            serializer_2 = FilterDonThuocSerializer(danh_sach_thuoc, many=True, context={'request': request})
            serializer_3 = FilterDichVuSerializer(danh_sach_dich_vu, many=True, context={'request': request})
            
            response = {
                'benh_nhan': serializer_1.data,
                'thuoc': serializer_2.data,
                'dich_vu': serializer_3.data,
            }
            return Response(response)
        elif tu_ngay and den_ngay:
            pass

class DanhSachMauPhieu(generics.ListCreateAPIView):
    serializer_class = MauPhieuSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        queryset = MauPhieu.objects.all()

        term = self.request.query_params.get('query[search]')
        sort_field = self.request.query_params.get('sort[field]')
        sort_type = self.request.query_params.get('sort[sort]')

        if term is not None:
            queryset = queryset.filter(Q(ten_mau__icontains=term) | Q(codename__icontains=term))

        if sort_field is not None and sort_type is not None:
            if sort_type == 'asc': 
                queryset = queryset.order_by(f'{sort_field}')
            elif sort_type == 'desc':
                queryset = queryset.order_by(f'-{sort_field}')

        return queryset

class TimKiemKetQuaBenhNhan(APIView):
    def get(self, request, format=None):
        _query = self.request.query_params.get('query')
        user = User.objects.filter(
            Q(so_dien_thoai__icontains=_query) | Q(ma_benh_nhan__icontains=_query) | 
            Q(cmnd_cccd__icontains=_query) | Q(ho_ten__icontains=_query) |
            Q(ma_so_bao_hiem__icontains=_query)
        )
        html_string_body = ""
        html_string_start = "\
            <html>\
            <head></head>\
            <body>\
                <div class='quick-search-result'>\
                    <div class='text-muted d-none'>\
                        Không có kết quả\
                    </div>\
                    <div class='font-size-sm text-primary font-weight-bolder text-uppercase mb-2'>\
                        Thành viên\
                    </div>\
                    <div class='mb-10'>\
        "
        html_string_end = "\
                    </div>\
                </div>\
            </body>\
            </html>\
            "

        for u in user:
            html_string_row = f"\
                <div class='d-flex align-items-center flex-grow-1 mb-2'>\
                    <div class='symbol symbol-30  flex-shrink-0'>\
                        <div class='symbol-label' style='background-image:url('https://preview.keenthemes.com/metronic/theme/html/demo1/dist/assets/media/users/300_20.jpg')'>\
                            </div>\
                        </div>\
                    <div class='d-flex flex-column ml-3 mt-2 mb-2'>\
                        <a href='/benh_nhan/{u.id}/tat_ca_lich_hen/' class='font-weight-bold text-dark text-hover-primary'>\
                            {u.ho_ten}\
                        </a>\
                        <span class='font-size-sm font-weight-bold text-muted'>\
                            {u.so_dien_thoai}\
                        </span>\
                    </div>\
                </div>"
            html_string_body += html_string_row

        html = html_string_start + html_string_body + html_string_end
        return Response(html)
    
class TatCaLichHenBenhNhanList(APIView):
    def get(self, request, format=None):
        id_benh_nhan = self.request.query_params.get('id')
        user = User.objects.get(id=id_benh_nhan)
        tat_ca_lich_hen = user.benh_nhan_hen_kham.all()
        serializer = TatCaLichHenSerializer(tat_ca_lich_hen, many=True, context={'request': request})
        response = {
            'data': serializer.data
        }
        return Response(response)

# UPDATE BY LONG 
class DanhSachLichSuKhamBenhNhan(APIView):
    def get(self, request, format=None):
        user_id = self.request.query_params.get("user_id")
        lich_su_kham = ChuoiKham.objects.filter(benh_nhan = user_id)
        serializer = ChuoiKhamSerializerSimple(lich_su_kham, many=True, context={'request': request})
        response = {
            'user_id': user_id,
            'data': serializer.data
        }
        return Response(response)
# END UPDATE

class ListTieuChuanDichVu(generics.ListCreateAPIView):
    serializer_class = NhomChiSoTieuChuanSerializer
    pagination_class = CustomPagination   

    def get_queryset(self):
        queryset = NhomChiSoXetNghiem.objects.all()

        term = self.request.query_params.get('query[search]')

        if term is not None:
            queryset = queryset.filter(ten_nhom__icontains=term)

        return queryset

class DanhSachTieuChuanTheoNhomAPIview(generics.ListCreateAPIView):
    serializer_class = ChiSoXetNghiemSerializer
    pagination_class = CustomPagination   

    def get_queryset(self):
        queryset = ChiSoXetNghiem.objects.all()

        id_nhom_chi_so = self.request.query_params.get('id_nhom_chi_so')
        nhom_chi_so = NhomChiSoXetNghiem.objects.filter(id=id_nhom_chi_so).first()

        term = self.request.query_params.get('query[search]')
        if id_nhom_chi_so is not None:
            queryset = queryset.filter(nhom_chi_so=nhom_chi_so)

        if term is not None:
            queryset = queryset.filter(ten_chi_so__icontains=term)

        return queryset


# class DanhSachKetQuaChuoiKhamBenhNhan(APIView):
#     def get(self, request, format=None):
#         id_benh_nhan = self.request.query_params.get('id_benh_nhan')
#         user = User.objects.filter(id=id_benh_nhan).first()
#         danh_sach_ket_qua = ChuoiKham.objects.filter(benh_nhan=user, trang_thai__trang_thai_chuoi_kham="Hoàn Thành")

class XemDonThuoc(APIView):
    def get(self, request, format=None):
        id_don_thuoc = self.request.query_params.get('id_don_thuoc', None)
        if id_don_thuoc is not None:
            don_thuoc = DonThuoc.objects.filter(id=id_don_thuoc).first()
            danh_sach_thuoc = don_thuoc.ke_don.all()
            serializer = DanhSachThuocSerializerSimple(danh_sach_thuoc, many=True, context={"request": request})
            data = serializer.data
            response = {
                'data': data
            }
            return Response(response)
    
class FilterDistrict(APIView):
    def get(self, request, format=None):
        id_province = self.request.query_params.get('id')
        province = Province.objects.filter(id=id_province).first()
        district = District.objects.filter(province=province)
        serializer = DistrictSerializer(district, many=True, context={'request': request})
        data = serializer.data
        response = {
            'data': data
        }
        return Response(response)

class FilterWard(APIView):
    def get(self, request, format=None):
        id_district = self.request.query_params.get('id')
        district = District.objects.filter(id=id_district).first()
        ward = Ward.objects.filter(district=district)
        serializer = WardSerializer(ward, many=True, context={'request': request})
        data = serializer.data
        response = {
            'data': data
        }
        return Response(response)

class KetQuaXetNghiemMobile(APIView):
    def get(self, request, format=None):
        id = self.request.query_params.get('id')
        ket_qua_chuyen_khoa = KetQuaChuyenKhoa.objects.filter(id=id).first()
        ket_qua_chi_so = ket_qua_chuyen_khoa.ket_qua_xet_nghiem.all()
        serializer = KetQuaXetNghiemSerializer(ket_qua_chi_so, many=True, context={'request': request})
        response = {
            'data': serializer.data
        }
        return Response(response)

class PhieuKetQuaMobile(APIView):
    def get(self, request, format=None):
        id = self.request.query_params.get('id')
        ket_qua_chuyen_khoa = KetQuaChuyenKhoa.objects.filter(id=id).first()
        html_ket_qua = ket_qua_chuyen_khoa.html_ket_qua.all().first()
        serializer = PhieuKetQuaSerializer(html_ket_qua, context={'request':request})
        response = {
            'data': serializer.data
        }
        return Response(response)

class GetFuncroomInfo(APIView):
    def get(self, request, format=None):
        id_dich_vu = self.request.query_params.get('id')
        dich_vu = DichVuKham.objects.filter(id=id_dich_vu).first()
        if dich_vu is not None:
            phong_chuc_nang = dich_vu.phong_chuc_nang
            id_phong_chuc_nang = phong_chuc_nang.id

            now = timezone.localtime(timezone.now())
            tomorrow = now + timedelta(1)
            today_start = now.replace(hour=0, minute=0, second=0)
            today_end = tomorrow.replace(hour=0, minute=0, second=0)
            thong_tin = PhanKhoaKham.objects.filter(thoi_gian_tao__lt=today_end, thoi_gian_tao__gte=today_start).values('id', 'dich_vu_kham__ten_dvkt', 'benh_nhan__ho_ten', 'trang_thai__trang_thai_khoa_kham').annotate(count=Count('id', filter=Q(dich_vu_kham__phong_chuc_nang__id=id_phong_chuc_nang)))
            
            count_pending = 0
            count_processing = 0
            count_finished = 0
            for i in thong_tin:
                if i['count'] != 0 and i['trang_thai__trang_thai_khoa_kham'] == "Đang Thực Hiện":
                    count_processing += 1
                elif i['count'] != 0 and i['trang_thai__trang_thai_khoa_kham'] == "Hoàn Thành":
                    count_finished += 1
                elif i['count'] != 0 and i['trang_thai__trang_thai_khoa_kham'] == None:
                    count_pending += 1
            response = {
                'dang_cho': count_pending,
                'dang_thuc_hien': count_processing,
                'hoan_thanh': count_finished,
            }
        else:
            response = {
                'dang_cho': "Không có thông tin",
                'dang_thuc_hien': "Không có thông tin",
                'hoan_thanh': "Không có thông tin",
            }
        return Response(response)


class ApiExportBenhNhanBaoHiemExcel(APIView):
    def get(self, request, format=None):
        startDate = self.request.query_params.get('range_start')
        endDate = self.request.query_params.get('range_end')
        start = datetime.strptime(startDate, "%d-%m-%Y")
        tomorrow_start = start + timedelta(1)
        if endDate == '':
            hoa_don_dich_vu = HoaDonChuoiKham.objects.filter(thoi_gian_tao__lte=tomorrow_start, thoi_gian_tao__gt=start)
        else:
            end = datetime.strptime(endDate, "%d-%m-%Y")
            if startDate == endDate:
                end = end + timedelta(1)
            
            hoa_don_dich_vu = HoaDonChuoiKham.objects.filter(thoi_gian_tao__lte=end, thoi_gian_tao__gt=start)

        serializer = FilterHoaDonChuoiKhamBaoHiemSerializer(hoa_don_dich_vu, many=True, context={'request': request})
        excel_data = serializer.data

        response = {
            'data': excel_data
        }

        return Response(response)

class ApiExportExcelDichVu(APIView):
    def get(self, request, format=None):
        startDate = self.request.query_params.get('range_start')
        endDate = self.request.query_params.get('range_end')
        start = datetime.strptime(startDate, "%d-%m-%Y")
        tomorrow_start = start + timedelta(1)

        if endDate == '':
            dich_vu = PhanKhoaKham.objects.filter(thoi_gian_tao__lt=tomorrow_start, thoi_gian_tao__gte=start).values('dich_vu_kham__ten_dvkt').annotate(tong_tien=Sum('dich_vu_kham__don_gia')).order_by('dich_vu_kham__ten_dvkt').annotate(dich_vu_kham_count = Count('dich_vu_kham__ten_dvkt')).annotate(ma_dvkt=F('dich_vu_kham__ma_dvkt')).annotate(don_gia=F('dich_vu_kham__don_gia')).annotate(stt=F('dich_vu_kham__stt'))
            list_dich_vu = []
            for i in dich_vu:
                list_dich_vu.append(i)
            response = {
                'data' : list_dich_vu,
            }
        else:
            end = datetime.strptime(endDate, "%d-%m-%Y")
            if startDate == endDate:
                end = end + timedelta(1)
            dich_vu = PhanKhoaKham.objects.filter(thoi_gian_tao__lt=end, thoi_gian_tao__gte=start).filter(bao_hiem=True).values('dich_vu_kham__ten_dvkt').annotate(tong_tien=Sum('dich_vu_kham__don_gia')).order_by('dich_vu_kham__ten_dvkt').annotate(dich_vu_kham_count = Count('dich_vu_kham__ten_dvkt')).annotate(ma_dvkt=F('dich_vu_kham__ma_dvkt')).annotate(don_gia=F('dich_vu_kham__don_gia')).annotate(stt=F('dich_vu_kham__stt'))
            
            list_tong_tien_formatted = ["{:,}".format(int(i['tong_tien'])) if i['tong_tien'] is not None else 0 for i in dich_vu]

            list_dich_vu = []
            for idx, val in enumerate(dich_vu):
                val['tong_tien'] = list_tong_tien_formatted[idx]
                list_dich_vu.append(val)

            response = {
                'data': list_dich_vu
            }

        return Response(response)

class ApiExportExcelThuoc(APIView):
    def get(self, request, format=None):
        startDate = self.request.query_params.get('range_start')
        endDate = self.request.query_params.get('range_end')
        start = datetime.strptime(startDate, "%d-%m-%Y")
        tomorrow_start = start + timedelta(1)

        if endDate == '':
            thuoc = KeDonThuoc.objects.filter(thoi_gian_tao__lt=tomorrow_start, thoi_gian_tao__gte=start).values('thuoc__ten_thuoc').annotate(tong_tien=Sum('thuoc__don_gia_tt')).order_by('thuoc__ten_thuoc').annotate(thuoc_count = Count('thuoc__ten_thuoc')).annotate(ten_hoat_chat=F('thuoc__ten_hoat_chat')).annotate(duong_dung=F('thuoc__duong_dung')).annotate(ham_luong=F('thuoc__ham_luong')).annotate(so_dang_ky=F('thuoc__so_dang_ky')).annotate(don_vi_tinh=F('thuoc__don_vi_tinh')).annotate(don_gia=F('thuoc__don_gia_tt'))
            
            list_thuoc = []
            for i in thuoc:
                list_thuoc.append(i)
            response = {
                'data' : list_thuoc,
            }
        else:
            end = datetime.strptime(endDate, "%d-%m-%Y")
            if startDate == endDate:
                end = end + timedelta(1)
            thuoc = KeDonThuoc.objects.filter(thoi_gian_tao__lt=end, thoi_gian_tao__gte=start).values('thuoc__ten_thuoc').annotate(tong_tien=Sum('thuoc__don_gia_tt')).order_by('thuoc__ten_thuoc').annotate(thuoc_count = Count('thuoc__ten_thuoc')).annotate(ten_hoat_chat=F('thuoc__ten_hoat_chat')).annotate(duong_dung=F('thuoc__duong_dung')).annotate(ham_luong=F('thuoc__ham_luong')).annotate(so_dang_ky=F('thuoc__so_dang_ky')).annotate(don_vi_tinh=F('thuoc__don_vi_tinh')).annotate(don_gia=F('thuoc__don_gia_tt')).annotate(ma_thuoc=F('thuoc__ma_thuoc'))
            list_tong_tien_formatted = ["{:,}".format(int(i['tong_tien'])) for i in thuoc]

            list_thuoc = []
            for idx, val in enumerate(thuoc):
                val['tong_tien'] = list_tong_tien_formatted[idx]
                list_thuoc.append(val)

            response = {
                'data': list_thuoc
            }

        return Response(response)

class ApiListGroup(APIView):
    def get(self, request, format=None):
        all_groups = Group.objects.all()
        serializer = GroupSerializer(all_groups, many=True, context = {'request': request})
        response = {
            'data': serializer.data
        }
        return Response(response)

class ApiListStaff(APIView):
    def get(self, request, format=None):
        staff_users = User.objects.filter(staff=True)
        serializer = StaffUserSerializer(staff_users, many=True)
        response = {
            'data': serializer.data
        }
        return Response(response)

class ApiListAllGroupOfUser(APIView):
    def get(self, request, format=None):
        user_id = self.request.query_params.get('id')
        user = get_object_or_404(User, id=user_id)
        user_groups = user.groups.all()
        serializer = GroupSerializer(user_groups, many=True)
        response = {
            'data': serializer.data
        }
        return Response(response)

class DanhSachBaoCaoTheoThoiGian(APIView):
    def get(self, request, format=None):
        range_start = self.request.query_params.get('range_start', None)
        range_end   = self.request.query_params.get('range_end', None)

        start = datetime.strptime(range_start, "%d-%m-%Y")
        tomorrow_start = start + timedelta(1)

        # print(start)
        if range_end == '':
            response = [
                {   
                    'type': 'bao_cao_nhap',
                    'loai_bao_cao': 'Báo Cáo Nhập BH',
                    'thoi_gian_bat_dau': start,
                    'thoi_gian_ket_thuc': tomorrow_start,
                    # 'tong_tien': tong_doanh_thu_formatted
                },
                {   
                    'type': 'bao_cao_xuat',
                    'loai_bao_cao': 'Báo Cáo Xuất BH',
                    'thoi_gian_bat_dau': start,
                    'thoi_gian_ket_thuc': tomorrow_start,
                    # 'tong_tien': tong_tien_dich_vu_formatted
                },
                {
                    'type': 'bao_cao_ton',
                    'loai_bao_cao': 'Báo Cáo Tồn BH',
                    'thoi_gian_bat_dau': start,
                    'thoi_gian_ket_thuc': tomorrow_start,
                    # 'tong_tien': tong_tien_don_thuoc_formatted
                },
                {   
                    'type': 'bao_cao_nhap_dv',
                    'loai_bao_cao': 'Báo Cáo Nhập DV',
                    'thoi_gian_bat_dau': start,
                    'thoi_gian_ket_thuc': tomorrow_start,
                    # 'tong_tien': tong_doanh_thu_formatted
                },
                {   
                    'type': 'bao_cao_xuat_dv',
                    'loai_bao_cao': 'Báo Cáo Xuất DV',
                    'thoi_gian_bat_dau': start,
                    'thoi_gian_ket_thuc': tomorrow_start,
                    # 'tong_tien': tong_tien_dich_vu_formatted
                },
                {
                    'type': 'bao_cao_ton_dv',
                    'loai_bao_cao': 'Báo Cáo Tồn DV',
                    'thoi_gian_bat_dau': start,
                    'thoi_gian_ket_thuc': tomorrow_start,
                    # 'tong_tien': tong_tien_don_thuoc_formatted
                },
            ]
            return Response(response)

        else:

            end = datetime.strptime(range_end, "%d-%m-%Y")
            print(end)
            # tomorrow_end = end + timedelta(1)
            if range_start == range_end:
                end = end + timedelta(1)

            response = [
                {   
                    'type': 'bao_cao_nhap',
                    'loai_bao_cao': 'Báo Cáo Nhập BH',
                    'thoi_gian_bat_dau': start,
                    'thoi_gian_ket_thuc': end,
                    # 'tong_tien': tong_doanh_thu_formatted
                },
                {   
                    'type': 'bao_cao_xuat',
                    'loai_bao_cao': 'Báo Cáo Xuất BH',
                    'thoi_gian_bat_dau': start,
                    'thoi_gian_ket_thuc': end,
                    # 'tong_tien': tong_tien_dich_vu_formatted
                },
                {
                    'type': 'bao_cao_ton',
                    'loai_bao_cao': 'Báo Cáo Tồn BH',
                    'thoi_gian_bat_dau': start,
                    'thoi_gian_ket_thuc': end,
                    # 'tong_tien': tong_tien_don_thuoc_formatted
                },
                {   
                    'type': 'bao_cao_nhap_dv',
                    'loai_bao_cao': 'Báo Cáo Nhập DV',
                    'thoi_gian_bat_dau': start,
                    'thoi_gian_ket_thuc': tomorrow_start,
                    # 'tong_tien': tong_doanh_thu_formatted
                },
                {   
                    'type': 'bao_cao_xuat_dv',
                    'loai_bao_cao': 'Báo Cáo Xuất DV',
                    'thoi_gian_bat_dau': start,
                    'thoi_gian_ket_thuc': tomorrow_start,
                    # 'tong_tien': tong_tien_dich_vu_formatted
                },
                {
                    'type': 'bao_cao_ton_dv',
                    'loai_bao_cao': 'Báo Cáo Tồn DV',
                    'thoi_gian_bat_dau': start,
                    'thoi_gian_ket_thuc': tomorrow_start,
                    # 'tong_tien': tong_tien_don_thuoc_formatted
                },
                
            ]
            return Response(response)

class DanhSachNhungThuocDuocNhap(APIView):
    def get(self, request, format=None):
        range_start = self.request.query_params.get('range_start', None)
        range_end   = self.request.query_params.get('range_end', None)
        start = datetime.strptime(range_start, "%d-%m-%Y")

        tomorrow_start = start + timedelta(1)

        if range_end == '':
            danh_sach_nhap_hang = NhapHang.objects.filter(thoi_gian_tao__lt=tomorrow_start, thoi_gian_tao__gt=start).exclude(bao_hiem=False).values('thuoc__ten_thuoc').annotate(so_luong = Sum('so_luong')).annotate(c = Count('thuoc__id')).annotate(id=F('thuoc__id')).annotate(bao_hiem=F('bao_hiem'))

            list_nhap_hang = []

            for i in danh_sach_nhap_hang:
                list_nhap_hang.append(i)
            response = {
                'data' : list_nhap_hang,
            }

            return Response(response)
        else: 
            end = datetime.strptime(range_end, "%d-%m-%Y")
            danh_sach_nhap_hang = NhapHang.objects.filter(thoi_gian_tao__lt=end, thoi_gian_tao__gt=start).exclude(bao_hiem=False).values('thuoc__ten_thuoc').annotate(so_luong=Sum('so_luong')).annotate(count=Count('thuoc__id')).annotate(bao_hiem=F('bao_hiem'))

            list_nhap_hang = []

            for i in danh_sach_nhap_hang:
                list_nhap_hang.append(i)

            response = {
                'data' : list_nhap_hang,
            }

            return Response(response)

class DanhSachNhungThuocDuocXuat(APIView):
    def get(self, request, format=None):
        range_start = self.request.query_params.get('range_start', None)
        range_end   = self.request.query_params.get('range_end', None)
        start = datetime.strptime(range_start, "%d-%m-%Y")

        tomorrow_start = start + timedelta(1)

        if range_end == '':
            danh_sach_xuat_hang = KeDonThuoc.objects.filter(thoi_gian_tao__lt=tomorrow_start, thoi_gian_tao__gt=start).exclude(bao_hiem=False).values('thuoc__ten_thuoc').annotate(so_luong = Sum('so_luong')).order_by('thuoc__id').annotate(c = Count('thuoc__id')).annotate(id=F('thuoc__id')).annotate(bao_hiem = F('bao_hiem'))
            list_xuat_hang = []

            for i in danh_sach_xuat_hang:
                list_xuat_hang.append(i)

            response = {
                'data' : list_xuat_hang,
            }

            return Response(response)
        else:
            end = datetime.strptime(range_end, "%d-%m-%Y")

            danh_sach_xuat_hang = KeDonThuoc.objects.filter(thoi_gian_tao__lt=end, thoi_gian_tao__gt=start).exclude(bao_hiem=False).values('thuoc__ten_thuoc').annotate(so_luong = Sum('so_luong')).order_by('thuoc__id').annotate(c = Count('thuoc__id')).annotate(id=F('thuoc__id')).annotate(bao_hiem = F('bao_hiem'))
            list_xuat_hang = []

            for i in danh_sach_xuat_hang:
                list_xuat_hang.append(i)
            response = {
                'data' : list_xuat_hang,
            }

            return Response(response)
    
class DanhSachThuocNhapDichVu(APIView):
    def get(self, request, format=None):
        range_start = self.request.query_params.get('range_start', None)
        range_end   = self.request.query_params.get('range_end', None)
        start = datetime.strptime(range_start, "%d-%m-%Y")

        list_xuat_hang = []
        if range_end == '': 
            end = start + timedelta(1)
            danh_sach_nhap_hang = NhapHang.objects.filter(thoi_gian_tao__lte=end, thoi_gian_tao__gte=start).exclude(bao_hiem=True).values('thuoc__ten_thuoc').annotate(so_luong = Sum('so_luong')).annotate(c = Count('thuoc__id')).annotate(id=F('thuoc__id')).annotate(bao_hiem=F('bao_hiem'))

        else:
            end = datetime.strptime(range_end, "%d-%m-%Y")

            if range_start == range_end:
                end = end + timedelta(1)

            danh_sach_nhap_hang = NhapHang.objects.filter(thoi_gian_tao__lte=end, thoi_gian_tao__gte=start).exclude(bao_hiem=True).values('thuoc__ten_thuoc').annotate(so_luong = Sum('so_luong')).annotate(c = Count('thuoc__id')).annotate(id=F('thuoc__id')).annotate(bao_hiem=F('bao_hiem'))
            

        for i in danh_sach_nhap_hang:
            list_xuat_hang.append(i)
            
        response = {
            'data' : list_xuat_hang,
        }

        return Response(response)

class DanhSachThuocXuatDichVu(APIView):
    def get(self, request, format=None):
        range_start = self.request.query_params.get('range_start', None)
        range_end   = self.request.query_params.get('range_end', None)
        start = datetime.strptime(range_start, "%d-%m-%Y")

        if range_end == '':
            end = start + timedelta(1)
            danh_sach_xuat_hang = KeDonThuoc.objects.filter(thoi_gian_tao__lte=end, thoi_gian_tao__gte=start).exclude(bao_hiem=True).values('thuoc__ten_thuoc').annotate(so_luong = Sum('so_luong')).order_by('thuoc__id').annotate(c = Count('thuoc__id')).annotate(id=F('thuoc__id')).annotate(bao_hiem = F('bao_hiem'))
            list_xuat_hang = []
        else:
            end = datetime.strptime(range_end, "%d-%m-%Y")
            if range_start == range_end:
                end = end + timedelta(1)
            danh_sach_xuat_hang = KeDonThuoc.objects.filter(thoi_gian_tao__lte=end, thoi_gian_tao__gte=start).exclude(bao_hiem=True).values('thuoc__ten_thuoc').annotate(so_luong = Sum('so_luong')).order_by('thuoc__id').annotate(c = Count('thuoc__id')).annotate(id=F('thuoc__id')).annotate(bao_hiem = F('bao_hiem'))
            list_xuat_hang = []

        for i in danh_sach_xuat_hang:
            list_xuat_hang.append(i)
        response = {
            'data' : list_xuat_hang,
        }

        return Response(response)

class GetDanhSachPhanKhoaCuaChuoiKham(APIView):
    def get(self, request, format=None):
        id_chuoi_kham = self.request.query_params.get('id_chuoi_kham')

        chuoi_kham = get_object_or_404(ChuoiKham, id=id_chuoi_kham)
        danh_sach_phan_khoa = chuoi_kham.phan_khoa_kham.all()
        
        
        list_data = []
        for phan_khoa in danh_sach_phan_khoa:
            dict_ = {}
            nested_dict = {}
            pcn_dict = {}
            pcn_dict['id'] = phan_khoa.dich_vu_kham.phong_chuc_nang.id
            pcn_dict['bac_si_phu_trach'] = phan_khoa.dich_vu_kham.phong_chuc_nang.bac_si_phu_trach
            pcn_dict['thoi_gian_tao'] = phan_khoa.dich_vu_kham.phong_chuc_nang.thoi_gian_tao.strftime("%d/%m/%y %H:%M:%S") 
            pcn_dict['thoi_gian_cap_nhat'] = phan_khoa.dich_vu_kham.phong_chuc_nang.thoi_gian_cap_nhat.strftime("%d/%m/%y %H:%M:%S")
            pcn_dict['ten_phong_chuc_nang'] = phan_khoa.dich_vu_kham.phong_chuc_nang.ten_phong_chuc_nang
            pcn_dict['slug'] = phan_khoa.dich_vu_kham.phong_chuc_nang.slug

            nested_dict['id'] = phan_khoa.dich_vu_kham.id
            nested_dict['don_gia'] = "{:,}".format(int(phan_khoa.dich_vu_kham.don_gia))
            nested_dict['don_gia_bhyt'] = "{:,}".format(int(phan_khoa.dich_vu_kham.don_gia_bhyt))
            nested_dict['phong_chuc_nang'] = pcn_dict
            nested_dict['bao_hiem_dich_vu'] = str(phan_khoa.dich_vu_kham.bao_hiem)
            
            nested_dict['ma_dvkt'] = phan_khoa.dich_vu_kham.ma_dvkt
            nested_dict['stt'] = phan_khoa.dich_vu_kham.stt
            nested_dict['ten_dvkt'] = phan_khoa.dich_vu_kham.ten_dvkt
            nested_dict['ma_gia'] = phan_khoa.dich_vu_kham.ma_gia
            nested_dict['quyet_dinh'] = phan_khoa.dich_vu_kham.quyet_dinh
            nested_dict['cong_bo'] = phan_khoa.dich_vu_kham.cong_bo
            nested_dict['ma_cosokcb'] = phan_khoa.dich_vu_kham.ma_cosokcb
            nested_dict['ten_dich_vu'] = phan_khoa.dich_vu_kham.ten_dich_vu
            nested_dict['tyle_tt'] = phan_khoa.dich_vu_kham.tyle_tt
            nested_dict['chi_so'] = phan_khoa.dich_vu_kham.chi_so
            nested_dict['html'] = phan_khoa.dich_vu_kham.html
            nested_dict['khoa'] = phan_khoa.dich_vu_kham.khoa
            nested_dict['nhom_chi_phi'] = phan_khoa.dich_vu_kham.nhom_chi_phi
            nested_dict['bao_hiem'] = phan_khoa.bao_hiem

            dict_['obj'] = nested_dict
            list_data.append(dict_)
            

        response = {
            'data': list_data
        }
        return Response(response)

class XemLaiBenhNhanDaKhamChuyenKhoaAPIView(APIView):
    def get(self, request, format=None):
        range_start = self.request.query_params.get('range_start', None)
        range_end   = self.request.query_params.get('range_end', None)
        start = datetime.strptime(range_start, "%d-%m-%Y")
        list_filtered = []
        
        if range_end == '':
            end = start + timedelta(1)
        else:
            end = datetime.strptime(range_end, "%d-%m-%Y")
            if range_start == range_end:
                end = end + timedelta(1)
            
        danh_sach_benh_nhan = request.user.ket_qua_bac_si_chuyen_khoa.all().filter(thoi_gian_tao__gte=start, thoi_gian_tao__lte=end).values("bac_si_chuyen_khoa__ho_ten", "phan_khoa_kham__benh_nhan__id", "phan_khoa_kham__benh_nhan__ho_ten", "phan_khoa_kham__benh_nhan__so_dien_thoai").annotate(count=Count('phan_khoa_kham__benh_nhan__id'))
        
        for i in danh_sach_benh_nhan:
            if i['count'] != 0:
                list_filtered.append(i)

        response = {
            'data': list_filtered
        }

        return Response(response)

class XemLaiBenhNhanLamSangAPIView(APIView):
    def get(self, request, format=None):
        range_start = self.request.query_params.get('range_start', None)
        range_end   = self.request.query_params.get('range_end', None)
        start = datetime.strptime(range_start, "%d-%m-%Y")
        list_filtered = []

        if range_end == '':
            end = start + timedelta(1)
        else:
            end = datetime.strptime(range_end, "%d-%m-%Y")
            if range_start == range_end:
                end = end + timedelta(1)

        trang_thai_hoan_thanh = TrangThaiChuoiKham.objects.filter(trang_thai_chuoi_kham="Hoàn Thành").first()
        trang_thai_dang_thuc_hien = TrangThaiChuoiKham.objects.filter(trang_thai_chuoi_kham="Đang Thực Hiện").first()
        trang_thai_dung_kham = TrangThaiChuoiKham.objects.filter(trang_thai_chuoi_kham="Dừng Khám").first()
        danh_sach_benh_nhan = request.user.bac_si_chuoi_kham.all().filter(Q(trang_thai=trang_thai_dang_thuc_hien) | Q(trang_thai=trang_thai_hoan_thanh) | Q(trang_thai=trang_thai_dung_kham)).filter(thoi_gian_tao__gte=start, thoi_gian_tao__lte=end).values('bac_si_dam_nhan__ho_ten', 'benh_nhan__id', 'benh_nhan__ho_ten', 'benh_nhan__so_dien_thoai').annotate(count=Count('benh_nhan__id'))
        
        for i in danh_sach_benh_nhan:
            if i['count'] != 0:
                list_filtered.append(i)

        response = {
            'data': list_filtered
        }
        return Response(response)

class XuatNhapTongThuocAPIView(APIView, PaginationHandlerMixin):
    pagination_class = CustomPagination

    def get(self, request, format=None):
        range_start = self.request.query_params.get('range_start', None)
        range_end   = self.request.query_params.get('range_end', None)
        start = datetime.strptime(range_start, "%d-%m-%Y")

        if range_end == '':
            end = start + timedelta(1)
        else:
            end = datetime.strptime(range_end, "%d-%m-%Y")
            if range_start == range_end:
                end = end + timedelta(1)

        danh_sach_thuoc = Thuoc.objects.all()

        medicines = danh_sach_thuoc.annotate(
            so_luong_nhap = Subquery(
                NhapHang.objects.filter(
                    thuoc = OuterRef('pk'),
                ).filter(thoi_gian_tao__gte=start, thoi_gian_tao__lt=end).values_list(
                    Func(
                        'so_luong',
                        function='SUM',
                    )
                )
            )
        ).annotate(
            so_luong_xuat = Subquery(
                KeDonThuoc.objects.filter(
                    thuoc = OuterRef('pk'),
                ).filter(thoi_gian_tao__gte=start, thoi_gian_tao__lt=end).values_list(
                    Func(
                        'so_luong',
                        function='SUM',
                    )
                )
            )
        ).annotate(
            ton_dau_ky=models.Case(
                models.When(Q(so_luong_nhap__isnull=True) & Q(so_luong_xuat__isnull=True), then=F('so_luong_kha_dung')),
                models.When(so_luong_nhap__isnull=True, then=F('so_luong_kha_dung') + F('so_luong_xuat')),
                models.When(so_luong_xuat__isnull=True, then=F('so_luong_kha_dung') - F('so_luong_nhap')),
                default = F('so_luong_kha_dung') - F('so_luong_nhap') + F('so_luong_xuat'),
                output_field=models.IntegerField(),
            )
        ).annotate(
            ton_cuoi_ky=models.Case(
                models.When(Q(so_luong_nhap__isnull=True) & Q(so_luong_xuat__isnull=True), then=F('ton_dau_ky')),
                models.When(so_luong_nhap__isnull=True, then=F('ton_dau_ky') - F('so_luong_xuat')),
                models.When(so_luong_xuat__isnull=True, then=F('ton_dau_ky') + F('so_luong_nhap')),
                default = F('ton_dau_ky') + F('so_luong_nhap') - F('so_luong_xuat'),
                output_field=models.IntegerField(),
            )
        ).annotate(
            thanh_tien_nhap=F('so_luong_nhap') * F('don_gia')
        ).annotate(
            thanh_tien_xuat=F('so_luong_xuat') * F('don_gia_tt')
        ).values(
            'ma_thuoc',
            'ten_thuoc',
            'ten_hoat_chat',
            'don_vi_tinh',
            'ham_luong',
            'cong_ty__ten_cong_ty',
            'nuoc_sx',
            'so_lo',
            'han_su_dung',
            'don_gia',
            'don_gia_tt',
            'gia_bhyt',      
            'so_luong_nhap',
            'so_luong_xuat',
            'ton_dau_ky',
            'thanh_tien_nhap',
            'thanh_tien_xuat',
            'ton_cuoi_ky',
        )
        
        page = self.paginate_queryset(medicines)

        if page is not None:
            serializer = self.get_paginated_response(page)
            return Response(serializer.data)
        else:
            serializer = medicines
        return Response(serializer)

class DanhSachThuocSapHetHan(APIView, PaginationHandlerMixin):
    pagination_class = CustomPagination
    serializer_class = ThuocSerializer

    def get(self, request, format=None):
        num_of_months = self.request.query_params.get('num_of_months')
        num_of_months_later = date.today() + relativedelta(months=+int(num_of_months))

        medicines = Thuoc.objects.filter(han_su_dung__lte=num_of_months_later)

        page = self.paginate_queryset(medicines)

        if page is not None:
            serializer = self.get_paginated_response(self.serializer_class(page, many=True).data)
        else:
            serializer = self.serializer_class(medicines, many=True)    
        return Response(serializer.data)

class ChiTietMauPhieuAPIView(APIView):
    def get(self, request, format=None):
        codename = self.request.query_params.get('codename')
        try:
            mau_phieu = MauPhieu.objects.get(codename=codename)
            serializer = MauPhieuSerializer(mau_phieu)
            response = {
                'status': 200,
                'data': serializer.data
            }
        except MauPhieu.DoesNotExist:
            response = {
                'status': 404,
                'data': "Mẫu Phiếu Không Tồn Tại"
            }
        return Response(response)

class SetHtmlDichVuKham(APIView):
    def get(self, request, format=None):
        id_dich_vu = self.request.query_params.get('id_dich_vu')
        flag = self.request.query_params.get('flag')
        dich_vu = DichVuKham.objects.get(id=id_dich_vu)
        if flag == "True":
            dich_vu.html = True
        elif flag == "False":
            dich_vu.html = False

        dich_vu.save()
        response = {
            'status': 200,
            'message': 'OKE'
        }
        return Response(response)

class SetChiSoDichVuKham(APIView):
    def get(self, request, format=None):
        id_dich_vu = self.request.query_params.get('id_dich_vu')
        flag = self.request.query_params.get('flag')
        dich_vu = DichVuKham.objects.get(id=id_dich_vu)
        if flag == "True":
            dich_vu.chi_so = True
        elif flag == "False":
            dich_vu.chi_so = False

        dich_vu.save()
        response = {
            'status': 200,
            'message': 'OKE'
        }
        return Response(response)