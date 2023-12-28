from rest_framework import serializers

from game.models import (
    Empire,
    Blueprint,
    Construction,
    Ship,
)


class EmpireSerializer(serializers.HyperlinkedModelSerializer):

    movables = serializers.HyperlinkedRelatedField(view_name = 'movable-detail', read_only = True, many = True)

    class Meta:
        model  = Empire
        fields = ['url', 'id', 'name', 'celestial_set', 'movables']


class BlueprintSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model  = Blueprint
        fields = ['url', 'id', 'base_id', 'empire', 'data']


class ConstructionSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model  = Construction
        fields = ['url', 'id', 'blueprint', 'celestial']


class ShipSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model  = Ship
        fields = ['url', 'id', 'blueprint', 'movable', 'owner']
