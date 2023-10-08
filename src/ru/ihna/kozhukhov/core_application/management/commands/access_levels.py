from ...entity.entity_sets.access_level_set import AccessLevelSet

from django.core.management import BaseCommand


class Command(BaseCommand):
    """
    Prints all access levels in one column (this will facilitate the view development).
    """

    help = "Prints project and application access levels"
    requires_migrations_checks = True

    def handle(self, *args, **kwargs):
        """
        Handles the command

        :param args: command arguments passed by the Django system
        :param kwargs: command keywords passed by the Django system
        :return: nothing
        """
        self.stdout.write("Project access levels")
        print("==================================================")
        level_set = AccessLevelSet()
        for level in level_set:
            self.stdout.write("%d\t%s\t%s" % (level.id, level.alias, level.name))
        self.stdout.write()
