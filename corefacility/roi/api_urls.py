from rest_framework.routers import DefaultRouter

from .views import PinwheelViewSet


router = DefaultRouter()
router.register(r'pinwheels', PinwheelViewSet, basename="pinwheel")
urlpatterns = router.urls
