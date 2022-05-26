from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import View404, UserViewSet, GroupViewSet, LoginView, ProfileView
from .views.profile_avatar import ProfileAvatarView

router = DefaultRouter()
router.register(r'users', UserViewSet, basename="users")
router.register(r'groups', GroupViewSet, basename="groups")

urlpatterns = [
    path(r'login/', LoginView.as_view(), name="login"),
    path(r'profile/', ProfileView.as_view(), name="profile"),
    path(r'profile/avatar/', ProfileAvatarView.as_view(), name="profile-avatar"),
              ] + router.urls + [
    path(r'<path:path>/', View404.as_view(), name="view404"),
]
