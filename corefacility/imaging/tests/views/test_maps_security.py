from core.test.views import BaseProjectDataSecurityTest


class TestMapsSecurity(BaseProjectDataSecurityTest):
    """
    Provides security tests for functional maps
    """

    def test_sample(self):
        """
        Let's create some map
        :return:
        """
        print(self.access_levels)
        print(self.user_list)
        print(self.superuser_token, self.full_token, self.data_full_token)
        print(self.project)
        for group, access_level in self.project.permissions:
            print(group.name if group is not None else "", access_level.name)


del BaseProjectDataSecurityTest
