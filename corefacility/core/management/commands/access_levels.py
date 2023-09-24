from core.models.enums import LevelType
from core.entity.entity_sets.access_level_set import AccessLevelSet

from django.core.management import BaseCommand


class Command(BaseCommand):
    """
    Prints all access levels in one column (this will facilitate the view development).
    """

    help = "Prints project and application access levels"
    requires_migrations_checks = True

    LEVEL_TYPES = {
        LevelType.project_level: "Project access levels",
        LevelType.app_level: "Application access levels",
    }

    def handle(self, *args, **kwargs):
        """
        Handles the command

        :param args: command arguments passed by the Django system
        :param kwargs: command keywords passed by the Django system
        :return: nothing
        """
        for level_type in [LevelType.project_level, LevelType.app_level]:
            self.stdout.write(self.LEVEL_TYPES[level_type])
            print("==================================================")
            level_set = AccessLevelSet()
            level_set.type = level_type
            for level in level_set:
                self.stdout.write("%d\t%s\t%s" % (level.id, level.alias, level.name))
            self.stdout.write()
