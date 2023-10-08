from rest_framework.views import APIView

from ..generic_views import AvatarMixin, EntityViewMixin
from ..entity.entity_sets.user_set import UserSet
from ..serializers import UserDetailSerializer
from ..permissions import NoSupportPermission


class ProfileAvatarView(AvatarMixin, EntityViewMixin, APIView):
    """
    Uploading or deleting the profile avatar
    """

    entity_set_class = UserSet
    detail_serializer_class = UserDetailSerializer
    permission_classes = [NoSupportPermission]

    def patch(self, request, *args, **kwargs):
        """
        Uploads the profile avatar

        :param request: the avatar uploading request
        :param args: function arguments
        :param kwargs: function keyword arguments
        :return: nothing
        """
        return self.upload_file(request)

    def delete(self, request, *args, **kwargs):
        """
        Deletes the profile avatar

        :param request: the avatar uploading request
        :param args: function arguments
        :param kwargs: function keyword arguments
        :return: nothing
        """
        return self.delete_file(request)

    def get_object(self):
        """
        Returns the object the view is displaying.

        You may want to override this if you need to provide non-standard
        queryset lookups.  Eg if objects are referenced using multiple
        keyword arguments in the url conf.
        """
        return self.request.user
