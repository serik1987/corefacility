# Generated by Django 4.2.5 on 2023-10-06 11:09

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AccessLevel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('alias', models.SlugField(editable=False)),
                ('name', models.CharField(editable=False, max_length=64)),
            ],
        ),
        migrations.CreateModel(
            name='EntryPoint',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('alias', models.SlugField()),
                ('name', models.CharField(editable=False, max_length=128)),
                ('type', models.CharField(choices=[('lst', 'As list (the user can enable arbitrary amount of modules in this entry point)'), ('sel', 'As select (the user must choice which module in this entry point to enable)')], default='lst', editable=False, max_length=3)),
                ('entry_point_class', models.CharField(editable=False, max_length=1024)),
            ],
        ),
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=256, unique=True)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='HealthCheck',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(db_index=True)),
                ('cpu_load', models.JSONField()),
                ('ram_free', models.PositiveBigIntegerField()),
                ('swap_free', models.PositiveBigIntegerField()),
                ('hdd_free', models.JSONField()),
                ('bytes_sent', models.PositiveBigIntegerField()),
                ('bytes_received', models.PositiveBigIntegerField()),
                ('temperature', models.JSONField()),
            ],
        ),
        migrations.CreateModel(
            name='Log',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('request_date', models.DateTimeField(db_index=True, editable=False)),
                ('log_address', models.CharField(editable=False, max_length=4096)),
                ('request_method', models.CharField(editable=False, max_length=7)),
                ('operation_description', models.CharField(editable=False, max_length=4096, null=True)),
                ('request_body', models.TextField(editable=False, null=True)),
                ('input_data', models.TextField(editable=False, null=True)),
                ('ip_address', models.GenericIPAddressField(editable=False, null=True)),
                ('geolocation', models.CharField(editable=False, max_length=256, null=True)),
                ('response_status', models.IntegerField(editable=False, null=True)),
                ('response_body', models.TextField(editable=False, help_text='defines the response body', null=True)),
                ('output_data', models.TextField(editable=False, null=True)),
            ],
            options={
                'ordering': ['-request_date'],
            },
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('login', models.SlugField(max_length=100, unique=True)),
                ('password_hash', models.CharField(max_length=256, null=True)),
                ('name', models.CharField(db_index=True, max_length=100, null=True)),
                ('surname', models.CharField(db_index=True, max_length=100, null=True)),
                ('email', models.EmailField(max_length=254, null=True, unique=True)),
                ('phone', models.CharField(max_length=20, null=True)),
                ('is_locked', models.BooleanField(default=False)),
                ('is_superuser', models.BooleanField(default=False)),
                ('is_support', models.BooleanField(default=False)),
                ('avatar', models.ImageField(null=True, upload_to='')),
                ('unix_group', models.CharField(editable=False, max_length=32, null=True, unique=True)),
                ('home_dir', models.CharField(editable=False, max_length=100, null=True, unique=True)),
                ('activation_code_hash', models.CharField(editable=False, max_length=256, null=True)),
                ('activation_code_expiry_date', models.DateTimeField(editable=False, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('alias', models.SlugField(max_length=64, unique=True)),
                ('avatar', models.ImageField(null=True, upload_to='')),
                ('name', models.CharField(db_index=True, max_length=64, unique=True)),
                ('description', models.TextField(null=True)),
                ('project_dir', models.CharField(editable=False, max_length=100, null=True, unique=True)),
                ('unix_group', models.CharField(editable=False, max_length=11, null=True, unique=True)),
                ('root_group', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='core_application.group')),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='PosixRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('initialization_date', models.DateTimeField(db_index=True, editable=False)),
                ('action_class', models.CharField(editable=False, max_length=1024)),
                ('action_arguments', models.JSONField(editable=False)),
                ('method_name', models.CharField(editable=False, max_length=1024)),
                ('method_arguments', models.JSONField(editable=False)),
                ('status', models.CharField(choices=[('I', 'Initialized'), ('A', 'Analyzed'), ('C', 'Confirmed')], default='I', max_length=1)),
                ('log', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core_application.log')),
            ],
        ),
        migrations.CreateModel(
            name='Module',
            fields=[
                ('uuid', models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('alias', models.SlugField(editable=False)),
                ('name', models.CharField(editable=False, max_length=128)),
                ('html_code', models.TextField(editable=False, null=True)),
                ('app_class', models.CharField(editable=False, max_length=1024)),
                ('user_settings', models.JSONField()),
                ('is_application', models.BooleanField(default=True, editable=False)),
                ('is_enabled', models.BooleanField(default=True)),
                ('parent_entry_point', models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.RESTRICT, related_name='modules', to='core_application.entrypoint')),
            ],
            options={
                'unique_together': {('alias', 'parent_entry_point')},
            },
        ),
        migrations.CreateModel(
            name='LogRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('record_time', models.DateTimeField(db_index=True, editable=False)),
                ('level', models.CharField(choices=[('DBG', 'Debugging message'), ('INF', 'Information message'), ('WRN', 'The system warning'), ('ERR', 'The system error'), ('CRI', 'The system was down')], db_index=True, default='DBG', editable=False, max_length=3)),
                ('message', models.CharField(editable=False, max_length=1024)),
                ('log', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='records', to='core_application.log')),
            ],
            options={
                'ordering': ['record_time'],
            },
        ),
        migrations.AddField(
            model_name='log',
            name='user',
            field=models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core_application.user'),
        ),
        migrations.CreateModel(
            name='FailedAuthorizations',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('auth_time', models.DateTimeField(db_index=True, editable=False, help_text='Authorization time')),
                ('ip', models.GenericIPAddressField(editable=False, help_text='The IP address defined')),
                ('user', models.ForeignKey(editable=False, help_text='The user that is trying to be authorized', null=True, on_delete=django.db.models.deletion.SET_NULL, to='core_application.user')),
            ],
        ),
        migrations.AddField(
            model_name='entrypoint',
            name='belonging_module',
            field=models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='entry_points', to='core_application.module'),
        ),
        migrations.CreateModel(
            name='Authentication',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('expiration_date', models.DateTimeField()),
                ('token_hash', models.CharField(editable=False, max_length=256)),
                ('user', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, to='core_application.user')),
            ],
        ),
        migrations.CreateModel(
            name='Permission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('access_level', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core_application.accesslevel')),
                ('group', models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='permissions', to='core_application.group')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='permissions', to='core_application.project')),
            ],
            options={
                'unique_together': {('group', 'project')},
            },
        ),
        migrations.CreateModel(
            name='GroupUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_governor', models.BooleanField(default=False, help_text='True for the group governor, False for the others')),
                ('group', models.ForeignKey(editable=False, help_text='The group in which the user participates', on_delete=django.db.models.deletion.CASCADE, related_name='users', to='core_application.group')),
                ('user', models.ForeignKey(editable=False, help_text='The user which is mentioned', on_delete=django.db.models.deletion.CASCADE, related_name='groups', to='core_application.user')),
            ],
            options={
                'unique_together': {('group', 'user')},
            },
        ),
        migrations.AlterUniqueTogether(
            name='entrypoint',
            unique_together={('alias', 'belonging_module')},
        ),
    ]