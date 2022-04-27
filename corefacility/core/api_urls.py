from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import View404, UserViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet, basename="users")

urlpatterns = [

              ] + router.urls + [
    path(r'<path:path>/', View404.as_view(), name="view404"),
]
