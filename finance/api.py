from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework import viewsets
from finance.models import HoaDonChuoiKham, HoaDonThuoc
from finance.serializers import HoaDonChuoiKhamSerializer, HoaDonThuocSerializer

class HoaDonThuocViewSet(viewsets.ModelViewSet):
    def list(self, request):
        hoa_don_thuoc = HoaDonThuoc.objects.all()
        serializer = HoaDonThuocSerializer(hoa_don_thuoc, many=True, context={"request": request})
        response = {
            "error": False,
            "status": status.HTTP_200_OK,
            "message": "Danh Sach Hoa Don Thuoc",
            "data": serializer.data        
        }
        return Response(response)

    def create(self, request):
        try:
            serializer = HoaDonThuocSerializer(data=request.data, context={"request": request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            response = {
                "error": False, 
                "status": status.HTTP_201_CREATED,
                "message": f"Them Hoa Don Thuoc Thanh Cong"
            }
        except:
            response = {
                "error": True, 
                "status": status.HTTP_409_CONFLICT,
                "message": "Khong The Them Hoa Don Thuoc"
            }
        return Response(response)

    def retrieve(self, request, pk=None):
        queryset = HoaDonThuoc.objects.all()
        hoa_don_thuoc = get_object_or_404(queryset, pk=pk)
        serializer = HoaDonThuocSerializer(hoa_don_thuoc, context={"request": request})
        data = serializer.data
        response = {
            "error": False, 
            "status": status.HTTP_200_OK,
            "message": "Hoa Don Thuoc",
            "data": data
        }
        return Response(response)   

    def update(self, request, pk=None):
        try:
            queryset = HoaDonThuoc.objects.all()
            hoa_don_thuoc = get_object_or_404(queryset, pk=pk)
            serializer = HoaDonThuocSerializer(hoa_don_thuoc, data=request.data, context={"request": request})
            serializer.is_valid()
            serializer.save()
            response = {
                "error": False, 
                "status": status.HTTP_200_OK,
                "message": "Cap Nhat Hoa Don Thuoc Thanh Cong",
                "data": serializer.data
            }
        except:
            response = {
                "error": True, 
                "status": status.HTTP_409_CONFLICT,
                "message": "Khong The Cap Nhat Hoa Don Thuoc",
            }
        return Response(response)

    def destroy(self, request, pk=None):
        queryset = HoaDonThuoc.objects.all()
        hoa_don_thuoc = get_object_or_404(queryset, pk=pk)
        hoa_don_thuoc.delete()
        return Response({
            "error": False, 
            "status": status.HTTP_204_NO_CONTENT,
            "message": "Xoa Hoa Don Thuoc Thanh Cong"
        })

    # * hóa đơn thuốc sẽ được query qua đơn thuốc, hoặc người dùng sẽ hiển thị ra một list các hóa đơn của họ
    # TODO custom lại hóa đơn thuốc

class HoaDonChuoiKhamViewSet(viewsets.ModelViewSet):
    def list(self, request):
        hoa_don_chuoi_kham = HoaDonChuoiKham.objects.all()
        serializer = HoaDonChuoiKhamSerializer(hoa_don_chuoi_kham, many=True, context={"request": request})
        response = {
            "error": False,
            "status": status.HTTP_200_OK,
            "message": "Danh Sach Hoa Don Chuoi Kham",
            "data": serializer.data        
        }
        return Response(response)

    def create(self, request):
        try:
            serializer = HoaDonChuoiKhamSerializer(data=request.data, context={"request": request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            response = {
                "error": False, 
                "status": status.HTTP_201_CREATED,
                "message": f"Them Hoa Don Chuoi Kham Thanh Cong"
            }
        except:
            response = {
                "error": True, 
                "status": status.HTTP_409_CONFLICT,
                "message": "Khong The Them Hoa Don Chuoi Kham"
            }
        return Response(response)

    def retrieve(self, request, pk=None):
        queryset = HoaDonChuoiKham.objects.all()
        hoa_don_chuoi_kham = get_object_or_404(queryset, pk=pk)
        serializer = HoaDonChuoiKhamSerializer(hoa_don_chuoi_kham, context={"request": request})
        data = serializer.data
        response = {
            "error": False, 
            "status": status.HTTP_200_OK,
            "message": "Hoa Don Chuoi Kham",
            "data": data
        }
        return Response(response)   

    def update(self, request, pk=None):
        try:
            queryset = HoaDonChuoiKham.objects.all()
            hoa_don_chuoi_kham = get_object_or_404(queryset, pk=pk)
            serializer = HoaDonChuoiKhamSerializer(hoa_don_chuoi_kham, data=request.data, context={"request": request})
            serializer.is_valid()
            serializer.save()
            response = {
                "error": False, 
                "status": status.HTTP_200_OK,
                "message": "Cap Nhat Hoa Don Chuoi Kham Thanh Cong",
                "data": serializer.data
            }
        except:
            response = {
                "error": True, 
                "status": status.HTTP_409_CONFLICT,
                "message": "Khong The Cap Nhat Hoa Don Chuoi Kham",
            }
        return Response(response)

    def destroy(self, request, pk=None):
        queryset = HoaDonChuoiKham.objects.all()
        hoa_don_chuoi_kham = get_object_or_404(queryset, pk=pk)
        hoa_don_chuoi_kham.delete()
        return Response({
            "error": False, 
            "status": status.HTTP_204_NO_CONTENT,
            "message": "Xoa Hoa Don Chuoi Kham Thanh Cong"
        })

    # * hóa đơn chuỗi khám sẽ được query qua chuỗi khám, hoặc người dùng sẽ hiển thị ra một list các hóa đơn của họ
    # TODO custom lại hóa đơn chuỗi khám