import os

from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from ru.ihna.kozhukhov.core_application.views import MainWindow, View404, AuthorizationView

from ru.ihna.kozhukhov.core_application.test.testviews.config import config
from ru.ihna.kozhukhov.core_application.test.testviews.test_ui import test_ui
from ru.ihna.kozhukhov.core_application.test.testviews.test_api import test_api, test_logger
from ru.ihna.kozhukhov.core_application.test.testviews.test_concurrent import test_concurrent

urlpatterns = [
    path('__config__/', config, name="config"),
    path('__test__/ui/<int:n>/', test_ui, name="test_ui"),
    path('__test__/api/<int:n>/', test_api, name="test_api"),
    path('__test__/concurrent/', test_concurrent, name="test_concurrent"),
    path('__test__/logger/', test_logger, name="test_logger"),

    path('api/v<version>/',
         include(("ru.ihna.kozhukhov.core_application.api_urls", "core"))),
    path('api/', View404.as_view(), name="no-api-version"),
    path('authorize/<slug:module_alias>/', AuthorizationView.as_view(), name='auth-view'),
    path('ui/<uuid:uuid>/<path:path>/', MainWindow.as_view(), name="subwindow"),
    path('ui/<uuid:uuid>/', MainWindow.as_view(), name="subwindow"),
    path('', MainWindow.as_view(), {'path': ''}, name="main_window"),
]

urlpatterns += static("/favicon.ico",
                      document_root=os.path.join(settings.BASE_DIR, "corefacility/static/favicon.ico"))
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# The following path must have the lowest priority because corresponding path pattern is suitable for any kind of
# path, i.e., any other path below it is unusable
urlpatterns += [
    path('<path:path>/', MainWindow.as_view(), name="main_window"),
]
