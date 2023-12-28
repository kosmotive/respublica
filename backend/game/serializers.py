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
        fields = ['url', 'name', 'celestial_set', 'movables']


class BlueprintSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model  = Blueprint
        fields = ['url', 'base_id', 'empire', 'data']


class ConstructionSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model  = Construction
        fields = ['url', 'blueprint', 'celestial']


class ShipSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model  = Ship
        fields = ['url', 'blueprint', 'movable', 'owner']
