import time
from urllib.parse import urlparse

from django.contrib.auth.models import User
from django.urls import resolve, reverse
from rest_framework import status
from rest_framework.test import APITestCase

import numpy as np

from world.generator import generate_test_world

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


def normalize(data, ignore_keys = frozenset()):
    if isinstance(data, dict):
        return {key: normalize(value) for key, value in data.items() if key not in ignore_keys}
    elif isinstance(data, list):
        return [normalize(value, ignore_keys) for value in data]
    elif isinstance(data, str):
        return urlparse(data).path
    elif isinstance(data, np.ndarray):
        return data.tolist()
    else:
        return data


class BaseRestTest(APITestCase):

    def setUp(self):
        generate_test_world(radius = 10, density = 0.5, seed = 0)
        self.client.login(username='testuser', password='password')
        self.list_url = reverse(f'{self.model.__name__.lower()}-list')

    def get_queryset(self):
        return self.model.objects

    @property
    def object(self):
        return self.get_queryset().all()[0]

    @property
    def object_url(self):
        return reverse(f'{self.model.__name__.lower()}-detail', kwargs = dict(pk = self.object.pk))

    def test_list(self):
        ignore_keys = getattr(self, 'ignore_keys', frozenset())
        response = self.client.get(self.list_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(normalize(response.data, ignore_keys), normalize(self.expected_details(self.get_queryset().all()), ignore_keys))

    def test_detail(self):
        ignore_keys = getattr(self, 'ignore_keys', frozenset())
        if self.get_queryset().count() > 0:
            response = self.client.get(self.object_url, format='json')
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(normalize(response.data, ignore_keys), normalize(self.expected_details([self.object])[0], ignore_keys))

    def test_delete(self):
        if self.get_queryset().count() > 0:
            response = self.client.delete(self.object_url)
            self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_different_user(self):
        self.client.logout()
        User.objects.create_user(
            username='testuser2',
            password='password')
        self.client.login(username='testuser2', password='password')

        # Check forbidden access to details
        response = self.client.get(self.object_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Check no appearance in list
        response = self.client.get(self.list_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)


class WorldTest(BaseRestTest):

    model = World
    ignore_keys = ['remaining_seconds', 'last_tick_timestamp']
    test_delete = False
    test_different_user = False

    def expected_details(self, objects):
        return [
            {
                'url': reverse('world-detail', kwargs = dict(pk = obj.pk)),
                'now': 1,
                'last_tick_timestamp': round(time.time()),
                'remaining_seconds': 60,
                'version': obj.version,
            }
            for obj in objects
        ]


class MovableTest(BaseRestTest):

    model = Movable
    test_delete = False

    @property
    def movable(self):
        return Movable.objects.get()

    @property
    def move_to_url(self):
        return reverse('movable-move-to', kwargs = dict(pk = self.movable.pk))

    def expected_details(self, objects):
        return [
            {
                'url': reverse('movable-detail', kwargs = dict(pk = obj.pk)),
                'position': obj.position,
                'destination': obj.destination,
                'speed': obj.speed,
                'next_position': obj.next_position,
                'ship_set': [
                    reverse('ship-detail', kwargs = dict(pk = ship.pk)) for ship in obj.ship_set.all()
                ],
                'owner': reverse('empire-detail', kwargs = dict(pk = obj.owner.pk)),
                'process': None if obj.process is None else reverse('process-detail', kwargs = dict(pk = obj.process.pk)),
                'name': obj.name,
                'trajectory': obj.trajectory,
            }
            for obj in objects
        ]

    def test_move_to(self):
        response = self.client.post(self.move_to_url, dict(x = -3, y = +1), format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(normalize(response.data), normalize(self.expected_details([self.movable])[0]))
        self.test_detail()

    def test_different_user(self):
        super(MovableTest, self).test_different_user()

        # Check forbidden access to "move_to" action
        response = self.client.post(self.move_to_url, dict(x = -3, y = +1), format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class SectorTest(BaseRestTest):

    model = Sector
    test_delete = False

    def get_queryset(self):
        empire = Empire.objects.get()
        unveiled_sectors = [Sector.objects.filter(position_x = u.position_x, position_y = u.position_y).first() for u in Unveiled.objects.filter(by_whom = empire)]
        return Sector.objects.filter(id__in = [s.id for s in unveiled_sectors if s is not None])

    def expected_details(self, objects):
        return [
            {
                'url': reverse('sector-detail', kwargs = dict(pk = obj.pk)),
                'position': obj.position,
                'name': obj.name,
                'celestial_set': [
                    reverse('celestial-detail', kwargs = dict(pk = celestial.pk)) for celestial in obj.celestial_set.all()
                ],
                'process': None if obj.process is None else reverse('process-detail', kwargs = dict(pk = obj.process.pk)),
            }
            for obj in objects
        ]


class CelestialTest(BaseRestTest):

    model = Celestial
    test_delete = False

    def get_queryset(self):
        empire = Empire.objects.get()
        unveiled_sectors    = [Sector.objects.filter(position_x = u.position_x, position_y = u.position_y).first() for u in Unveiled.objects.filter(by_whom = empire)]
        unveiled_sectors_qs =  Sector.objects.filter(id__in = [s.id for s in unveiled_sectors if s is not None])
        return Celestial.objects.filter(sector__in = unveiled_sectors_qs)

    def expected_details(self, objects):
        return [
            {
                'url': reverse('celestial-detail', kwargs = dict(pk = obj.pk)),
                'sector': reverse('sector-detail', kwargs = dict(pk = obj.sector.pk)),
                'position': obj.position,
                'features': obj.features,
                'habitated_by': None if obj.habitated_by is None else reverse('empire-detail', kwargs = dict(pk = obj.habitated_by.pk)),
            }
            for obj in objects
        ]


class UnveiledTest(BaseRestTest):

    model = Unveiled
    test_delete = False

    def expected_details(self, objects):
        return [
            {
                'url': reverse('unveiled-detail', kwargs = dict(pk = obj.pk)),
                'position': obj.position,
                'by_whom': reverse('empire-detail', kwargs = dict(pk = obj.by_whom.pk)),
            }
            for obj in objects
        ]


class EmpireTest(BaseRestTest):

    model = Empire
    test_delete = False

    def expected_details(self, objects):
        return [
            {
                'url': reverse('empire-detail', kwargs = dict(pk = obj.pk)),
                'name': obj.name,
                'habitat': [
                    reverse('celestial-detail', kwargs = dict(pk = celestial.pk)) for celestial in obj.habitat.all()
                ],
                'ships': [
                    reverse('ship-detail', kwargs = dict(pk = process.pk)) for process in obj.ships.all()
                ],
                'movables': [
                    reverse('movable-detail', kwargs = dict(pk = process.pk)) for process in obj.movables.all()
                ],
                'territory': obj.territory.explicit(),
                'origin': obj.origin,
                'blueprint_set': [
                    reverse('blueprint-detail', kwargs = dict(pk = blueprint.pk)) for blueprint in obj.blueprint_set.all()
                ],
            }
            for obj in objects
        ]


class BlueprintTest(BaseRestTest):

    model = Blueprint
    test_delete = False

    @property
    def empire(self):
        return Empire.objects.get()

    @property
    def celestial_url(self):
        return reverse('celestial-detail', kwargs = dict(pk = self.empire.habitat.get().pk))

    @property
    def build_url(self):
        return reverse('blueprint-build', kwargs = dict(pk = self.empire.blueprint_set.get(base_id = 'constructions/digital-cave').pk))

    def expected_details(self, objects):
        return [
            {
                'url': reverse('blueprint-detail', kwargs = dict(pk = obj.pk)),
                'base_id': obj.base_id,
                'empire': reverse('empire-detail', kwargs = dict(pk = obj.empire.pk)),
                'data': obj.data,
            }
            for obj in objects
        ]

    def test_build(self):
        response = self.client.post(self.build_url, dict(celestial = self.celestial_url), format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(normalize(response.data), normalize(ProcessTest().expected_details([Process.objects.get()])[0]))

        return response.data['url']

    def test_different_user(self):
        super(BlueprintTest, self).test_different_user()

        # Check forbidden access to "build" action
        response = self.client.post(self.build_url, dict(celestial = self.celestial_url), format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_celestial_of_different_user(self):
        celestial = Celestial.objects \
            .filter(features__capacity__gte = 1) \
            .exclude(habitated_by = self.empire)[0]

        # Issue the build process
        celestial_url = reverse('celestial-detail', kwargs = dict(pk = celestial.pk))
        response = self.client.post(self.build_url, dict(celestial = celestial_url), format='json')

        # Check for denial
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class ConstructionTest(BaseRestTest):

    model = Construction

    def setUp(self):
        super(ConstructionTest, self).setUp()

        # Add constructions
        empire    = Empire.objects.get()
        blueprint = empire.blueprint_set.get(base_id = 'constructions/digital-cave')
        celestial = empire.habitat.get()
        Construction.objects.create(blueprint = blueprint, celestial = celestial)

    def expected_details(self, objects):
        return [
            {
                'url': reverse('construction-detail', kwargs = dict(pk = obj.pk)),
                'blueprint': reverse('blueprint-detail', kwargs = dict(pk = obj.blueprint.pk)),
                'celestial': reverse('celestial-detail', kwargs = dict(pk = obj.celestial.pk)),
            }
            for obj in objects
        ]


class ShipTest(BaseRestTest):

    model = Ship

    def expected_details(self, objects):
        return [
            {
                'url': reverse('ship-detail', kwargs = dict(pk = obj.pk)),
                'blueprint': reverse('blueprint-detail', kwargs = dict(pk = obj.blueprint.pk)),
                'movable': reverse('movable-detail', kwargs = dict(pk = obj.movable.pk)),
                'owner': reverse('empire-detail', kwargs = dict(pk = obj.owner.pk)),
            }
            for obj in objects
        ]


class ProcessTest(BaseRestTest):

    model = Process

    def setUp(self):
        super(ProcessTest, self).setUp()

        # Create movement process
        self.movable = Movable.objects.get()
        self.movable.move_to((-3, +1))

        # Create build process
        empire    = Empire.objects.get()
        blueprint = empire.blueprint_set.get(base_id = 'constructions/digital-cave')
        celestial = empire.habitat.get()
        blueprint.build(celestial = celestial)

    def expected_details(self, objects):
        def resolve_data(handler_id, data):
            data = dict(data)
            if handler_id == 'BuildingHandler':
                data['blueprint_url'] = reverse(f'blueprint-detail', kwargs = dict(pk = data.pop('blueprint_id')))
                data['celestial_url'] = reverse(f'celestial-detail', kwargs = dict(pk = data.pop('celestial_id')))
            if handler_id == 'MovementHandler':
                data['movable_url'] = reverse(f'movable-detail', kwargs = dict(pk = data.pop('movable_id')))
            return data
        return [
            {
                'url': reverse('process-detail', kwargs = dict(pk = obj.pk)),
                'start_tick': obj.start_tick,
                'end_tick': obj.end_tick,
                'handler_id': obj.handler_id,
                'data': None if obj.data is None else resolve_data(obj.handler_id, obj.data),
            }
            for obj in objects
        ]

    def test_delete(self):
        super(ProcessTest, self).test_delete() ## cancel movement process
        super(ProcessTest, self).test_delete() ## cancel build process

        # Check whether movement was aborted
        self.movable.refresh_from_db()
        self.assertEqual(tuple(self.movable.destination), tuple(self.movable.position))

    def test_different_user(self):
        super(ProcessTest, self).test_different_user()

        # Check forbidden access to delete
        response = self.client.delete(self.object_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


# Do not run the base class as a test
del BaseRestTest
