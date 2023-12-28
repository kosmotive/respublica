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
        fields = ['url', 'id', 'now', 'last_tick_timestamp', 'remaining_seconds']


class MovableSerializer(serializers.HyperlinkedModelSerializer):

    owner = serializers.HyperlinkedRelatedField(view_name = 'empire-detail', read_only = True)

    class Meta:
        model  = Movable
        fields = ['url', 'id', 'position', 'destination', 'speed', 'next_position', 'ship_set', 'owner']


class SectorSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model  = Sector
        fields = ['url', 'id', 'name', 'celestial_set']


class CelestialSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model  = Celestial
        fields = ['url', 'id', 'sector', 'position', 'features', 'habitated_by']
