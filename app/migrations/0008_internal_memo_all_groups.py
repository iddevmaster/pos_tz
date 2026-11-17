"""ให้ทุกกลุ่มผู้ใช้มีสิทธิ์เมนูบันทึกภายใน (ยกเว้น ตรวจสอบ / อนุมัติ)"""
import uuid

from django.db import migrations

MENU_ITEMS = (
    ('internal-memos/create/', 'แบบฟอร์มบันทึกภายใน'),
    ('internal-memos/', 'ทะเบียนบันทึกภายใน'),
    ('internal-memos/cc/', 'สำเนาถึง'),
    ('internal-memos/tracking/', 'ติดตามงาน'),
)


def grant_all_groups(apps, schema_editor):
    Category = apps.get_model('app', 'category_program')
    Permission = apps.get_model('app', 'category_program_permission')
    for cm_id in Category.objects.values_list('id', flat=True):
        for route, label in MENU_ITEMS:
            Permission.objects.get_or_create(
                cm_id=cm_id,
                page_route=route,
                defaults={
                    'id': uuid.uuid4().hex[:24],
                    'page_label': label,
                    'group_value': 'internalMemo',
                    'group_label': 'บันทึกภายใน',
                },
            )


class Migration(migrations.Migration):
    dependencies = [('app', '0007_internal_memo')]

    operations = [
        migrations.RunPython(grant_all_groups, migrations.RunPython.noop),
    ]
