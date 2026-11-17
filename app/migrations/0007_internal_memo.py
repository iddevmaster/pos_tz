"""บันทึกภายใน (Internal Memo) — port จาก branch uat_tz (migrations 0005-0007, 0011-0014 รวมเป็นไฟล์เดียว)"""
import uuid

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


DEFAULT_CATEGORIES = [
    'ยกเลิกบิลในวัน',
    'ยกเลิกบิลข้ามวัน',
    'เรื่องงานขาย',
    'อื่นๆ',
]

MENU_ITEMS = (
    ('internal-memos/create/', 'แบบฟอร์มบันทึกภายใน'),
    ('internal-memos/', 'ทะเบียนบันทึกภายใน'),
    ('internal-memos/approval/', 'ตรวจสอบ / อนุมัติ'),
)

WORK_STATUS_CHOICES = [
    ('ACKNOWLEDGED', 'รับทราบ'),
    ('IN_PROGRESS', 'อยู่ระหว่างดำเนินงาน'),
    ('DONE', 'เสร็จสิ้น'),
]


def seed_categories(apps, schema_editor):
    InternalMemoCategory = apps.get_model('app', 'InternalMemoCategory')
    for index, name in enumerate(DEFAULT_CATEGORIES, start=1):
        InternalMemoCategory.objects.get_or_create(
            name=name, defaults={'sort_order': index * 10}
        )


def add_internal_memo_permissions(apps, schema_editor):
    """ให้กลุ่มผู้ใช้ที่เข้าถึง 'เอกสารบันทึกภายใน' เดิม ได้เมนูบันทึกภายในใหม่"""
    Permission = apps.get_model('app', 'category_program_permission')
    category_ids = set(
        Permission.objects.filter(
            page_route='approve/documents/internal'
        ).values_list('cm_id', flat=True)
    )
    for cm_id in category_ids:
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


def remove_internal_memo_permissions(apps, schema_editor):
    Permission = apps.get_model('app', 'category_program_permission')
    Permission.objects.filter(group_value='internalMemo').delete()


class Migration(migrations.Migration):
    dependencies = [
        ('app', '0006_salesorder_er_fk_to_register_main'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='InternalMemoCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
                ('sort_order', models.PositiveIntegerField(default=0)),
                ('is_active', models.BooleanField(default=True)),
            ],
            options={'ordering': ('sort_order', 'name')},
        ),
        migrations.CreateModel(
            name='InternalMemo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('memo_number', models.CharField(blank=True, max_length=24, unique=True)),
                ('recipient', models.CharField(max_length=255)),
                ('subject', models.CharField(max_length=255)),
                ('branch', models.CharField(default='สำนักงานใหญ่', max_length=128)),
                ('detail', models.TextField()),
                ('require_review', models.BooleanField(default=True)),
                ('status', models.CharField(choices=[
                    ('DRAFT', 'ฉบับร่าง'),
                    ('PENDING_REVIEW', 'รอผู้ตรวจสอบ ชั้น 1'),
                    ('PENDING_APPROVAL', 'รอผู้อนุมัติ ชั้น 2'),
                    ('APPROVED', 'อนุมัติแล้ว'),
                    ('REJECTED', 'ไม่อนุมัติ'),
                ], default='DRAFT', max_length=16)),
                ('submitted_at', models.DateTimeField(blank=True, null=True)),
                ('reviewed_at', models.DateTimeField(blank=True, null=True)),
                ('reviewer_note', models.TextField(blank=True)),
                ('decided_at', models.DateTimeField(blank=True, null=True)),
                ('decision_note', models.TextField(blank=True)),
                ('work_status', models.CharField(blank=True, choices=WORK_STATUS_CHOICES, max_length=16)),
                ('work_status_updated_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='memos', to='app.internalmemocategory')),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='created_internal_memos', to=settings.AUTH_USER_MODEL)),
                ('reviewer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='internal_memos_to_review', to=settings.AUTH_USER_MODEL)),
                ('approver', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='internal_memos_to_approve', to=settings.AUTH_USER_MODEL)),
                ('work_status_updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('cc_users', models.ManyToManyField(blank=True, related_name='internal_memos_cc', to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ('-created_at',)},
        ),
        migrations.CreateModel(
            name='InternalMemoAttachment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='internal_memos/%Y/%m/')),
                ('original_name', models.CharField(max_length=255)),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('memo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attachments', to='app.internalmemo')),
            ],
        ),
        migrations.CreateModel(
            name='InternalMemoWorkLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('work_status', models.CharField(choices=WORK_STATUS_CHOICES, max_length=16)),
                ('note', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('memo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='work_logs', to='app.internalmemo')),
                ('updated_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='internal_memo_work_logs', to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ('-created_at',)},
        ),
        migrations.CreateModel(
            name='InternalMemoWorkImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='internal_memos/work/%Y/%m/')),
                ('original_name', models.CharField(max_length=255)),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('log', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='app.internalmemoworklog')),
            ],
        ),
        migrations.RunPython(seed_categories, migrations.RunPython.noop),
        migrations.RunPython(add_internal_memo_permissions, remove_internal_memo_permissions),
    ]
