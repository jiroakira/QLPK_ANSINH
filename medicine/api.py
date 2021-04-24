from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404
from django.db import transaction
from django.db.models import F
from django.utils import timezone
from medicine.models import Thuoc, CongTy, ThuocLog
from medicine.serializers import ThuocSerializer, CongTySerializer

class ThuocViewSet(viewsets.ViewSet):
    # authentication_class = [JWTAuthentication] # comment out this for testing
    # permission_classes = [IsAuthenticated] # comment out this for testing

    def list(self, request):
        thuoc = Thuoc.objects.all()
        serializer = ThuocSerializer(thuoc, many=True, context={"request": request})

        thuoc_data = serializer.data
        # ds_thuoc_moi = []

        # for thuoc in thuoc_data:
        #     chi_tiet_thuoc = ChiTietThuoc.objects.filter(id_thuoc = thuoc['id'])
        #     chi_tiet_thuoc_serializers = ChiTietThuocSerializerSimple(chi_tiet_thuoc,many=True)
        #     thuoc['chi_tiet_thuoc'] = chi_tiet_thuoc_serializers.data
        #     ds_thuoc_moi.append(thuoc)

        response = {"error": False, "message": "Danh sach thuoc", "data": thuoc_data}
        return Response(response)
    
    def create(self, request):
        try:
            serializer = ThuocSerializer(data=request.data, context={"request":request})
            serializer.is_valid(raise_exception = True)
            serializer.save()

            # id_thuoc=serializer.data['id']

            # # adding and saving id into medicine compositions table
            # danh_sach_chi_tiet_thuoc = []
            # for thuoc in request.data["chi_tiet_thuoc"]:
            #     print(thuoc)
            #     thuoc["id_thuoc"] = id_thuoc
            #     thuoc.append(thuoc)
            #     print(thuoc)

            # serializer_2 = ChiTietThuocSerializer(data=danh_sach_chi_tiet_thuoc, many=True, context={"request": request})
            # serializer_2.is_valid()
            # serializer_2.save()
            dict_response={"error":False,"message":"Luu Du Lieu Thuoc Thanh Cong"}

        except:
            dict_response={"error":True,"message":"Xay Ra Loi Trong Qua Trinh Luu Du Lieu Thuoc"}

        return Response(dict_response)

    def retrieve(self,request,id=None):
        queryset = Thuoc.objects.all()
        thuoc = get_object_or_404(queryset,id=id)
        serializer = ThuocSerializer(thuoc,context={"request":request})

        serializer_data = serializer.data
        # Accessing All the Medicine Details of Current Medicine ID
        # chi_tiet_thuoc = ChiTietThuoc.objects.filter(id_thuoc=serializer_data["id"])
        # chi_tiet_thuoc_serializers = ChiTietThuocSerializerSimple(chi_tiet_thuoc, many=True)
        # serializer_data["chi_tiet_thuoc"] = chi_tiet_thuoc_serializers.data

        return Response({"error":False,"message":"Single Data Fetch","data":serializer_data})

    def update(self,request,id=None):
        queryset = Thuoc.objects.all()
        thuoc = get_object_or_404(queryset,id=id)
        serializer = ThuocSerializer(thuoc,data=request.data,context={"request":request})
        serializer.is_valid()
        serializer.save()
        #print(request.data["medicine_details"])
        # for salt_detail in request.data["chi_tiet_thuoc"]:
        #     if salt_detail["id"]==0:
        #         #For Insert New Salt Details
        #         del salt_detail["id"]
        #         salt_detail["id_thuoc"]=serializer.data["id"]
        #         serializer2 = ChiTietThuocSerializer(data=salt_detail,context={"request": request})
        #         serializer2.is_valid()
        #         serializer2.save()
        #     else:
        #         #For Update Salt Details
        #         queryset2 = ChiTietThuoc.objects.all()
        #         medicine_salt = get_object_or_404(queryset2,pk=salt_detail["id"])
        #         del salt_detail["id"]
        #         serializer3 = ChiTietThuocSerializer(medicine_salt,data=salt_detail,context={"request":request})
        #         serializer3.is_valid()
        #         serializer3.save()
        #         print("UPDATE")

        return Response({"error":False,"message":"Cap Nhat Du Lieu Thanh Cong"})

    def destroy(self, request, id=None):
        queryset = Thuoc.objects.all()
        thuoc = get_object_or_404(queryset,id=id)
        thuoc.delete()
        return Response({"error":False,"message":f"Ban Ghi Voi id = {id} Da Duoc Xoa Thanh Cong"})

    @transaction.atomic
    def nhap(self, request, id=None, so_luong=None):
        try:
            thuoc = Thuoc.objects.filter(id=id)
            thuoc.update(so_luong_kha_dung=F('so_luong_kha_dung') + so_luong)
            ThuocLog.objects.create(thuoc=thuoc[0], ngay=timezone.now(), quy_trinh=ThuocLog.IN, so_luong=so_luong)
            return Response({"error": False, "message": f"Nhap Thuoc Thanh Cong: {so_luong} {thuoc[0].ten_thuoc}"})
        except:
            return Response({"error": True, "message": "Loi Tao Log Thuoc"})

    @transaction.atomic
    def xuat(self, request, id=None, so_luong=None):
        try:
            thuoc = Thuoc.objects.filter(id=id)
            print(thuoc[0].kha_dung)
            if thuoc[0].kha_dung:
                thuoc.update(so_luong_kha_dung=F('so_luong_kha_dung') - so_luong)
                ThuocLog.objects.create(thuoc=thuoc[0], ngay=timezone.now(), quy_trinh=ThuocLog.OUT, so_luong=so_luong)
            else:
                return Response({"error": True, "message": "So Luong Thuoc Kha Dung = 0, Khong The Xuat Thuoc"})  
            return Response({"error": False, "message": f"Xuat Thuoc Thanh Cong: {so_luong} {thuoc[0].ten_thuoc}"})
        except:
            
            return Response({"error": True, "message": "Loi Tao Log Thuoc"})

