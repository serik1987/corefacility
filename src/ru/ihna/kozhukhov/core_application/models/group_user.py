from django.db import models


class GroupUser(models.Model):
    """
    A joining class that defines how user participates in different groups
    """
    group = models.ForeignKey("Group", editable=False, on_delete=models.CASCADE, related_name="users",
                              help_text="The group in which the user participates")
    user = models.ForeignKey("User", editable=False, on_delete=models.CASCADE, related_name="groups",
                             help_text="The user which is mentioned")
    is_governor = models.BooleanField(default=False,
                                      help_text="True for the group governor, False for the others")

    def __str__(self):
        # noinspection PyUnresolvedReferences
        info = super().__str__() + " for user ID = %d, group ID = %d" % (self.user_id, self.group_id)
        if self.is_governor:
            info += ". The group leader"
        return info

    class Meta:
        unique_together = ["group", "user"]
