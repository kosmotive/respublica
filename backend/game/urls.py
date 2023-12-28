from django.urls import include, path
from rest_framework import routers

from game import views

router = routers.DefaultRouter()
router.register(r'empires', views.EmpireViewSet)

urlpatterns = [
    path('', include(router.urls)),
]

urlpatterns += router.urls
