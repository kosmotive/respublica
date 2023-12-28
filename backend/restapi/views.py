from urllib.parse import urlparse

from django.urls import resolve
from rest_framework import permissions, viewsets, mixins
from rest_framework.decorators import action
from rest_framework.response import Response

from restapi.serializers import (
    WorldSerializer,
    MovableSerializer,
    SectorSerializer,
    CelestialSerializer,

    EmpireSerializer,
    BlueprintSerializer,
    ConstructionSerializer,
    ShipSerializer,

    ProcessSerializer,
)
from world.models import (
    World,
    Movable,
    Sector,
    Celestial,
)
from game.models import (
    Empire,
    Blueprint,
    Construction,
    Ship,
)
from processes.models import (
    Process,
)


class WorldViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = World.objects.all()
    serializer_class = WorldSerializer
    #permission_classes = [permissions.IsAuthenticated]


class MovableViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = Movable.objects.all()
    serializer_class = MovableSerializer
    #permission_classes = [permissions.IsAuthenticated]

    @action(detail = True, methods = ['post'])
    def move_to(self, request, pk = None):
        movable = self.get_object()
        x = request.data['x']
        y = request.data['y']
        movable.move_to((x, y))
        serializer = self.get_serializer(movable)
        return Response(serializer.data)


class SectorViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = Sector.objects.all()
    serializer_class = SectorSerializer
    #permission_classes = [permissions.IsAuthenticated]


class CelestialViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = Celestial.objects.all()
    serializer_class = CelestialSerializer
    #permission_classes = [permissions.IsAuthenticated]


class EmpireViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = Empire.objects.all()
    serializer_class = EmpireSerializer
    #permission_classes = [permissions.IsAuthenticated]


class BlueprintViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = Blueprint.objects.all()
    serializer_class = BlueprintSerializer
    #permission_classes = [permissions.IsAuthenticated]

    @action(detail = True, methods  =['post'])
    def build(self, request, pk = None):
        from world.models import Celestial
        from processes.serializers import ProcessSerializer
        blueprint = self.get_object()
        celestial = Celestial.objects.get(**resolve(urlparse(request.data['celestial']).path).kwargs)
        process = blueprint.build(celestial)
        assert process is not None
        serializer = ProcessSerializer(process, context = dict(request = request))
        return Response(serializer.data)


class ConstructionViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet):

    queryset = Construction.objects.all()
    serializer_class = ConstructionSerializer
    #permission_classes = [permissions.IsAuthenticated]


class ShipViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet):

    queryset = Ship.objects.all()
    serializer_class = ShipSerializer
    #permission_classes = [permissions.IsAuthenticated]


class ProcessViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet):

    queryset = Process.objects.all()
    serializer_class = ProcessSerializer
    #permission_classes = [permissions.IsAuthenticated]
