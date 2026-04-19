from django.core.management.base import BaseCommand
import requests
from app.models import notifications,category_program_permission, course_event, customers, location_thai, course,fact_signature, register_main, register_payment, register_payment_items, student,register_ref, register_applove, user_group, user_detail, event_register,salesorder,desciption_bill,factbilldes,teacher_income_setting,User,document,teacher,signature,add_on,fact_addon,training,fact_teacher_user,commissionstages,fact_commission,fact_customer
from app.functions import addDay, addYear, dateTimeNow, dmytoymd,checkpermi

class Command(BaseCommand):
    help = 'My cron job'

    def handle(self, *args, **kwargs):
       

        TOKEN = "8739307260:AAGLXH1vx2_1xpnRdeLA5Uaw7fcV1j2nB0I"
        CHAT_ID = "-1003830011664"

        msg = ""

        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

        content = course_event.objects.select_related('course').filter(status='I')

        for rs in content:

            course_list = course.objects.filter(course_id=rs.course.course_id).first()
            msg = '-' + course_list.course_name + ' รุ่นที่ ' + str(rs.ev_generation) + ' วันที่ ' + str(rs.ev_date_start) + ' ถึง ' + str(rs.ev_date_end) + ' ครบกำหนด ปิดงานแล้ว '
            

            noti = notifications(
                 notification_type='app',
                 title='แจ้งเตือน',
                 message=msg,
                 reference_id='123',
                 reference_type='task',
                 is_read='false',
                 read_at=dateTimeNow(),
                 action_url='/approve/update/processevent',
                 priority='easy',
                 user_id=3,
                 created_by='1',cm_id=10,
                 crt_date=dateTimeNow(),
                 upd_date=dateTimeNow())
            noti.save()
            requests.post(url, data={
            "chat_id": CHAT_ID,
            "text": msg
        })
      

        
        # เขียน logic ของคุณตรงนี้