import uuid
from django.db import models


class Module(models.Model):
    """
    Defines the information related to the application module that is stored to the
    database, not as a Django application
    """
    uuid = models.UUIDField(db_index=True, editable=False, primary_key=True, default=uuid.uuid4)
    parent_entry_point = models.ForeignKey("EntryPoint", null=True, on_delete=models.RESTRICT,
                                           related_name="modules", editable=False)
    alias = models.SlugField(editable=False, db_index=True)
    name = models.CharField(max_length=128, editable=False)
    html_code = models.TextField(null=True, editable=False)
    app_class = models.CharField(max_length=1024, editable=False)
    user_settings = models.JSONField()
    is_application = models.BooleanField(default=True, editable=False)
    is_enabled = models.BooleanField(default=True)

    class Meta:
        unique_together = ["alias", "parent_entry_point"]
