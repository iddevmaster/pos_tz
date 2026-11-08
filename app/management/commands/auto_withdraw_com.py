import calendar
import os
from datetime import datetime

import requests
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction

from app.models import User, fact_commission
from app.views.finance import _cash_commissions_pending, create_com_income


def send_discord(text):
    """ส่งข้อความเข้า Discord webhook (ตั้งค่าใน env DISCORD_WEBHOOK_URL หรือ settings.DISCORD_WEBHOOK_URL)"""
    url = os.environ.get('DISCORD_WEBHOOK_URL') or getattr(settings, 'DISCORD_WEBHOOK_URL', '')
    if not url:
        return False
    if len(text) > 1900:  # Discord จำกัด 2000 ตัวอักษรต่อข้อความ
        text = text[:1900] + '\n...(ตัดข้อความ)'
    try:
        requests.post(url, json={'content': text}, timeout=10).raise_for_status()
        return True
    except requests.RequestException:
        return False


def user_label(uid):
    u = User.objects.filter(id=uid).only('first_name', 'last_name', 'username').first()
    if u is None:
        return f'user {uid}'
    name = f'{u.first_name} {u.last_name}'.strip() or u.username
    return f'{name} (#{uid})'


class Command(BaseCommand):
    help = ('เบิกค่าคอมอัตโนมัติ (เหมือนกดปุ่มเบิกค่าตอบแทนในหน้า finance/sale/com ให้ทุกคน) '
            'รันเฉพาะวันที่ 20 และวันสุดท้ายของเดือน เว้นแต่ใส่ --force')

    def add_arguments(self, parser):
        parser.add_argument('--force', action='store_true', help='รันทันทีโดยไม่เช็ควันที่')
        parser.add_argument('--dry-run', action='store_true', help='แสดงรายการที่จะเบิก ไม่บันทึก')
        parser.add_argument('--user', type=int, help='เบิกเฉพาะ user_id นี้')
        parser.add_argument('--no-discord', action='store_true', help='ไม่ส่งแจ้งเตือน Discord')

    def handle(self, *args, **options):
        started = datetime.now()
        today = started.date()
        last_day = calendar.monthrange(today.year, today.month)[1]
        if not options['force'] and today.day not in (20, last_day):
            self.stdout.write(f'{today}: ไม่ใช่วันตัดรอบ (20 / {last_day}) ข้าม')
            return

        dry = options['dry_run']
        if options['user']:
            user_ids = [options['user']]
        else:
            user_ids = list(fact_commission.objects
                            .filter(status='N', user_id__isnull=False)
                            .values_list('user_id', flat=True).distinct())

        total = 0
        lines, errors = [], []
        for uid in user_ids:
            rows = _cash_commissions_pending(uid)
            if not rows:
                continue
            if dry:
                done = [r.commit_id for r in rows]
            else:
                try:
                    with transaction.atomic():
                        done = create_com_income(rows)
                except Exception as e:
                    errors.append(f'• {user_label(uid)}: {e}')
                    self.stderr.write(f'user {uid}: error {e}')
                    continue
            if done:
                lines.append(f'• {user_label(uid)}: {len(done)} รายการ')
                self.stdout.write(f'user {uid}: {len(done)} รายการ {done}')
                total += len(done)

        finished = datetime.now()
        prefix = '[dry-run] ' if dry else ''
        self.stdout.write(f'{prefix}{today}: รวม {total} รายการ')

        if options['no_discord']:
            return
        icon = '🧪' if dry else ('⚠️' if errors else '✅')
        msg = [
            f'{icon} **{prefix}เบิกค่าคอมอัตโนมัติ**',
            f'เริ่ม: {started:%Y-%m-%d %H:%M:%S}',
            f'เสร็จ: {finished:%Y-%m-%d %H:%M:%S} ({(finished - started).total_seconds():.1f} วินาที)',
            f'รวม: **{total}** รายการ จาก {len(lines)} คน',
        ]
        if lines:
            msg += [''] + lines
        if errors:
            msg += ['', '**ผิดพลาด:**'] + errors
        if not send_discord('\n'.join(msg)):
            self.stderr.write('ส่ง Discord ไม่สำเร็จ (ยังไม่ได้ตั้ง DISCORD_WEBHOOK_URL หรือเชื่อมต่อไม่ได้)')
