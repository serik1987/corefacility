from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .testviews.test_transaction import TestTransaction
from .views import View404, UserViewSet, GroupViewSet, ProjectViewSet, LoginView, ProfileView, AccessLevelView, \
    ProjectPermissionViewSet, SynchronizationView, LogViewSet, LogRecordViewSet, WidgetsView, ProjectModulesListView, \
    ProjectApplicationViewSet, ModuleSettingsViewSet
from .views.profile_avatar import ProfileAvatarView

router = DefaultRouter()
router.register(r'users', UserViewSet, basename="users")
router.register(r'groups', GroupViewSet, basename="groups")
router.register(r'projects', ProjectViewSet, basename="projects")
router.register(r'projects/(?P<project_lookup>\w+)/permissions', ProjectPermissionViewSet,
                basename="project-permissions")
router.register(r'projects/(?P<project_lookup>\w+)/apps', ProjectApplicationViewSet, basename="project-applications")
router.register(r'settings', ModuleSettingsViewSet, basename='settings')
router.register(r'logs', LogViewSet, basename="logs")
router.register(r'logs/(?P<log_id>\d+)/records', LogRecordViewSet, basename="log-records")

urlpatterns = [
    path(r'__test__/transaction/<str:dirname>/', TestTransaction.as_view(), name="test-transaction"),

    path(r'core/projects/<str:project_lookup>/', ProjectModulesListView.as_view(), name="module-list-projects"),
    path(r'core/projects/<str:project_lookup>/', include(("core.entity.ep_urls.projects", "projects"))),

    path(r'login/', LoginView.as_view(), name="login"),
    path(r'profile/', ProfileView.as_view(), name="profile"),
    path(r'profile/avatar/', ProfileAvatarView.as_view(), name="profile-avatar"),
    path(r'access-levels/', AccessLevelView.as_view(), name="access-level"),
    path(r'account-synchronization/', SynchronizationView.as_view(), name="account-synchronization"),
    path(r'widgets/<uuid:module_uuid>/<str:entry_point_alias>/', WidgetsView.as_view(), name="widgets"),

              ] + router.urls + [

    path(r'<path:path>/', View404.as_view(), name="view404"),
]
