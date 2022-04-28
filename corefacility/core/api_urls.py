from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import View404, UserViewSet, LoginView

router = DefaultRouter()
router.register(r'users', UserViewSet, basename="users")

urlpatterns = [

              ] + router.urls + [
    path(r'login/', LoginView.as_view(), name="login"),
    path(r'<path:path>/', View404.as_view(), name="view404"),
]
