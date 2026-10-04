from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def migrate_pending_status(apps, schema_editor):
    InternalMemo = apps.get_model('app', 'InternalMemo')
    InternalMemo.objects.filter(
        status='DRAFT', reviewer__isnull=True
    ).update(reviewer_id=models.F('approver_id'))
    InternalMemo.objects.filter(status='PENDING').update(
        status='PENDING_APPROVAL'
    )


def restore_pending_status(apps, schema_editor):
    InternalMemo = apps.get_model('app', 'InternalMemo')
    InternalMemo.objects.filter(
        status__in=['PENDING_REVIEW', 'PENDING_APPROVAL']
    ).update(status='PENDING')


class Migration(migrations.Migration):
    dependencies = [
        ('app', '0006_internal_memo_sidebar'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='internalmemo',
            name='reviewer',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='internal_memos_to_review',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name='internalmemo',
            name='reviewed_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='internalmemo',
            name='reviewer_note',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='internalmemo',
            name='status',
            field=models.CharField(
                choices=[
                    ('DRAFT', 'ฉบับร่าง'),
                    ('PENDING_REVIEW', 'รอผู้ตรวจสอบ ชั้น 1'),
                    ('PENDING_APPROVAL', 'รอผู้อนุมัติ ชั้น 2'),
                    ('APPROVED', 'อนุมัติแล้ว'),
                    ('REJECTED', 'ไม่อนุมัติ'),
                ],
                default='DRAFT',
                max_length=16,
            ),
        ),
        migrations.RunPython(migrate_pending_status, restore_pending_status),
    ]
