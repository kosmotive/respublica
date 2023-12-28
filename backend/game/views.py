from urllib.parse import urlparse

from django.urls import resolve
from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import bad_request

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


class ConstructionViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = Construction.objects.all()
    serializer_class = ConstructionSerializer
    #permission_classes = [permissions.IsAuthenticated]


class ShipViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = Ship.objects.all()
    serializer_class = ShipSerializer
    #permission_classes = [permissions.IsAuthenticated]
