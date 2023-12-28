from rest_framework import serializers

from game.models import (
    Empire,
)


class EmpireSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model  = Empire
        fields = ['url', 'name', 'celestial_set']
