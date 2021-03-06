from clinic.views import phan_khoa_kham
from clinic.serializers import DanhSachPhanKhoaSerializer
from clinic.models import ChuoiKham, DichVuKham, PhanKhoaKham, User
from datetime import timedelta
from django.utils import timezone
from channels.generic.websocket import AsyncWebsocketConsumer, AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
import json
from django.db.models import Count, F, Sum, Q

# class DashConsumer(AsyncWebsocketConsumer):
    
#     async def connect(self):
#         self.groupname='dashboard'
#         await self.channel_layer.group_add(
#             self.groupname,
#             self.channel_name,
#         )

#         await self.accept()

#     async def disconnect(self, close_code):

#         await self.channel_layer.group_discard(
#             self.groupname,
#             self.channel_name
#         )
    
#     async def receive(self, text_data):
#         datapoint = json.loads(text_data)
#         print(datapoint)
#         val = datapoint['value']

#         await self.channel_layer.group_send(
#             self.groupname,
#             {
#                 'type': 'deprocessing',
#                 'value': val
#             }
#         )

#         print ('>>>>',text_data)

#         # pass

#     async def deprocessing(self, event):
#         print(event)

#         valOther = event['value']

#         await self.send(text_data=json.dumps({'value': valOther}))


class CheckupProcessConsumer(AsyncJsonWebsocketConsumer):
    async def websocket_connect(self, event):
        print("Connected", event)
        print(self.scope)
        await self.channel_layer.group_add(
            f"user_{self.scope['url_route']['kwargs']['user_id']}",
            self.channel_name
        )

        await self.accept()

        context = await self.get_process_checkup(self.scope)
        
        await self.send_json(content=context)


    async def websocket_disconnect(self, event):
        print("RECEIVE", event)
        await self.send(text_data='HELLO')

    # async def receive_json(self, content):
    #     # data = json.loads(content)
    #     print(content)
    async def websocket_receive(self, content):
        print("RECEIVE")
        await self.channel_layer.group_send(
            f"user_{self.scope['url_route']['kwargs']['user_id']}",
            {
                'type': 'checkup_process_info',
                'value': content
            }
        )
        # await self.send(content='HELLO')
        print ('>>>>', content)


    async def checkup_process_info(self, event):
        context = await self.get_process_checkup(self.scope)
        
        await self.send_json(content=context)

    @database_sync_to_async
    def get_process_checkup(self, scope):
        user_id = self.scope['url_route']['kwargs']['user_id']
        now = timezone.localtime(timezone.now())
        tomorrow = now + timedelta(1)
        today_start = now.replace(hour=0, minute=0, second=0)
        today_end = tomorrow.replace(hour=0, minute=0, second=0)
        user = User.objects.get(id=user_id)
        
        chuoi_kham = ChuoiKham.objects.filter(benh_nhan=user, thoi_gian_tao__lt=today_end, thoi_gian_tao__gte=today_start).order_by('-thoi_gian_tao').first()
        if chuoi_kham:
            danh_sach_phan_khoa = chuoi_kham.phan_khoa_kham.all()
            # serializer = DanhSachPhanKhoaSerializer(danh_sach_phan_khoa, many=True, context={'request': request})
            serializer = DanhSachPhanKhoaSerializer(danh_sach_phan_khoa, many=True)
            data = serializer.data
            context = {
                'benh_nhan': user_id,
                'data': data
            }
       
        else:
            context = {
                'benh_nhan': user_id,
                'data': []  
            }
        return context

class FuncroomInfor(AsyncJsonWebsocketConsumer):
    async def websocket_connect(self, event):
        print("Connected", event)
        print(self.scope)
        await self.channel_layer.group_add(
            f"funcroom_service",
            self.channel_name
        )

        await self.accept()

        context = await self.get_funcroom_info(self.scope)
        
        await self.send_json(content=context)

    async def websocket_disconnect(self, event):
        print("Disconnect", event)
        await self.send(text_data='HELLO')

    async def websocket_receive(self, content):
        print("RECEIVE")
        await self.channel_layer.group_send(
            f"funcroom_service",
            {
                'type': 'funcroom_info',
                'value': content
            }
        )
        # await self.send(content='HELLO')
        print ('>>>>', content)
    
    async def funcroom_info(self, event):
        context = await self.get_funcroom_info(self.scope)
        
        await self.send_json(content=context)

    @database_sync_to_async
    def get_funcroom_info(self, scope):
        id_dich_vu = self.scope['url_route']['kwargs']['id_dich_vu']
    
        dich_vu = DichVuKham.objects.get(id=id_dich_vu)
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
            if i['count'] != 0 and i['trang_thai__trang_thai_khoa_kham'] == "??ang Th???c Hi???n":
                count_processing += 1
            elif i['count'] != 0 and i['trang_thai__trang_thai_khoa_kham'] == "Ho??n Th??nh":
                count_finished += 1
            elif i['count'] != 0 and i['trang_thai__trang_thai_khoa_kham'] == None:
                count_pending += 1
        context = {
            'phong_chuc_nang': phong_chuc_nang.ten_phong_chuc_nang,
            'dang_cho': count_pending,
            'dang_thuc_hien': count_processing,
            'hoan_thanh': count_finished,
        }
        return context

