import uuid

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


# cm_id: 1 ผู้ดูแลระบบ, 6 ฝ่ายขาย, 9 ผอ, 10 ผู้จัดการ, 11 กลุ่มสาขา,
#        12 ผจก การตลาด, 13 Saledesk, 15 ครูฝึก/ฝ่ายขาย, 16 รายงานฝ่ายขาย
SALE_CATEGORIES = (1, 6, 9, 10, 11, 12, 13, 15, 16)
REGISTRY_CATEGORIES = (1, 9, 10, 12, 13, 16)
MENU_ITEMS = (
    ('customer-followup', 'ติดตามลูกค้า', SALE_CATEGORIES),
    ('customer-followup/pool', 'ลูกค้าตกค้าง', SALE_CATEGORIES),
    ('customer-followup/registry', 'ทะเบียนติดตามลูกค้า', REGISTRY_CATEGORIES),
)


def add_followup_menu(apps, schema_editor):
    Category = apps.get_model('app', 'category_program')
    Permission = apps.get_model('app', 'category_program_permission')
    existing = set(Category.objects.values_list('id', flat=True))
    for route, label, categories in MENU_ITEMS:
        for cm_id in categories:
            if cm_id not in existing:
                continue
            Permission.objects.get_or_create(
                cm_id=cm_id,
                page_route=route,
                defaults={
                    'id': uuid.uuid4().hex[:24],
                    'page_label': label,
                    'group_value': 'customerFollowup',
                    'group_label': 'ติดตามลูกค้า',
                },
            )


def remove_followup_menu(apps, schema_editor):
    Permission = apps.get_model('app', 'category_program_permission')
    Permission.objects.filter(group_value='customerFollowup').delete()


class Migration(migrations.Migration):
    dependencies = [
        ('app', '0007_internal_memo_two_step_approval'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='customer_followup',
            fields=[
                ('followup_id', models.AutoField(primary_key=True, serialize=False)),
                ('source_sale_id', models.IntegerField(blank=True, null=True)),
                ('source_doc_no', models.CharField(blank=True, default='', max_length=256)),
                ('customer_name', models.CharField(blank=True, default='', max_length=256)),
                ('customer_tax', models.CharField(blank=True, default='', max_length=64)),
                ('customer_phone', models.CharField(blank=True, default='', max_length=64)),
                ('base_date', models.DateField()),
                ('due_date', models.DateField()),
                ('alert_level', models.IntegerField(default=0)),
                ('first_alert_date', models.DateField(blank=True, null=True)),
                ('last_alert_date', models.DateField(blank=True, null=True)),
                ('followup_count', models.IntegerField(default=0)),
                ('last_followup_date', models.DateField(blank=True, null=True)),
                ('protect_until', models.DateField(blank=True, null=True)),
                ('status', models.CharField(choices=[('waiting', 'ยังไม่ถึงกำหนดเตือน'), ('alerting', 'เตือนแล้ว รอติดตาม'), ('following', 'กำลังติดตาม'), ('quoted', 'ออกใบเสนอราคาใหม่แล้ว'), ('won', 'ปิดการขายแล้ว'), ('pool', 'ลูกค้าตกค้าง')], default='waiting', max_length=16)),
                ('pool_date', models.DateTimeField(blank=True, null=True)),
                ('claim_until', models.DateField(blank=True, null=True)),
                ('new_doc_no', models.CharField(blank=True, default='', max_length=256)),
                ('crt_date', models.DateTimeField(auto_now_add=True)),
                ('upd_date', models.DateTimeField(auto_now=True)),
                ('claimed_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='followup_claimed', to=settings.AUTH_USER_MODEL)),
                ('course', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='app.course')),
                ('new_register', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='followup_renewal', to='app.register_main')),
                ('original_sale', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='followup_original', to=settings.AUTH_USER_MODEL)),
                ('owner_sale', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='followup_owner', to=settings.AUTH_USER_MODEL)),
                ('source_register', models.OneToOneField(db_constraint=False, on_delete=django.db.models.deletion.CASCADE, related_name='followup', to='app.register_main')),
            ],
            options={'ordering': ('due_date',)},
        ),
        migrations.CreateModel(
            name='customer_followup_log',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('contact_name', models.CharField(max_length=256)),
                ('contact_phone', models.CharField(max_length=64)),
                ('channel', models.CharField(choices=[('phone', 'โทรศัพท์'), ('line', 'Line'), ('email', 'อีเมล'), ('visit', 'เข้าพบ'), ('other', 'อื่น ๆ')], max_length=16)),
                ('result', models.CharField(max_length=256)),
                ('note', models.TextField(blank=True, default='')),
                ('counted', models.BooleanField(default=True)),
                ('crt_date', models.DateTimeField(auto_now_add=True)),
                ('followup', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='logs', to='app.customer_followup')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ('-crt_date',)},
        ),
        migrations.CreateModel(
            name='customer_followup_owner_log',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reason', models.CharField(choices=[('auto_pool', 'หมดสิทธิ์ ย้ายไปลูกค้าตกค้าง'), ('claim', 'รับเรื่องจากลูกค้าตกค้าง'), ('claim_expired', 'หมดเวลารับเรื่อง'), ('sale_desk', 'Sale Desk บันทึกผู้ขาย')], max_length=16)),
                ('crt_date', models.DateTimeField(auto_now_add=True)),
                ('followup', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='owner_logs', to='app.customer_followup')),
                ('from_user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='followup_owner_from', to=settings.AUTH_USER_MODEL)),
                ('to_user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='followup_owner_to', to=settings.AUTH_USER_MODEL)),
                ('user_crt', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='followup_owner_crt', to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ('-crt_date',)},
        ),
        migrations.RunPython(add_followup_menu, remove_followup_menu),
    ]
