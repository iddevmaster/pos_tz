from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


def add_internal_memo_permissions(apps, schema_editor):
    Permission = apps.get_model('app', 'category_program_permission')
    old_permissions = Permission.objects.filter(
        page_route='approve/documents/internal'
    )
    for old in old_permissions:
        for route, label in (
            ('internal-memos/', 'ทะเบียนบันทึกภายใน'),
            ('internal-memos/approval/', 'อนุมัติบันทึกภายใน'),
        ):
            Permission.objects.get_or_create(
                cm_id=old.cm_id,
                page_route=route,
                defaults={
                    'id': uuid.uuid4().hex[:24],
                    'page_label': label,
                    'group_value': old.group_value,
                    'group_label': old.group_label,
                },
            )


def remove_internal_memo_permissions(apps, schema_editor):
    Permission = apps.get_model('app', 'category_program_permission')
    Permission.objects.filter(
        page_route__in=['internal-memos/', 'internal-memos/approval/']
    ).delete()


class Migration(migrations.Migration):
    dependencies = [
        ('app', '0004_move_certificate_permission_to_settings'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='InternalMemo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('memo_number', models.CharField(blank=True, max_length=24, unique=True)),
                ('recipient', models.CharField(max_length=255)),
                ('subject', models.CharField(max_length=255)),
                ('branch', models.CharField(default='สำนักงานใหญ่', max_length=128)),
                ('detail', models.TextField()),
                ('status', models.CharField(choices=[('DRAFT', 'ฉบับร่าง'), ('PENDING', 'รออนุมัติ'), ('APPROVED', 'อนุมัติแล้ว'), ('REJECTED', 'ไม่อนุมัติ')], default='DRAFT', max_length=16)),
                ('submitted_at', models.DateTimeField(blank=True, null=True)),
                ('decided_at', models.DateTimeField(blank=True, null=True)),
                ('decision_note', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('approver', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='internal_memos_to_approve', to=settings.AUTH_USER_MODEL)),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='created_internal_memos', to=settings.AUTH_USER_MODEL)),
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
        migrations.RunPython(
            add_internal_memo_permissions,
            remove_internal_memo_permissions,
        ),
    ]
