from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from game.serializers import (
    EmpireSerializer,
    BlueprintSerializer,
    ConstructionSerializer,
    ShipSerializer,
)
from game.models import (
    Empire,
    Blueprint,
    Construction,
    Ship,
)


class EmpireViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = Empire.objects.all()
    serializer_class = EmpireSerializer
    #permission_classes = [permissions.IsAuthenticated]


class BlueprintViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = Blueprint.objects.all()
    serializer_class = BlueprintSerializer
    #permission_classes = [permissions.IsAuthenticated]


class ConstructionViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = Construction.objects.all()
    serializer_class = ConstructionSerializer
    #permission_classes = [permissions.IsAuthenticated]


class ShipViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = Ship.objects.all()
    serializer_class = ShipSerializer
    #permission_classes = [permissions.IsAuthenticated]
