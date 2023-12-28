from django.urls import include, path
from rest_framework import routers

from game import views

router = routers.DefaultRouter()
router.register(r'empires'      , views.EmpireViewSet)
router.register(r'blueprints'   , views.BlueprintViewSet)
router.register(r'constructions', views.ConstructionViewSet)
router.register(r'ships'        , views.ShipViewSet)

urlpatterns = [
    path('', include(router.urls)),
]

urlpatterns += router.urls
