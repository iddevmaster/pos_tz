from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('app', '0010_certificate_setting_template_type_eng')]

    operations = [
        migrations.AddField(
            model_name='internalmemo',
            name='require_review',
            field=models.BooleanField(default=True),
        ),
    ]
