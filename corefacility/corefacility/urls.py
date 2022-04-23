import os

from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from core.testviews.config import config
from core.testviews.test_ui import test_ui
from core.testviews.test_api import test_api, test_logger
from core.testviews.test_concurrent import test_concurrent

urlpatterns = [
    path('__config__/', config, name="config"),
    path('__test__/ui/<int:n>/', test_ui, name="test_ui"),
    path('__test__/api/<int:n>/', test_api, name="test_api"),
    path('__test__/concurrent/', test_concurrent, name="test_concurrent"),
    path('__test__/logger/', test_logger, name="test_logger"),
]

urlpatterns += static("/favicon.ico", document_root=os.path.join(settings.BASE_DIR, "corefacility/static/favicon.ico"))
