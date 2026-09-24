from django.db import migrations, models


def create_default_certificate_setting(apps, schema_editor):
    CertificateSetting = apps.get_model('app', 'certificate_setting')
    CertificateSetting.objects.get_or_create(
        certificate_setting_id=1,
        defaults={'template_type': 1},
    )


class Migration(migrations.Migration):
    dependencies = [
        ('app', '0002_billing_cycle_setting_category_program_pay_item_and_more'),
    ]
    operations = [
        migrations.CreateModel(
            name='certificate_setting',
            fields=[
                ('certificate_setting_id', models.AutoField(primary_key=True, serialize=False)),
                ('template_type', models.PositiveSmallIntegerField(default=1)),
            ],
        ),
        migrations.RunPython(create_default_certificate_setting, migrations.RunPython.noop),
    ]
