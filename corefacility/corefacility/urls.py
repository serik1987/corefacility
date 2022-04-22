import os

from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from core.testviews.config import config
from core.testviews.test_ui import test_ui
from core.testviews.test_api import test_api

urlpatterns = [
    path('__config__/', config, name="config"),
    path('__test__/ui/<int:n>/', test_ui, name="test_ui"),
    path('__test__/api/<int:n>/', test_api, name="test_api"),
]

urlpatterns += static("/favicon.ico", document_root=os.path.join(settings.BASE_DIR, "corefacility/static/favicon.ico"))
