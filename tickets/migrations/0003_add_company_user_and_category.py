import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0001_initial'),
    ]

    operations = [
        # Replaces the deleted 0002: ImageField -> FileField
        migrations.AlterField(
            model_name='company',
            name='logo',
            field=models.FileField(blank=True, null=True, upload_to='companies/logos/'),
        ),
        migrations.AddField(
            model_name='ticket',
            name='category',
            field=models.CharField(
                choices=[('software', 'Software'), ('hardware', 'Hardware'), ('email', 'Email / Correo')],
                default='software', max_length=20, verbose_name='Categoría de soporte'
            ),
        ),
        migrations.CreateModel(
            name='CompanyUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='Nombre completo')),
                ('email', models.EmailField(max_length=254, verbose_name='Email')),
                ('position', models.CharField(blank=True, max_length=100, verbose_name='Cargo')),
                ('is_active', models.BooleanField(default=True, verbose_name='Activo')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('company', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='users', to='tickets.company', verbose_name='Empresa'
                )),
            ],
            options={
                'verbose_name': 'Usuario de empresa',
                'verbose_name_plural': 'Usuarios de empresa',
                'ordering': ['company', 'name'],
                'unique_together': {('company', 'email')},
            },
        ),
        migrations.AddField(
            model_name='ticket',
            name='company_user',
            field=models.ForeignKey(
                blank=True, null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='tickets', to='tickets.companyuser',
                verbose_name='Usuario solicitante'
            ),
        ),
    ]
