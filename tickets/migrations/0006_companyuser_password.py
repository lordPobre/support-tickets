from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0005_companyuser_is_manager'),
    ]

    operations = [
        migrations.AddField(
            model_name='companyuser',
            name='password',
            field=models.CharField(
                blank=True, max_length=128,
                verbose_name='Contraseña del portal',
                help_text='Contraseña para acceder al inventario desde el portal'
            ),
        ),
    ]
