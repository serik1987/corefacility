from django.db import migrations, transaction
from django.contrib.auth.hashers import make_password
from django.utils.translation import gettext as _
from core.models.enums import LevelType, EntryPointType


def run_migration_routines(apps, schema_editor):
    """
    Adds the user 'support

    :param apps: the applications registry supplied by the migration system
    :param schema_editor: the default schema editor to use
    :return: nothing
    """
    with transaction.atomic(schema_editor.connection.alias):
        User = apps.get_model("core", "User")
        AccessLevel = apps.get_model("core", "AccessLevel")
        Module = apps.get_model("core", "Module")
        EntryPoint = apps.get_model("core", "EntryPoint")
        Migration.add_support_user(User)
        Migration.set_project_access_levels(AccessLevel)
        Migration.set_application_access_levels(AccessLevel)
        Migration.create_default_app_tree(Module, EntryPoint)


class Migration(migrations.Migration):
    """
    Since all SQL tables were created during the first migration,
    this migration will fill the table by appropriate values
    """

    @staticmethod
    def add_support_user(User):
        """
        Adds support user to the database

        :param User: the User model class
        :return: nothing
        """
        support = User(
            login="support",
            password_hash=make_password("support"),
            is_locked=False,
            is_superuser=True,
            is_support=True
        )
        support.save()

    @staticmethod
    def set_project_access_levels(AccessLevel):
        """
        Adds all project access levels

        :param AccessLevel: the AccessLevel model class
        :return: nothing
        """
        project_permission = LevelType.project_level.value
        AccessLevel.objects.bulk_create([
            AccessLevel(type=project_permission, alias="full", name=_("Full access")),
            AccessLevel(type=project_permission, alias="data_full", name=_("Dealing with data")),
            AccessLevel(type=project_permission, alias="data_add", name=_("Data adding and processing only")),
            AccessLevel(type=project_permission, alias="data_process", name=_("Data processing only")),
            AccessLevel(type=project_permission, alias="data_view", name=_("Viewing the data")),
            AccessLevel(type=project_permission, alias="no_access", name=_("No access")),
        ])

    @staticmethod
    def set_application_access_levels(AccessLevel):
        """
        Sets the access levels for applications

        :param AccessLevel: the AccessLevel model class
        :return: nothing
        """
        app_permission = LevelType.app_level.value
        AccessLevel.objects.bulk_create([
            AccessLevel(type=app_permission, alias="add", name=_("Add application")),
            AccessLevel(type=app_permission, alias="permission_required",
                        name=_("Add application (superuser permission required)")),
            AccessLevel(type=app_permission, alias="usage",
                        name=_("Application usage")),
            AccessLevel(type=app_permission, alias="no_access",
                        name=_("No access"))
        ])

    @staticmethod
    def create_default_app_tree(Module, EntryPoint):
        """
        Creates the default application tree

        :param Module: the Module model object
        :param EntryPoint: the EntryPoint model object
        :return: nothing
        """
        core_application = Module(parent_entry_point=None, alias="core", name=_("Basic facility"), html_code=None,
                                  app_class="core.App", user_settings=dict(), is_application=False, is_enabled=True)
        core_application.save()

        authorizations = EntryPoint(alias="authorizations", belonging_module=core_application,
                                    name=_("Authorization modules"), type=EntryPointType.list.value)
        authorizations.save()
        Module(parent_entry_point=authorizations, alias="standard", name=_("Standard authorization"), html_code=None,
               app_class="core.authorizations.StandardAuthorization", is_application=False, is_enabled=True,
               user_settings=dict()).save()
        Module(parent_entry_point=authorizations, alias="ihna", name=_("Authorization through IHNA website"),
               html_code="<div class='auth ihna'></div>", app_class="authorizations.ihna.App", user_settings=dict(),
               is_application=False, is_enabled=False).save()
        Module(parent_entry_point=authorizations, alias="google", name=_("Authorization though Google"),
               html_code="<div class='auth google'></div>", app_class="authorizations.google.App", user_settings=dict(),
               is_application=False, is_enabled=False).save()
        Module(parent_entry_point=authorizations, alias="mailru", name=_("Authorization through Mail.ru"),
               html_code="<div class='auth mailru'></div>", app_class="authorizations.mailru.App", user_settings=dict(),
               is_application=False, is_enabled=False).save()
        Module(parent_entry_point=authorizations, alias="unix", name=_("Authorization through UNIX account"),
               html_code=None, app_class="core.authorizations.UnixAuthorization", user_settings=dict(),
               is_application=False, is_enabled=False).save()
        Module(parent_entry_point=authorizations, alias="cookie", name=_("Authorization through Cookie"),
               html_code=None, app_class="authorizations.cookie.App", user_settings=dict(),
               is_application=False, is_enabled=False).save()
        Module(parent_entry_point=authorizations, alias="password_recovery", name=_("Password recovery function"),
               html_code=None, app_class="core.authorizations.PasswordRecoveryAuthorization", user_settings=dict(),
               is_application=False, is_enabled=False).save()
        Module(parent_entry_point=authorizations, alias="auto", name=_("Automatic authorization"),
               html_code=None, app_class="core.authorizations.AutomaticAuthorization", user_settings=dict(),
               is_application=False, is_enabled=False).save()

        synchronizations = EntryPoint(alias="synchronizations", belonging_module=core_application,
                                      name=_("Synchronization modules"), type=EntryPointType.select.value)
        synchronizations.save()
        Module(parent_entry_point=synchronizations, alias="ihna_employees",
               name=_("Synchronization with the IHNA website"), html_code=None,
               app_class="core.synchronizations.IhnaSynchronization", user_settings=dict(), is_application=False,
               is_enabled=False).save()

        projects = EntryPoint(alias="projects", belonging_module=core_application, name=_("Project applications"),
                              type=EntryPointType.list.value)
        projects.save()
        imaging = Module(parent_entry_point=projects, alias="imaging",
                         name=_("Basic functional maps processing"), html_code=None, app_class="imaging.App",
                         user_settings=dict(), is_application=False, is_enabled=False)
        imaging.save()

        image_processors = EntryPoint(alias="processors", belonging_module=imaging,
                                      name=_("Imaging processors"), type=EntryPointType.list.value)
        image_processors.save()
        Module(parent_entry_point=image_processors, alias="roi", name=_("ROI definition"), html_code=None,
               app_class="roi.App", user_settings=dict(), is_application=False, is_enabled=False).save()

    dependencies = [
        ("core", "0001_initial")
    ]

    operations = [
        migrations.RunPython(run_migration_routines)
    ]
