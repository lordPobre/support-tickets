import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0003_add_company_user_and_category'),
    ]

    operations = [
        migrations.CreateModel(
            name='Equipment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('device_type', models.CharField(
                    choices=[('desktop','Desktop / PC'),('laptop','Notebook / Laptop'),('server','Servidor'),
                             ('printer','Impresora'),('monitor','Monitor'),('switch','Switch / Router'),('other','Otro')],
                    default='desktop', max_length=20, verbose_name='Tipo de equipo')),
                ('brand', models.CharField(max_length=100, verbose_name='Marca')),
                ('model', models.CharField(max_length=100, verbose_name='Modelo')),
                ('serial_number', models.CharField(max_length=200, unique=True, verbose_name='Número de serie')),
                ('year', models.PositiveIntegerField(verbose_name='Año de adquisición')),
                ('status', models.CharField(
                    choices=[('active','Activo'),('maintenance','En mantención'),
                             ('retired','Dado de baja'),('storage','En bodega')],
                    default='active', max_length=20, verbose_name='Estado')),
                ('specs', models.TextField(blank=True, verbose_name='Especificaciones',
                    help_text='CPU, RAM, disco, etc.')),
                ('notes', models.TextField(blank=True, verbose_name='Notas adicionales')),
                ('image', models.FileField(blank=True, null=True, upload_to='equipment/images/', verbose_name='Imagen')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('company', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='equipment', to='tickets.company', verbose_name='Empresa')),
                ('assigned_to', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='equipment', to='tickets.companyuser', verbose_name='Asignado a')),
            ],
            options={
                'verbose_name': 'Equipo',
                'verbose_name_plural': 'Equipos',
                'ordering': ['company', 'device_type', 'brand'],
            },
        ),
    ]
