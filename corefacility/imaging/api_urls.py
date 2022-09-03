from django.urls import path, include
from rest_framework.routers import DefaultRouter

from imaging.views import MapViewSet, ProcessorsListView

app_name = "imaging"

router = DefaultRouter()
router.register(r'data', MapViewSet, basename="functional-map")

urlpatterns = [
    path(r'processors/<str:map_lookup>/', ProcessorsListView.as_view(), name="module-list-processors")
              ] + router.urls
