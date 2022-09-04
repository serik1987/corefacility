from rest_framework.routers import DefaultRouter

from .views import PinwheelViewSet, RectangularRoiViewSet


router = DefaultRouter()
router.register(r'pinwheels', PinwheelViewSet, basename="pinwheel")
router.register(r'rectangular', RectangularRoiViewSet, basename="rectangular-roi")
urlpatterns = router.urls
