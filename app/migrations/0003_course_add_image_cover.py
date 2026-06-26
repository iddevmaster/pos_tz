from django.db import migrations, models
import app.functions


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_billing_cycle_setting_category_program_pay_item_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='image_cover',
            field=models.ImageField(
                blank=True,
                default=None,
                null=True,
                upload_to=app.functions.generate_unique_name('images/course'),
            ),
        ),
    ]
