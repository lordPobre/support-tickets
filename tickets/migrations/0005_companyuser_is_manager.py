from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0004_add_equipment'),
    ]

    operations = [
        migrations.AddField(
            model_name='companyuser',
            name='is_manager',
            field=models.BooleanField(
                default=False,
                verbose_name='Es jefatura',
                help_text='Puede acceder al inventario de equipos en el portal'
            ),
        ),
    ]
