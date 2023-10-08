from django.db import transaction, migrations
from django.utils.translation import gettext_lazy as _


def run_migration_routines(apps, schema_editor):
    with transaction.atomic(schema_editor.connection.alias):
        from .. import App
        App().install()


class Migration(migrations.Migration):

    APP_NAME = _("{{app_name}}")

    dependencies = [
        ("{{app_module}}", "0001_initial"),
        ("{{parent_app_module}}", "0002_install"),
    ]

    operations = [
        migrations.RunPython(run_migration_routines)
    ]