class FirstProcessNoti(AsyncJsonWebsocketConsumer):
    async def websocket_connect(self, event):
        print("Connected", event)
        print(self.scope)
        await self.channel_layer.group_add(
            f"first_process_user_{self.scope['url_route']['kwargs']['user_id']}",
            self.channel_name
        )

        await self.accept()
    
    async def websocket_disconnect(self, event):
        print("Disconnect", event)
        await self.send(text_data="hello")

    async def websocket_receive(self, content):
        print("Receive")
        await self.channel_layer.group_send(
            f"first_process_user_{self.scope['url_route']['kwargs']['user_id']}",
            {
                'type': 'first_process_notification',
                'value': content
            }
        )
        print ('>>>>', content)

    async def first_process_notification(self, event):
        context = {
            'title': 'Th??ng B??o ????ng Ph??',
            'body': 'B???n Vui L??ng Di Chuy???n T???i Ph??ng T??i Ch??nh \n ????? ????ng Ph?? L??m S??ng',
        }

        

        await self.send_json(content=context)

class CheckupProcessNoti(AsyncJsonWebsocketConsumer):
    async def websocket_connect(self, event):
        print("Connected", event)
        print(self.scope)
        await self.channel_layer.group_add(
            f"checkup_process_user_{self.scope['url_route']['kwargs']['user_id']}",
            self.channel_name
        )

        await self.accept()
    
    async def websocket_disconnect(self, event):
        print("Disconnect", event)
        await self.send(text_data="hello")

    async def websocket_receive(self, content):
        print("Receive")
        await self.channel_layer.group_send(
            f"checkup_process_user_{self.scope['url_route']['kwargs']['user_id']}",
            {
                'type': 'checkup_process_notification',
                'value': content
            }
        )
        print ('>>>>', content)

    async def checkup_process_notification(self, event):
        context = {
            'title': 'Th??ng B??o',
            'body': 'B???n Vui L??ng Di Chuy???n T???i Ph??ng T??i Ch??nh \n ????? Thanh To??n H??a ????n D???ch V??? \n(B???m v??o ????y ????? bi???t chi ti???t h??a ????n)',
        } 

        

        await self.send_json(content=context)


class PrescriptionNoti(AsyncJsonWebsocketConsumer):
    async def websocket_connect(self, event):
        print("Connected", event)
        print(self.scope)
        await self.channel_layer.group_add(
            f"prescription_user_{self.scope['url_route']['kwargs']['user_id']}",
            self.channel_name
        )

        await self.accept()
    
    async def websocket_disconnect(self, event):
        print("Disconnect", event)
        await self.send(text_data="hello")

    async def websocket_receive(self, content):
        print("Receive")
        await self.channel_layer.group_send(
            f"prescription_user_{self.scope['url_route']['kwargs']['user_id']}",
            {
                'type': 'prescription_notification',
                'value': content
            }
        )
        print ('>>>>', content)

    async def prescription_notification(self, event):
        context = {
            'title': 'Th??ng B??o',
            'body': 'B???n Vui L??ng Di Chuy???n T???i Ph??ng T??i Ch??nh ????? \n Thanh To??n H??a ????n Thu???c \n (B???m v??o ????y ????? bi???t chi ti???t h??a ????n)',
        }

        

        await self.send_json(content=context)

class CancelAppointment(AsyncJsonWebsocketConsumer):
    async def websocket_connect(self, event):
        print("Connected", event)
        print(self.scope)
        await self.channel_layer.group_add(
            f"appointment_{self.scope['url_route']['kwargs']['appointment_id']}",
            self.channel_name
        )

        await self.accept()

        # context = await self.get_process_checkup(self.scope)
        # # 
        # await self.send_json(content=context)

    async def websocket_disconnect(self, event):
        print("Disconnect", event)
        await self.send(text_data='HELLO')

    async def websocket_receive(self, content):
        print("Receive")
        await self.channel_layer.group_send(
            f"appointment_{self.scope['url_route']['kwargs']['appointment_id']}",
            {
                'type': 'cancel_appointment',
                'value': content
            }
        )
        # await self.send(content='HELLO')
        print ('>>>>', content)

    async def cancel_appointment(self, event):
        context = await self.get_upcoming_appointment(self.scope)
        
        await self.send_json(content=context)

    @database_sync_to_async
    def get_upcoming_appointment(self, scope):
        pass

