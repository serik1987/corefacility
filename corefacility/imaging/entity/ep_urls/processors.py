from django.urls import path, include


urlpatterns = [
    path(r'roi/', include("roi.api_urls"))
]
