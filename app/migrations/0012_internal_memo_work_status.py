from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('app', '0011_internal_memo_require_review')]

    operations = [
        migrations.AddField(
            model_name='internalmemo',
            name='work_status',
            field=models.CharField(
                blank=True,
                choices=[
                    ('ACKNOWLEDGED', 'รับทราบ'),
                    ('IN_PROGRESS', 'อยู่ระหว่างดำเนินงาน'),
                    ('DONE', 'เสร็จสิ้น'),
                ],
                max_length=16,
            ),
        ),
        migrations.AddField(
            model_name='internalmemo',
            name='work_status_updated_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
