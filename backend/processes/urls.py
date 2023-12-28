from django.urls import include, path
from rest_framework import routers

from processes import views

router = routers.DefaultRouter()
router.register(r'processes', views.ProcessViewSet)

urlpatterns = [
    path('', include(router.urls)),
]

urlpatterns += router.urls
