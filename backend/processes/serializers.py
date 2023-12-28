from rest_framework import serializers

from processes.models import (
    Process,
)


class ProcessSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model  = Process
        fields = ['url', 'start_tick', 'end_tick', 'handler_id', 'data']
