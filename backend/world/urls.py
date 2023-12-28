from django.urls import include, path
from rest_framework import routers

from world import views

router = routers.DefaultRouter()
router.register(r'worlds'  , views.WorldViewSet)
router.register(r'movables', views.MovableViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]

urlpatterns += router.urls
