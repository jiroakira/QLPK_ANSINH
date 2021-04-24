
from django.urls import path
from . import consumer

websocket_urlpatterns = [
    # path("ws/polData/", consumer.DashConsumer.as_asgi()),
    # # path("ws/test/<int:user_id>/", consumer.CheckupProcessConsumer.as_asgi()),
    path('ws/checkup_process/<int:user_id>/', consumer.CheckupProcessConsumer.as_asgi()),
    path('ws/funcroom_info/service/<int:id_dich_vu>/', consumer.FuncroomInfor.as_asgi()),
    path('ws/first_process_notification/<int:user_id>/', consumer.FirstProcessNoti.as_asgi()),
    path('ws/checkup_process_notification/<int:user_id>/', consumer.CheckupProcessNoti.as_asgi()),
    path('ws/prescription_noti/<int:user_id>/', consumer.PrescriptionNoti.as_asgi()),
    path('ws/charge_bill/<int:user_id>/', consumer.ChargeBillNoti.as_asgi()),
    path('ws/charge_prescription_bill/<int:user_id>/', consumer.ChargePrescriptionBillNoti.as_asgi()),
    path('ws/charge_process_bill/<int:user_id>/', consumer.ChargeProcessBillNoti.as_asgi()),
    path('ws/process_accomplished/<int:user_id>/', consumer.ProcessAccomplishedNoti.as_asgi()),
]
