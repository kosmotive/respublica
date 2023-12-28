from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from world.serializers import (
    WorldSerializer,
    MovableSerializer,
)
from world.models import (
    World,
    Movable,
    Sector,
    Celestial,
)


class WorldViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = World.objects.all()
    serializer_class = WorldSerializer
    #permission_classes = [permissions.IsAuthenticated]


class MovableViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = Movable.objects.all()
    serializer_class = MovableSerializer
    #permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=['post'])
    def move_to(self, request, pk=None):
        movable = self.get_object()
        x = request.data['x']
        y = request.data['y']
        movable.move_to((x, y))
