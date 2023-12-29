from django.contrib.auth.models import User
from rest_framework import serializers

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


class UserSerializer(serializers.HyperlinkedModelSerializer):

    empire = serializers.HyperlinkedRelatedField(view_name = 'empire-detail', read_only = True)

    class Meta:
        model = User
        fields = ['url', 'username', 'empire']


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

    process = serializers.HyperlinkedRelatedField(view_name = 'process-detail', read_only = True, allow_null = True)

    class Meta:
        model  = Sector
        fields = ['url', 'position', 'name', 'celestial_set', 'process']


class CelestialSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model  = Celestial
        fields = ['url', 'sector', 'position', 'features', 'habitated_by']


class UnveiledSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model  = Unveiled
        fields = ['url', 'position', 'by_whom']


class EmpireSerializer(serializers.HyperlinkedModelSerializer):

    movables = serializers.HyperlinkedRelatedField(view_name = 'movable-detail', read_only = True, many = True)
    ships    = serializers.HyperlinkedRelatedField(view_name =    'ship-detail', read_only = True, many = True)

    class Meta:
        model  = Empire
        fields = ['url', 'name', 'habitat', 'movables', 'ships']


class BlueprintSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model  = Blueprint
        fields = ['url', 'base_id', 'empire', 'data']


class ConstructionSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model  = Construction
        fields = ['url', 'blueprint', 'celestial']


class ShipSerializer(serializers.HyperlinkedModelSerializer):

    owner = serializers.HyperlinkedRelatedField(view_name = 'empire-detail', read_only = True)

    class Meta:
        model  = Ship
        fields = ['url', 'blueprint', 'movable', 'owner']


class ProcessSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model  = Process
        fields = ['url', 'start_tick', 'end_tick', 'handler_id', 'data']