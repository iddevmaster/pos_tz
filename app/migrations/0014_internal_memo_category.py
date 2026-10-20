import django.db.models.deletion
from django.db import migrations, models


DEFAULT_CATEGORIES = [
    'ยกเลิกบิลในวัน',
    'ยกเลิกบิลข้ามวัน',
    'เรื่องงานขาย',
    'อื่นๆ',
]


def seed_categories(apps, schema_editor):
    InternalMemoCategory = apps.get_model('app', 'InternalMemoCategory')
    for index, name in enumerate(DEFAULT_CATEGORIES, start=1):
        InternalMemoCategory.objects.get_or_create(
            name=name, defaults={'sort_order': index * 10}
        )


class Migration(migrations.Migration):
    dependencies = [
        ('app', '0013_internal_memo_work_log'),
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
            options={
                'ordering': ('sort_order', 'name'),
            },
        ),
        migrations.AddField(
            model_name='internalmemo',
            name='category',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='memos',
                to='app.internalmemocategory',
            ),
        ),
        migrations.RunPython(seed_categories, migrations.RunPython.noop),
    ]
