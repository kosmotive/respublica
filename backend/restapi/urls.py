from django.urls import include, path
from rest_framework import routers

from restapi import views

router = routers.DefaultRouter()

router.register(r'users', views.UserViewSet)

router.register(r'worlds'    , views.WorldViewSet)
router.register(r'movables'  , views.MovableViewSet)
router.register(r'sectors'   , views.SectorViewSet)
router.register(r'celestials', views.CelestialViewSet)
router.register(r'unveiled'  , views.UnveiledViewSet)

router.register(r'empires'      , views.EmpireViewSet)
router.register(r'blueprints'   , views.BlueprintViewSet)
router.register(r'constructions', views.ConstructionViewSet)
router.register(r'ships'        , views.ShipViewSet)

router.register(r'processes', views.ProcessViewSet)

urlpatterns = [
    path('', include(router.urls)),
]

urlpatterns += router.urls
