from rest_framework import serializers

from world.models import (
    World,
    Movable,
    Sector,
    Celestial,
)


class WorldSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model  = World
        fields = ['now', 'last_tick_timestamp', 'remaining_seconds']


class MovableSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model  = Movable
        fields = ['position', 'destination', 'speed', 'next_position']
