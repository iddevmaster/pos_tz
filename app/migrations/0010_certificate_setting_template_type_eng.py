from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0009_customer_entity'),
    ]

    operations = [
        migrations.AddField(
            model_name='certificate_setting',
            name='template_type_eng',
            field=models.PositiveSmallIntegerField(default=1),
        ),
    ]
