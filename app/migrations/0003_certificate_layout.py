from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('app', '0002_billing_cycle_setting_category_program_pay_item_and_more')]
    operations = [migrations.CreateModel(
        name='CertificateLayout',
        fields=[
            ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ('language', models.CharField(choices=[('th', 'ไทย'), ('eng', 'English')], max_length=3, unique=True)),
            ('layout', models.JSONField(blank=True, default=dict)),
            ('updated_at', models.DateTimeField(auto_now=True)),
        ],
        options={'verbose_name': 'แม่แบบใบประกาศ', 'verbose_name_plural': 'แม่แบบใบประกาศ'},
    )]
