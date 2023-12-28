from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from game.serializers import (
    EmpireSerializer,
)
from game.models import (
    Empire,
)


class EmpireViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = Empire.objects.all()
    serializer_class = EmpireSerializer
    #permission_classes = [permissions.IsAuthenticated]
