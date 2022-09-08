from django.db import migrations, transaction
from django.utils.translation import gettext as _


def run_migration_routines(apps, schema_editor):
    """
    Adds the user 'support'

    :param apps: the applications registry supplied by the migration system
    :param schema_editor: the default schema editor to use
    :return: nothing
    """
    with transaction.atomic(schema_editor.connection.alias):
        from .. import App
        App().install()


class Migration(migrations.Migration):
    """
    Since all SQL tables were created during the first migration,
    this migration will fill the table by appropriate values
    """

    APP_NAME = _("Core functionality")

    dependencies = [
        ("core", "0001_initial")
    ]

    operations = [
        migrations.RunPython(run_migration_routines)
    ]
