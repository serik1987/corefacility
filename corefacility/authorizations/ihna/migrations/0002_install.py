from django.db import transaction, migrations
from django.utils.translation import gettext_lazy as _


def run_migration_routines(apps, schema_editor):
    with transaction.atomic(schema_editor.connection.alias):
        from .. import App
        App().install()


class Migration(migrations.Migration):

    APP_NAME = _("Authorization through IHNA website")

    dependencies = [
        ("ihna", "0001_initial"),
        ("core", "0002_install"),
    ]

    operations = [
        migrations.RunPython(run_migration_routines)
    ]
