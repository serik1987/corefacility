import uuid
from django.db import models


class Module(models.Model):
    """
    Defines the information related to the application module that is stored to the
    database, not as a Django application
    """
    uuid = models.UUIDField(db_index=True, editable=False, primary_key=True, default=uuid.uuid4,
                            help_text="The UUID provides a quick access to the application during the routing")
    parent_entry_point = models.ForeignKey("EntryPoint", null=True, on_delete=models.RESTRICT,
                                           related_name="modules", editable=False,
                                           help_text="List of all modules connected to this entry point")
    alias = models.SlugField(editable=False,
                             help_text="A short name that can be used to identify the module in the app")
    name = models.CharField(max_length=128, editable=False, db_index=True,
                            help_text="The name through which the module is visible in the system")
    html_code = models.TextField(null=True, editable=False,
                                 help_text="When the module is visible on the frontend as widget, this field relates"
                                           "to the module HTML code to show")
    app_class = models.CharField(max_length=1024, editable=False,
                                 help_text="The python class connected to the module")
    user_settings = models.JSONField(help_text="Settings defined by the user and stored in the JSON format")
    is_application = models.BooleanField(default=True, editable=False,
                                         help_text="True if the module is application")
    is_enabled = models.BooleanField(default=True, help_text="True if the module has switched on")

    class Meta:
        unique_together = ["alias", "parent_entry_point"]
