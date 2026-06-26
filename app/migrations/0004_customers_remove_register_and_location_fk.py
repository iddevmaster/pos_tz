from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_course_add_image_cover'),
    ]

    operations = [
        # 1. Drop register_id FK column (Django จัดการ drop constraint ให้อัตโนมัติ)
        migrations.RemoveField(
            model_name='customers',
            name='register',
        ),
        # 2. อัปเดต state ให้รู้ว่า location ไม่ใช่ FK แล้ว
        #    DB: drop เฉพาะ FK constraint แต่ไม่ drop column (ข้อมูลยังอยู่)
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.RemoveField(
                    model_name='customers',
                    name='location',
                ),
                migrations.AddField(
                    model_name='customers',
                    name='location_id',
                    field=models.IntegerField(blank=True, default=0),
                ),
            ],
            database_operations=[
                migrations.RunSQL(
                    sql="""
                        SET @fk = (
                            SELECT CONSTRAINT_NAME
                            FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
                            WHERE TABLE_SCHEMA = DATABASE()
                              AND TABLE_NAME = 'app_customers'
                              AND COLUMN_NAME = 'location_id'
                              AND REFERENCED_TABLE_NAME IS NOT NULL
                            LIMIT 1
                        );
                        SET @sql = IF(
                            @fk IS NOT NULL,
                            CONCAT('ALTER TABLE `app_customers` DROP FOREIGN KEY `', @fk, '`'),
                            'SELECT 1'
                        );
                        PREPARE _stmt FROM @sql;
                        EXECUTE _stmt;
                        DEALLOCATE PREPARE _stmt;
                    """,
                    reverse_sql=migrations.RunSQL.noop,
                ),
            ],
        ),
    ]
