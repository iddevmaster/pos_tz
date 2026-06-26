from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0004_customers_remove_register_and_location_fk'),
    ]

    operations = [
        migrations.AddField(
            model_name='customers',
            name='customer_type',
            field=models.IntegerField(blank=True, default=1),
        ),
    ]
