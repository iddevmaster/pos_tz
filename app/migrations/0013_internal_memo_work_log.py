import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('app', '0012_internal_memo_work_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='internalmemo',
            name='work_status_updated_by',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='+',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.CreateModel(
            name='InternalMemoWorkLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('work_status', models.CharField(
                    choices=[
                        ('ACKNOWLEDGED', 'รับทราบ'),
                        ('IN_PROGRESS', 'อยู่ระหว่างดำเนินงาน'),
                        ('DONE', 'เสร็จสิ้น'),
                    ],
                    max_length=16,
                )),
                ('note', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('memo', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='work_logs',
                    to='app.internalmemo',
                )),
                ('updated_by', models.ForeignKey(
                    on_delete=django.db.models.deletion.PROTECT,
                    related_name='internal_memo_work_logs',
                    to=settings.AUTH_USER_MODEL,
                )),
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
                ('log', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='images',
                    to='app.internalmemoworklog',
                )),
            ],
        ),
    ]
