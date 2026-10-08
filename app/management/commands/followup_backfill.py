from collections import Counter

from django.core.management.base import BaseCommand

from app.customer_followup import process_alerts, sync_new_followups, today


class Command(BaseCommand):
    help = 'ติดตามลูกค้าเก่า: ดึง salesorder ย้อนหลังเข้าทะเบียนติดตาม (รันครั้งเดียวหลัง migrate)'

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true', help='แสดงจำนวนที่จะสร้าง ไม่บันทึก')

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        created = sync_new_followups(dry_run=dry_run)
        prefix = '[dry-run] ' if dry_run else ''
        self.stdout.write(f'{prefix}สร้างทะเบียนติดตาม {len(created)} รายการ')
        by_year = Counter(f.due_date.year for f in created)
        for year in sorted(by_year):
            self.stdout.write(f'{prefix}  ครบกำหนดปี {year}: {by_year[year]} รายการ')
        due_now = [f for f in created if (f.due_date - today()).days <= 90]
        self.stdout.write(f'{prefix}เข้าเกณฑ์เตือนทันที (<= 90 วัน): {len(due_now)} รายการ')
        if not dry_run:
            self.stdout.write(f'ส่งการเตือน {len(process_alerts(today()))} รายการ')
