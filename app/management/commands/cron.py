from django.core.management.base import BaseCommand
import requests

class Command(BaseCommand):
    help = 'My cron job'

    def handle(self, *args, **kwargs):
        print("Cron job running...")

        TOKEN = "8739307260:AAGLXH1vx2_1xpnRdeLA5Uaw7fcV1j2nB0I"
        CHAT_ID = "-1003830011664"

        msg = "สวัสดีจาก Django 🚀"

        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

        requests.post(url, data={
            "chat_id": CHAT_ID,
            "text": msg
        })
        # เขียน logic ของคุณตรงนี้