class ChargeBillNoti(AsyncJsonWebsocketConsumer):
    async def websocket_connect(self, event):
        print("Connected", event)
        print(self.scope)
        await self.channel_layer.group_add(
            f"charge_bill_user_{self.scope['url_route']['kwargs']['user_id']}",
            self.channel_name
        )

        await self.accept()
    
    async def websocket_disconnect(self, event):
        print("Disconnect", event)
        await self.send(text_data="hello")

    async def websocket_receive(self, content):
        print("Receive")
        await self.channel_layer.group_send(
            f"charge_bill_user_{self.scope['url_route']['kwargs']['user_id']}",
            {
                'type': 'charge_bill_notification',
                'value': content
            }
        )
        print ('>>>>', content)

    async def charge_bill_notification(self, event):
        context = {
            'title': 'Th??ng B??o',
            'body': 'B???n Vui L??ng Di Chuy???n T???i Ph??ng Kh??m L??m S??ng \n????? Th???c Hi???n Kh??m',
        } 

        

        await self.send_json(content=context)

class ChargePrescriptionBillNoti(AsyncJsonWebsocketConsumer):
    async def websocket_connect(self, event):
        print("Connected", event)
        print(self.scope)
        await self.channel_layer.group_add(
            f"charge_prescription_user_{self.scope['url_route']['kwargs']['user_id']}",
            self.channel_name
        )

        await self.accept()
    
    async def websocket_disconnect(self, event):
        print("Disconnect", event)
        await self.send(text_data="hello")

    async def websocket_receive(self, content):
        print("Receive")
        await self.channel_layer.group_send(
            f"charge_prescription_user_{self.scope['url_route']['kwargs']['user_id']}",
            {
                'type': 'charge_prescription_notification',
                'value': content
            }
        )
        print ('>>>>', content)

    async def charge_prescription_notification(self, event):
        context = {
            'title': 'Th??ng B??o',
            'body': 'B???n Vui L??ng Di Chuy???n T???i Ph??ng Thu???c \n????? L???y Thu???c',
        } 

        

        await self.send_json(content=context)

class ChargeProcessBillNoti(AsyncJsonWebsocketConsumer):
    async def websocket_connect(self, event):
        print("Connected", event)
        print(self.scope)
        await self.channel_layer.group_add(
            f"charge_process_bill_{self.scope['url_route']['kwargs']['user_id']}",
            self.channel_name
        )

        await self.accept()
    
    async def websocket_disconnect(self, event):
        print("Disconnect", event)
        await self.send(text_data="hello")

    async def websocket_receive(self, content):
        print("Receive")
        await self.channel_layer.group_send(
            f"charge_process_bill_{self.scope['url_route']['kwargs']['user_id']}",
            {
                'type': 'charge_process_bill_notification',
                'value': content
            }
        )
        print ('>>>>', content)

    async def charge_process_bill_notification(self, event):
        context = {
            'title': 'Th??ng B??o',
            'body': 'B???n Vui L??ng Di Chuy???n T???i C??c Ph??ng Ch???c N??ng \n????? Th???c Hi???n Kh??m \n(Tham Kh???o S??? Th??? T??? Trong Ti???n Tr??nh Kh??m)\n',
        } 

        

        await self.send_json(content=context)


class ProcessAccomplishedNoti(AsyncJsonWebsocketConsumer):
    async def websocket_connect(self, event):
        print("Connected", event)
        print(self.scope)
        await self.channel_layer.group_add(
            f"process_accomplished_user_{self.scope['url_route']['kwargs']['user_id']}",
            self.channel_name
        )

        await self.accept()
    
    async def websocket_disconnect(self, event):
        print("Disconnect", event)
        await self.send(text_data="hello")

    async def websocket_receive(self, content):
        print("Receive")
        await self.channel_layer.group_send(
            f"process_accomplished_user_{self.scope['url_route']['kwargs']['user_id']}",
            {
                'type': 'process_accomplished_notification',
                'value': content
            }
        )
        print ('>>>>', content)

    async def process_accomplished_notification(self, event):
        context = {
            'title': 'Th??ng B??o',
            'body': 'B???n ???? Ho??n Th??nh L???ch Tr??nh Kh??m L???n N??y',
        } 

        

        await self.send_json(content=context)