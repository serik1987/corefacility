from django.urls import path, include
from rest_framework.routers import DefaultRouter

from imaging.views import MapViewSet, ProcessorsListView

app_name = "imaging"

router = DefaultRouter()
router.register(r'data', MapViewSet, basename="functional-map")

urlpatterns = [
    path(r'processors/<str:map_lookup>/', ProcessorsListView.as_view(), name="module-list-processors"),
    path(r'processors/<str:map_lookup>/', include(("imaging.entity.ep_urls.processors", "processors"))),
              ] + router.urls
