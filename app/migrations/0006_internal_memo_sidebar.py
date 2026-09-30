import uuid

from django.db import migrations


def configure_internal_memo_sidebar(apps, schema_editor):
    Permission = apps.get_model('app', 'category_program_permission')
    existing = Permission.objects.filter(
        page_route__in=['internal-memos/', 'internal-memos/approval/']
    )
    category_ids = set(existing.values_list('cm_id', flat=True))

    # รองรับฐานข้อมูลที่ยังไม่มีเมนูใหม่ โดยอิงกลุ่มที่เข้าถึงเอกสารภายในเดิม
    if not category_ids:
        category_ids.update(
            Permission.objects.filter(
                page_route='approve/documents/internal'
            ).values_list('cm_id', flat=True)
        )

    menu_items = (
        ('internal-memos/create/', 'แบบฟอร์มบันทึกภายใน'),
        ('internal-memos/', 'ทะเบียนบันทึกภายใน'),
        ('internal-memos/approval/', 'ตรวจสอบ / อนุมัติ'),
    )
    for cm_id in category_ids:
        for route, label in menu_items:
            permission, _ = Permission.objects.get_or_create(
                cm_id=cm_id,
                page_route=route,
                defaults={
                    'id': uuid.uuid4().hex[:24],
                    'page_label': label,
                    'group_value': 'internalMemo',
                    'group_label': 'บันทึกภายใน',
                },
            )
            permission.page_label = label
            permission.group_value = 'internalMemo'
            permission.group_label = 'บันทึกภายใน'
            permission.save(update_fields=[
                'page_label', 'group_value', 'group_label'
            ])


def restore_internal_memo_sidebar(apps, schema_editor):
    Permission = apps.get_model('app', 'category_program_permission')
    Permission.objects.filter(
        page_route='internal-memos/create/'
    ).delete()
    Permission.objects.filter(
        page_route='internal-memos/'
    ).update(
        page_label='ทะเบียนบันทึกภายใน',
        group_value='z2NIxi',
        group_label='อนุมัติเอกสาร',
    )
    Permission.objects.filter(
        page_route='internal-memos/approval/'
    ).update(
        page_label='อนุมัติบันทึกภายใน',
        group_value='z2NIxi',
        group_label='อนุมัติเอกสาร',
    )


class Migration(migrations.Migration):
    dependencies = [('app', '0005_internal_memo')]

    operations = [
        migrations.RunPython(
            configure_internal_memo_sidebar,
            restore_internal_memo_sidebar,
        ),
    ]
