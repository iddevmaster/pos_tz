from django.db import migrations


def move_certificate_permission(apps, schema_editor):
    CategoryProgramPermission = apps.get_model(
        'app', 'category_program_permission'
    )
    CategoryProgramPermission.objects.filter(
        page_route='certificate/setting'
    ).update(
        group_value='settings',
        group_label='ตั้งค่า',
        page_label='ตั้งค่าใบเซอร์',
    )


def move_certificate_permission_back(apps, schema_editor):
    CategoryProgramPermission = apps.get_model(
        'app', 'category_program_permission'
    )
    CategoryProgramPermission.objects.filter(
        page_route='certificate/setting'
    ).update(
        group_value='pRem5',
        group_label='หลักสูตร',
    )


class Migration(migrations.Migration):
    dependencies = [
        ('app', '0003_certificate_setting'),
    ]

    operations = [
        migrations.RunPython(
            move_certificate_permission,
            move_certificate_permission_back,
        ),
    ]
