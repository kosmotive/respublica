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

    owner   = serializers.HyperlinkedRelatedField(view_name =  'empire-detail', read_only = True, allow_null = True)
    process = serializers.HyperlinkedRelatedField(view_name = 'process-detail', read_only = True, allow_null = True)

    class Meta:
        model  = Movable
        fields = ['url', 'position', 'destination', 'speed', 'next_position', 'ship_set', 'owner', 'process']


class SectorSerializer(serializers.HyperlinkedModelSerializer):

    processes = serializers.HyperlinkedRelatedField(view_name = 'process-detail', read_only = True, many = True)

    class Meta:
        model  = Sector
        fields = ['url', 'name', 'celestial_set', 'processes']


class CelestialSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model  = Celestial
        fields = ['url', 'sector', 'position', 'features', 'habitated_by']
