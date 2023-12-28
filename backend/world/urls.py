from django.urls import include, path
from rest_framework import routers

from world import views

router = routers.DefaultRouter()
router.register(r'worlds'    , views.WorldViewSet)
router.register(r'movables'  , views.MovableViewSet)
router.register(r'sectors'   , views.SectorViewSet)
router.register(r'celestials', views.CelestialViewSet)

urlpatterns = [
    path('', include(router.urls)),
]

urlpatterns += router.urls
