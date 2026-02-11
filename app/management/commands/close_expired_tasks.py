from django.core.management.base import BaseCommand
from django.utils import timezone

class Command(BaseCommand):
    help = 'คำอธิบายคำสั่งของคุณ'

    def handle(self, *args, **kwargs):
        self.stdout.write("เริ่มทำงานตอน: " + str(timezone.now()))
        # ใส่ Logic ที่ต้องการทำตรงนี้