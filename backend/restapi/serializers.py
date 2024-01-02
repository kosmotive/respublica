from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.reverse import reverse

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


class LoginSerializer(serializers.Serializer):

    username = serializers.CharField(
        label = 'Username',
        write_only = True)
    password = serializers.CharField(
        label = 'Password',
        style = dict(input_type = 'password'),  ## will be used for the browsable API
        trim_whitespace = False,
        write_only = True)

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        if username and password:
            user = authenticate(
                request = self.context.get('request'),
                username = username,
                password = password)

            if not user:
                raise serializers.ValidationError('Authentication failed.', code='authorization')

            attrs['user'] = user
            return attrs

        else:
            raise serializers.ValidationError('Username and password required.', code='authorization')


class WorldSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model  = World
        fields = ['url', 'now', 'last_tick_timestamp', 'remaining_seconds', 'version']


class MovableSerializer(serializers.HyperlinkedModelSerializer):

    owner   = serializers.HyperlinkedRelatedField(view_name =  'empire-detail', read_only = True, allow_null = True)
    process = serializers.HyperlinkedRelatedField(view_name = 'process-detail', read_only = True, allow_null = True)

    class Meta:
        model  = Movable
        fields = ['url', 'position', 'destination', 'speed', 'next_position', 'ship_set', 'owner', 'process', 'name', 'trajectory']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.Meta.depth = self.context.get('depth', 0)
        assert self.Meta.depth in (0, 1)


class CelestialSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model  = Celestial
        fields = ['url', 'sector', 'position', 'features', 'habitated_by', 'remaining_capacity']


class SectorSerializer(serializers.HyperlinkedModelSerializer):

    process = serializers.HyperlinkedRelatedField(view_name = 'process-detail', read_only = True, allow_null = True)

    class Meta:
        model  = Sector
        fields = ['url', 'position', 'name', 'celestial_set', 'process']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.Meta.depth = self.context.get('depth', 0)
        assert self.Meta.depth in (0, 1)

    def get_fields(self):
        fields = super().get_fields()
        if self.Meta.depth == 1:
            fields['celestial_set'] = CelestialSerializer(read_only = True, many = True)
        return fields


class UnveiledSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model  = Unveiled
        fields = ['url', 'position', 'by_whom']


class EmpireSerializer(serializers.HyperlinkedModelSerializer):

    movables  = serializers.HyperlinkedRelatedField(view_name = 'movable-detail', read_only = True, many = True)
    ships     = serializers.HyperlinkedRelatedField(view_name =    'ship-detail', read_only = True, many = True)
    territory = serializers.SerializerMethodField();

    class Meta:
        model  = Empire
        fields = ['url', 'name', 'habitat', 'movables', 'ships', 'territory', 'origin', 'blueprint_set']

    def get_territory(self, empire):
        return empire.territory.explicit();


class BlueprintSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model  = Blueprint
        fields = ['url', 'base_id', 'empire', 'data', 'requirements']


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

    data = serializers.SerializerMethodField();

    class Meta:
        model  = Process
        fields = ['url', 'start_tick', 'end_tick', 'handler_id', 'data']

    def get_data(self, process):
        data = dict()
        for key, value in process.data.items():
            if key.endswith('_id'):
                basename = key[:-3]
                url = reverse(f'{basename}-detail', kwargs=dict(pk = value), request = self.context.get('request'))
                data[f'{basename}_url'] = url
            else:
                data[key] = value
        return data
