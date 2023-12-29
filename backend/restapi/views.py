from urllib.parse import urlparse

from django.contrib.auth.models import User
from django.db import models
from django.urls import resolve
from rest_framework import permissions, viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response

from restapi.serializers import (
    UserSerializer,

    WorldSerializer,
    MovableSerializer,
    SectorSerializer,
    CelestialSerializer,
    UnveiledSerializer,

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
    Unveiled,
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


class UserViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = User.objects.all()
    serializer_class = UserSerializer


class WorldViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = World.objects.all()
    serializer_class = WorldSerializer


class MovableViewSet(viewsets.ReadOnlyModelViewSet):

    serializer_class = MovableSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        unveiled_qs = Unveiled.objects.filter(
            by_whom__player = self.request.user,
            position_x = models.OuterRef('position_x'),
            position_y = models.OuterRef('position_y'))
        return Movable.objects.filter(models.Exists(unveiled_qs))

    @action(detail = True, methods = ['post'])
    def move_to(self, request, pk = None):
        movable = self.get_object()
        x = request.data['x']
        y = request.data['y']
        movable.move_to((x, y))
        serializer = self.get_serializer(movable)
        return Response(serializer.data)


class SectorViewSet(viewsets.ReadOnlyModelViewSet):

    serializer_class = SectorSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        unveiled_qs = Unveiled.objects.filter(
            by_whom__player = self.request.user,
            position_x = models.OuterRef('position_x'),
            position_y = models.OuterRef('position_y'))
        return Sector.objects.filter(models.Exists(unveiled_qs))


class CelestialViewSet(viewsets.ReadOnlyModelViewSet):

    serializer_class = CelestialSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        unveiled_qs = Unveiled.objects.filter(
            by_whom__player = self.request.user,
            position_x = models.OuterRef('sector__position_x'),
            position_y = models.OuterRef('sector__position_y'))
        return Celestial.objects.filter(models.Exists(unveiled_qs))


class UnveiledViewSet(viewsets.ReadOnlyModelViewSet):

    serializer_class = UnveiledSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Unveiled.objects.filter(by_whom__player = self.request.user)


class EmpireViewSet(viewsets.ReadOnlyModelViewSet):

    serializer_class = EmpireSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Empire.objects.filter(player = self.request.user)


class BlueprintViewSet(viewsets.ReadOnlyModelViewSet):

    serializer_class = BlueprintSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Blueprint.objects.filter(empire__player = self.request.user)

    @action(detail = True, methods = ['post'])
    def build(self, request, pk = None):
        from world.models import Celestial
        from restapi.serializers import ProcessSerializer
        blueprint = self.get_object()
        celestial = Celestial.objects.get(**resolve(urlparse(request.data['celestial']).path).kwargs)
        process = blueprint.build(celestial)
        assert process is not None
        serializer = ProcessSerializer(process, context = dict(request = request))
        return Response(serializer.data)


class ConstructionViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet):

    serializer_class = ConstructionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Construction.objects.filter(blueprint__empire__player = self.request.user)


class ShipViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet):

    serializer_class = ShipSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Ship.objects.filter(blueprint__empire__player = self.request.user)


class ProcessViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):

    serializer_class = ProcessSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Process.objects.filter(owner__player = self.request.user)

    def destroy(self, request, *args, **kwargs):
        process = self.get_object()
        process_id = process.id
        process.handler.cancel(process)
        assert Process.objects.filter(id = process_id).count() == 0
        return Response(status=status.HTTP_204_NO_CONTENT)