class CongTyViewSet(viewsets.ViewSet):
    # authentication_class = [JWTAuthentication] # comment out this for testing
    # permission_classes = [IsAuthenticated] # comment out this for testing

    def list(self, request):
        cong_ty = CongTy.objects.all()
        serializer = CongTySerializer(cong_ty, many=True, context={"request": request})
        cong_ty_data = serializer.data
        return Response({"error":False, "message": "Danh Sach Cong Ty", "data": cong_ty_data})
    
    def create(self, request):
        try:
            serializer = CongTySerializer(data=request.data, context={'request': request})
            serializer.is_valid(raise_exception = True)
            serializer.save()
            response = {"error": False, "message": "Luu Du Lieu Cong Ty Thanh Cong"}
        except:
            response = {"error": True, "message": "Xay Ra Loi Trong Khi Luu Du Lieu Cong Ty"}
        return Response(response)

    def retrieve(self, request, pk=None):
        queryset = CongTy.objects.all()
        cong_ty = get_object_or_404(queryset, pk=pk)
        serializer = CongTySerializer(cong_ty, context={"request": request})
        serializer_data = serializer.data
        return Response({"error": False, "message": "Chi Tiet Ban Ghi", "data": serializer_data})

    def update(self, request, pk=None):
        try:
            queryset=CongTy.objects.all()
            cong_ty=get_object_or_404(queryset,pk=pk)
            serializer=CongTySerializer(cong_ty,data=request.data,context={"request":request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            dict_response={"error":False,"message":"Cap Nhat Du Lieu Cong Ty Thanh Cong"}
        except:
            dict_response={"error":True,"message":"Xay Ra Loi Trong Khi Cap Nhat Du Lieu Cong Ty"}

        return Response(dict_response)

    def destroy(self, request, pk=None):
        queryset = CongTy.objects.all()
        cong_ty = get_object_or_404(queryset,pk=pk)
        cong_ty.delete()
        return Response({"error":False,"message":f"Ban Ghi Voi pk = {pk} Da Duoc Xoa"})