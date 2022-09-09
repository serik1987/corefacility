# Generated by Django 3.2.9 on 2022-09-09 16:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('core', '0002_install'),
    ]

    operations = [
        migrations.CreateModel(
            name='AuthorizationToken',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('access_token', models.CharField(max_length=256)),
                ('expires_in', models.DateTimeField()),
                ('refresh_token', models.CharField(max_length=256)),
                ('authentication', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='mailru_token', to='core.authentication')),
            ],
        ),
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(db_index=True, help_text='The user E-mail when he registered in the Mail.ru system', max_length=254, unique=True)),
                ('user', models.OneToOneField(help_text='corefacility user to which this account is attached', on_delete=django.db.models.deletion.CASCADE, related_name='mailru_account', to='core.user')),
            ],
        ),
    ]
