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
        fields = ['url', 'now', 'last_tick_timestamp', 'remaining_seconds']


class MovableSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model  = Movable
        fields = ['url', 'position', 'destination', 'speed', 'next_position']


class SectorSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model  = Sector
        fields = ['url', 'name', 'celestial_set']


class CelestialSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model  = Celestial
        fields = ['url', 'sector', 'position', 'features', 'habitated_by']
