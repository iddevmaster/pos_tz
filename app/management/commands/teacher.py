from django.core.management.base import BaseCommand
import requests
from datetime import timedelta
from app.models import notifications,category_program_permission, course_event, customers, location_thai, course,fact_signature, register_main, register_payment, register_payment_items, student,register_ref, register_applove, user_group, user_detail, event_register,salesorder,desciption_bill,factbilldes,teacher_income_setting,User,document,teacher,signature,add_on,fact_addon,training,fact_teacher_user,commissionstages,fact_commission,fact_customer
from app.functions import addDay, addYear, dateTimeNow, dmytoymd,checkpermi
from django.utils import timezone

class Command(BaseCommand):
    help = 'My cron job'

    def handle(self, *args, **kwargs):
       

        TOKEN = "8739307260:AAGLXH1vx2_1xpnRdeLA5Uaw7fcV1j2nB0I"
        CHAT_ID = "-1003830011664"

        msg = ""

        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

        teacher_income = teacher_income_setting.objects.filter(status='I') .values('teacher_id').distinct()
        today = timezone.now().date()
        if today.day == 22:
         for rs in teacher_income:
            msg = 'แจ้งเตือนกดเบิกเงินครูฝึก'
            
            uuid_without_dashes = str(rs['teacher_id']).replace('-', '')
            teac = fact_teacher_user.objects.get(teacher_id=uuid_without_dashes)
            getuser = user_detail.objects.get(user_id=teac.user_id)
           
            
          
            noti = notifications(
                 notification_type='app',
                 title='แจ้งเตือน',
                 message=msg + '-' +uuid_without_dashes,
                 reference_id='123',
                 reference_type='task',
                 is_read='false',
                 read_at=dateTimeNow(),
                 action_url='/finance/teacher',
                 priority='easy',
                 user_id=teac.user_id,
                 created_by='1',cm_id=getuser.cm_id,
                 crt_date=dateTimeNow(),
                 upd_date=dateTimeNow())
            noti.save()
            requests.post(url, data={
            "chat_id": CHAT_ID,
            "text": msg})
      

        
        # เขียน logic ของคุณตรงนี้