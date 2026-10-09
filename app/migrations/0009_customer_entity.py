from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0008_customer_followup'),
    ]

    operations = [
        migrations.AddField(
            model_name='customers',
            name='customer_entity',
            field=models.IntegerField(blank=True, default=1),
        ),
    ]
