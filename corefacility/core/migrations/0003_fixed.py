# Generated by Django 3.2.9 on 2022-01-16 03:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_fill'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='accesslevel',
            options={'ordering': ['id']},
        ),
        migrations.AlterModelOptions(
            name='user',
            options={'ordering': ['surname', 'name', 'login']},
        ),
        migrations.RemoveField(
            model_name='group',
            name='users',
        ),
        migrations.AlterField(
            model_name='groupuser',
            name='group',
            field=models.ForeignKey(editable=False, help_text='The group in which the user participates', on_delete=django.db.models.deletion.CASCADE, related_name='users', to='core.group'),
        ),
    ]
