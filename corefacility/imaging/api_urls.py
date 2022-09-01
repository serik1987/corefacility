from rest_framework.routers import DefaultRouter

from imaging.views import MapViewSet

app_name = "imaging"

router = DefaultRouter()
router.register(r'data', MapViewSet, basename="functional-map")

urlpatterns = router.urls
