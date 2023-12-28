from rest_framework import permissions, viewsets, mixins
from rest_framework.decorators import action
from rest_framework.response import Response

from processes.serializers import (
    ProcessSerializer,
)
from processes.models import (
    Process,
)


class ProcessViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet):

    queryset = Process.objects.all()
    serializer_class = ProcessSerializer
    #permission_classes = [permissions.IsAuthenticated]
