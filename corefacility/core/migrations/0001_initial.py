# Generated by Django 3.2.9 on 2021-12-05 17:15
# DO NOT EDIT THIS FILE!

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
                ('type', models.CharField(choices=[('prj', 'Project access level'), ('app', 'Application access level')], default='app', editable=False, help_text='Defines whether this is an application access level or text access level', max_length=3)),
                ('alias', models.SlugField(editable=False, help_text='short name of the access level to use in the API')),
                ('name', models.CharField(editable=False, help_text='Long name of the access level to use in the UI', max_length=64)),
            ],
            options={
                'unique_together': {('type', 'alias'), ('type', 'name')},
            },
        ),
        migrations.CreateModel(
            name='EntryPoint',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('alias', models.SlugField(help_text='A short name that can be used to identify the entry point in the app')),
                ('name', models.CharField(editable=False, help_text='The name through which the entry point is visible on the system', max_length=128)),
                ('type', models.CharField(choices=[('lst', 'As list (the user can enable arbitrary amount of modules in this entry point)'), ('sel', 'as choice (the user myst choice which module in this entry point to enable)')], default='lst', editable=False, help_text='Whether the entry point looks like list or select?', max_length=3)),
            ],
        ),
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, help_text='The name of the user group to print', max_length=256, unique=True)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Log',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('request_date', models.DateTimeField(db_index=True, editable=False, help_text='Date and time when the request has been received')),
                ('log_address', models.CharField(editable=False, help_text='Defines a full route to the request', max_length=4096)),
                ('request_method', models.CharField(editable=False, help_text='The request method', max_length=5)),
                ('operation_description', models.CharField(editable=False, help_text='The operation description', max_length=4096, null=True)),
                ('request_body', models.TextField(editable=False, help_text='The request body when it represented in text format', null=True)),
                ('input_data', models.TextField(editable=False, help_text='Description of the request input data', null=True)),
                ('ip_address', models.GenericIPAddressField(editable=False, help_text='The IP address defined', null=True)),
                ('geolocation', models.CharField(editable=False, help_text='Geolocation of that IP address', max_length=256, null=True)),
                ('response_status', models.IntegerField(editable=False, help_text='HTTP response status', null=True)),
                ('response_body', models.TextField(editable=False, help_text='defines the response body', null=True)),
                ('output_data', models.TextField(editable=False, help_text='Short description of the output data', null=True)),
            ],
            options={
                'ordering': ['-request_date'],
            },
        ),
        migrations.CreateModel(
            name='Module',
            fields=[
                ('uuid', models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, help_text='The UUID provides a quick access to the application during the routing', primary_key=True, serialize=False)),
                ('alias', models.SlugField(editable=False, help_text='A short name that can be used to identify the module in the app', unique=True)),
                ('name', models.CharField(db_index=True, editable=False, help_text='The name through which the module is visible in the system', max_length=128)),
                ('html_code', models.TextField(editable=False, help_text='When the module is visible on the frontend as widget, this field relatesto the module HTML code to show', null=True)),
                ('app_class', models.CharField(editable=False, help_text='The python class connected to the module', max_length=1024)),
                ('user_settings', models.JSONField(help_text='Settings defined by the user and stored in the JSON format')),
                ('is_application', models.BooleanField(default=True, editable=False, help_text='True if the module is application')),
                ('is_enabled', models.BooleanField(default=True, help_text='True if the module has switched on')),
                ('parent_entry_point', models.ForeignKey(editable=False, help_text='List of all modules connected to this entry point', null=True, on_delete=django.db.models.deletion.RESTRICT, related_name='modules', to='core.entrypoint')),
            ],
            options={
                'unique_together': {('alias', 'parent_entry_point')},
            },
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('alias', models.SlugField(help_text='A short string that is needed to build the project URL', max_length=64, unique=True)),
                ('avatar', models.ImageField(help_text='The project image to be shown on the project list', null=True, upload_to='')),
                ('name', models.CharField(db_index=True, help_text='The project name to display', max_length=64, unique=True)),
                ('description', models.TextField(help_text='Short project description, necessary for sending submissions', null=True)),
                ('project_dir', models.CharField(editable=False, help_text='directory where project files will be located', max_length=100, null=True, unique=True)),
                ('unix_group', models.CharField(editable=False, help_text='unix group related to the project', max_length=11, null=True, unique=True)),
                ('project_apps', models.ManyToManyField(help_text='List of application visible in the particular project', to='core.Module')),
                ('root_group', models.ForeignKey(help_text='The group that created and initialized the project', on_delete=django.db.models.deletion.RESTRICT, to='core.group')),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('login', models.SlugField(help_text='the user login', max_length=100, unique=True)),
                ('password_hash', models.CharField(help_text='The password hash for simple login procedure or None if simple login procedure is not available for this user', max_length=256, null=True)),
                ('name', models.CharField(help_text='User first name', max_length=100, null=True)),
                ('surname', models.CharField(help_text='User last name', max_length=100, null=True)),
                ('email', models.EmailField(help_text='E-mail that will be used for receiving notifications', max_length=254, null=True, unique=True)),
                ('phone', models.CharField(help_text="The user phone for connections via What's App etc.", max_length=20, null=True)),
                ('is_locked', models.BooleanField(help_text='True if the user is unable to login in any way')),
                ('is_superuser', models.BooleanField(help_text='True, if the user has all possible permissions')),
                ('is_support', models.BooleanField(help_text='True oif the user is technical support')),
                ('avatar', models.ImageField(help_text='User photo or another picture', null=True, upload_to='')),
                ('unix_group', models.CharField(editable=False, help_text='The UNIX group belonging to the user', max_length=32, null=True, unique=True)),
                ('home_dir', models.CharField(editable=False, help_text='The home directory belonging to the user', max_length=100, null=True, unique=True)),
                ('activation_code_hash', models.CharField(editable=False, help_text='The activation code hash for password recovery via E-mail or None if activation code has not sent yet', max_length=256, null=True)),
                ('activation_code_expiry_date', models.DateTimeField(editable=False, help_text='The activation code when given is valid until this date', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='LogRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('record_time', models.DateTimeField(auto_now_add=True, db_index=True, help_text='Date and time when this record has been created')),
                ('level', models.CharField(choices=[('DBG', 'Debugging message'), ('INF', 'Information message'), ('WRN', 'The system warning'), ('ERR', 'The system error'), ('CRI', 'The system was down')], db_index=True, default='DBG', editable=False, help_text='The importance of this log message', max_length=3)),
                ('message', models.CharField(editable=False, help_text='The log message itself', max_length=1024)),
                ('log', models.ForeignKey(editable=False, help_text='Log to which this record belongs to', on_delete=django.db.models.deletion.CASCADE, related_name='records', to='core.log')),
            ],
            options={
                'ordering': ['record_time'],
            },
        ),
        migrations.AddField(
            model_name='log',
            name='user',
            field=models.ForeignKey(editable=False, help_text='User that is authorized or null if no user is authorized', null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.user'),
        ),
        migrations.CreateModel(
            name='GroupUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_governor', models.BooleanField(default=False, help_text='True for the group governor, False for the others')),
                ('group', models.ForeignKey(editable=False, help_text='The group in which the user participates', on_delete=django.db.models.deletion.CASCADE, to='core.group')),
                ('user', models.ForeignKey(editable=False, help_text='The user which is mentioned', on_delete=django.db.models.deletion.CASCADE, related_name='groups', to='core.user')),
            ],
            options={
                'unique_together': {('group', 'user')},
            },
        ),
        migrations.AddField(
            model_name='group',
            name='users',
            field=models.ManyToManyField(help_text='Users that has been included to that group', through='core.GroupUser', to='core.User'),
        ),
        migrations.CreateModel(
            name='ExternalAuthorizationSession',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('session_key', models.CharField(editable=False, help_text='The session key is used to prove that external authorization system redirects the same user which actually types loging and password', max_length=11)),
                ('session_key_expiry_date', models.DateTimeField(editable=False, help_text='The session key is valid for approximately 1 hour')),
                ('authorization_module', models.ForeignKey(editable=False, help_text='The authorization module through which the authorization is provided', on_delete=django.db.models.deletion.CASCADE, to='core.module')),
            ],
        ),
        migrations.AddField(
            model_name='entrypoint',
            name='belonging_module',
            field=models.ForeignKey(editable=False, help_text='a module having this entry point', on_delete=django.db.models.deletion.CASCADE, related_name='entry_points', to='core.module'),
        ),
        migrations.CreateModel(
            name='Authentication',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('expiration_date', models.DateTimeField(editable=False, help_text='Date and time until which the token is valid')),
                ('token_hash', models.CharField(editable=False, help_text='Hash code for the authentication token. The authentication token isneeded for authenticating requests', max_length=256)),
                ('user', models.ForeignKey(editable=False, help_text='The authenticated user', on_delete=django.db.models.deletion.CASCADE, to='core.user')),
            ],
        ),
        migrations.CreateModel(
            name='ProjectPermission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('access_level', models.ForeignKey(help_text='A certain access level', on_delete=django.db.models.deletion.CASCADE, to='core.accesslevel')),
                ('group', models.ForeignKey(editable=False, help_text='The user group that also has an access to the project', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='permissions', to='core.group')),
                ('project', models.ForeignKey(help_text='The project to which the user group has an additional access', on_delete=django.db.models.deletion.CASCADE, related_name='permissions', to='core.project')),
            ],
            options={
                'unique_together': {('group', 'project')},
            },
        ),
        migrations.AlterUniqueTogether(
            name='entrypoint',
            unique_together={('alias', 'belonging_module')},
        ),
        migrations.CreateModel(
            name='AppPermission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('access_level', models.ForeignKey(help_text='A certain access level', on_delete=django.db.models.deletion.CASCADE, to='core.accesslevel')),
                ('application', models.ForeignKey(help_text='The application which permissions are described here', on_delete=django.db.models.deletion.CASCADE, related_name='permissions', to='core.module')),
                ('group', models.ForeignKey(editable=False, help_text='The user group that also has an access to the project', null=True, on_delete=django.db.models.deletion.CASCADE, to='core.group')),
            ],
            options={
                'unique_together': {('group', 'application')},
            },
        ),
    ]
