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
                ('access_token', models.CharField(editable=False, help_text='The authorization token that provides an access of the application to all Google facilities', max_length=256)),
                ('expires_in', models.DateTimeField(editable=False, help_text='Date and time when authorization token expires')),
                ('refresh_token', models.CharField(editable=False, help_text='This token will be used when authorization token expires', max_length=256)),
                ('authentication', models.OneToOneField(help_text='Link to the authentication details', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='google_token', to='core.authentication')),
            ],
        ),
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(db_index=True, help_text='The user e-mail address in the Google', max_length=254)),
                ('user', models.OneToOneField(help_text='User to which this Google account is attached', on_delete=django.db.models.deletion.CASCADE, to='core.user')),
            ],
        ),
    ]
