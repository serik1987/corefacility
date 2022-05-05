from core.generic_views import EntityRetrieveUpdateView
from core.serializers import ProfileSerializer
from core.permissions import NoSupportPermission


class ProfileView(EntityRetrieveUpdateView):
    """
    Working with profile information
    """

    detail_serializer_class = ProfileSerializer
    permission_classes = [NoSupportPermission]

    def get_object(self):
        """
        Returns a user which profile is going to be changed.

        :return: a user which profile is going to be changed
        """
        return self.request.user
