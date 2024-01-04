from urllib.parse import urlparse

from django.contrib.auth import login
from django.contrib.auth.models import User
from django.db import models
from django.urls import resolve
from rest_framework import permissions, views, viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response

from restapi.permissions import IsObjectOwner
from restapi.serializers import (
    UserSerializer,
    LoginSerializer,

    WorldSerializer,
    MovableSerializer,
    SectorSerializer,
    CelestialSerializer,
    UnveiledSerializer,

    EmpireSerializer,
    PrivateEmpireSerializer,
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

    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return User.objects.filter(id = self.request.user.id)


class LoginView(views.APIView):

    def post(self, request, format = None):
        serializer = LoginSerializer(
            data = self.request.data,
            context = dict(request = self.request))
        serializer.is_valid(raise_exception = True)
        user = serializer.validated_data['user']
        login(request, user)
        return Response(None, status = status.HTTP_202_ACCEPTED)


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

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['depth'] = int(self.request.query_params.get('depth', 0))
        return context

    @action(detail = True, methods = ['post'], permission_classes = [permissions.IsAuthenticated, IsObjectOwner])
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

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['depth'] = int(self.request.query_params.get('depth', 0))
        return context


class CelestialViewSet(viewsets.ReadOnlyModelViewSet):

    serializer_class = CelestialSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        unveiled_qs = Unveiled.objects.filter(
            by_whom__player = self.request.user,
            position_x = models.OuterRef('sector__position_x'),
            position_y = models.OuterRef('sector__position_y'))
        return Celestial.objects.filter(models.Exists(unveiled_qs))

    @action(detail = True, methods = ['post'], permission_classes = [permissions.IsAuthenticated])
    def colonize(self, request, pk = None):
        celestial = self.get_object()
        empire    = request.user.empire
        movable   = Movable.objects.get(**resolve(urlparse(request.data['movable']).path).kwargs) if len(request.data.get('movable', '')) > 0 else None
        process   = celestial.colonize(empire, movable)
        assert process is not None
        if movable is not None:
            serializer = MovableSerializer(movable, context = dict(request = request))
            return Response(serializer.data)
        else:
            serializer = ProcessSerializer(process, context = dict(request = request))
            return Response(serializer.data)


class UnveiledViewSet(viewsets.ReadOnlyModelViewSet):

    serializer_class = UnveiledSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Unveiled.objects.filter(by_whom__player = self.request.user)


class EmpireViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):

    queryset = Empire.objects.all()
    serializer_class = EmpireSerializer
    permission_classes = [permissions.IsAuthenticated]


class PrivateEmpireViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):

    serializer_class = PrivateEmpireSerializer
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
        unveiled_qs = Unveiled.objects.filter(
            by_whom__player = self.request.user,
            position_x = models.OuterRef('movable__position_x'),
            position_y = models.OuterRef('movable__position_y'))
        qs_unveiled = Ship.objects.filter(models.Exists(unveiled_qs))
        qs_owned = Ship.objects.filter(blueprint__empire__player = self.request.user)
        return qs_unveiled | qs_owned


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
