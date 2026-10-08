from datetime import date

from django.core.management.base import BaseCommand

from app.customer_followup import run_daily


class Command(BaseCommand):
    help = 'ติดตามลูกค้าเก่า: สร้างทะเบียน เตือน 90/60/30 วัน ย้ายไปลูกค้าตกค้าง (รันวันละครั้ง)'

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true', help='คำนวณอย่างเดียว ไม่บันทึก')
        parser.add_argument('--date', help='จำลองวันที่รัน YYYY-MM-DD')

    def handle(self, *args, **options):
        run_date = date.fromisoformat(options['date']) if options['date'] else None
        result = run_daily(run_date=run_date, dry_run=options['dry_run'])
        prefix = '[dry-run] ' if options['dry_run'] else ''
        for key, value in result.items():
            self.stdout.write(f'{prefix}{key}: {value}')
