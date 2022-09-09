
from django.urls import path, include

urlpatterns = [
    path(r'imaging/', include('imaging.api_urls'))
]
