from django.urls import path
from rest_framework.routers import DefaultRouter

from ru.ihna.kozhukhov.core_application.views import View404, UserViewSet, GroupViewSet, ProjectViewSet, LoginView, \
    ProfileView, AccessLevelView, \
    PermissionViewSet, SynchronizationView, LogViewSet, LogRecordViewSet, WidgetsView, \
    ModuleSettingsViewSet, EntryPointListView, AuthorizationMethodSetupView, SystemInformationView, \
    OperatingSystemLogs, HealthCheck
from ru.ihna.kozhukhov.core_application.views.labjournal import CategoryView, ExportView
from ru.ihna.kozhukhov.core_application.views import ProfileAvatarView
from ru.ihna.kozhukhov.core_application.views.process_information import ProcessInformation

router = DefaultRouter()
router.register(r'users', UserViewSet, basename="users")
router.register(r'groups', GroupViewSet, basename="groups")
router.register(r'projects', ProjectViewSet, basename="projects")
router.register(r'projects/(?P<project_lookup>[-a-zA-Z0-9_]+)/permissions', PermissionViewSet,
                basename="project-permissions")
router.register(r'settings', ModuleSettingsViewSet, basename='settings')
router.register(r'logs', LogViewSet, basename="logs")
router.register(r'logs/(?P<log_id>\d+)/records', LogRecordViewSet, basename="log-records")

urlpatterns = [
    # General views
    path(r'login/', LoginView.as_view(), name="login"),
    path(r'profile/', ProfileView.as_view(), name="profile"),
    path(r'profile/password-reset/', ProfileView.as_view(action='password_reset'), name="profile-password-reset"),
    path(r'profile/avatar/', ProfileAvatarView.as_view(), name="profile-avatar"),
    path(r'users/<int:user_id>/authorizations/<str:module_alias>/', AuthorizationMethodSetupView.as_view(),
         name='authorization-method-setup'),
    path(r'access-levels/', AccessLevelView.as_view(), name="access-level"),
    path(r'account-synchronization/', SynchronizationView.as_view(), name="account-synchronization"),
    path(r'widgets/<uuid:module_uuid>/<str:entry_point_alias>/', WidgetsView.as_view(), name="widgets"),
    path(r'settings/<uuid:uuid>/entry-points/', EntryPointListView.as_view(), name="entry-points"),
    path(r'sysinfo/', SystemInformationView.as_view(), name='system-information'),
    path(r'procinfo/', ProcessInformation.as_view(), name="process-information"),
    path(r'health-check/<slug:category>/', HealthCheck.as_view(), name="health-check"),
    path(r'os-logs/', OperatingSystemLogs.as_view(), name="os-logs"),

    # Labjournal views
    path(r'projects/<slug:project_lookup>/labjournal/categories/<slug:filename>.<slug:export_format>',
         ExportView.as_view(parent_category_access='root_only'), name='category_export_root'),
    path(r'projects/<slug:project_lookup>/labjournal/categories/<int:category_id>/<slug:filename>.<slug:export_format>',
         ExportView.as_view(parent_category_access='by_id'), name='category_export_by_id'),
    path(r'projects/<slug:project_lookup>/labjournal/categories<path:category_path>/<slug:filename>.<slug:export_format>',
         ExportView.as_view(parent_category_access='by_path'), name='category_export_by_path'),
    path(r'projects/<slug:project_lookup>/labjournal/categories/',
         CategoryView.as_view(parent_category_access='root_only'), name='category_view_root'),
    path(r'projects/<slug:project_lookup>/labjournal/categories/<int:category_id>/',
         CategoryView.as_view(parent_category_access='by_id'), name='category_view_by_id'),
    path(r'projects/<slug:project_lookup>/labjournal/categories<path:category_path>/',
         CategoryView.as_view(parent_category_access='by_path'), name='category_view_by_path'),

    # All router-defined views
              ] + router.urls + [

    # All views that are not within the list relate to view 404
    path(r'<path:path>/', View404.as_view(), name="view404"),
]
