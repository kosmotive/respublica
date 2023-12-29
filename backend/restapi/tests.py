import time
from urllib.parse import urlparse

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

    def test_list(self):
        ignore_keys = getattr(self, 'ignore_keys', frozenset())
        response = self.client.get(reverse(f'{self.model.__name__.lower()}-list'), format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(normalize(response.data, ignore_keys), normalize(self.expected_details(self.model.objects.all()), ignore_keys))

    def test_detail(self):
        ignore_keys = getattr(self, 'ignore_keys', frozenset())
        if self.model.objects.count() > 0:
            obj = self.model.objects.all()[0]
            url = reverse(f'{self.model.__name__.lower()}-detail', kwargs = dict(pk = obj.pk))
            response = self.client.get(url, format='json')
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(normalize(response.data, ignore_keys), normalize(self.expected_details([obj])[0], ignore_keys))

    def test_delete(self):
        if self.model.objects.count() > 0:
            obj = self.model.objects.all()[0]
            url = reverse(f'{self.model.__name__.lower()}-detail', kwargs = dict(pk = obj.pk))
            response = self.client.delete(url)
            self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class WorldTest(BaseRestTest):

    model = World
    ignore_keys = ['remaining_seconds', 'last_tick_timestamp']
    test_delete = False

    def expected_details(self, objects):
        return [
            {
                'url': reverse('world-detail', kwargs = dict(pk = obj.pk)),
                'now': 1,
                'last_tick_timestamp': round(time.time()),
                'remaining_seconds': 60,
            }
            for obj in objects
        ]


class MovableTest(BaseRestTest):

    model = Movable
    test_delete = False

    def expected_details(self, objects):
        return [
            {
                'url': reverse('movable-detail', kwargs = dict(pk = obj.pk)),
                'position': obj.position,
                'destination': obj.destination,
                'speed': obj.speed,
                'next_position': obj.next_position,
                'ship_set': [
                    reverse('ship-detail', kwargs = dict(pk = ship.pk)) for ship in obj.owner.ship_set.all()
                ],
                'owner': reverse('empire-detail', kwargs = dict(pk = obj.owner.pk)),
                'process': None if obj.process is None else reverse('process-detail', kwargs = dict(pk = obj.process.pk)),
            }
            for obj in objects
        ]

    def test_move_to(self):
        movable = Movable.objects.get()
        url = reverse('movable-move-to', kwargs = dict(pk = Movable.objects.get().pk))
        response = self.client.post(url, dict(x = -3, y = +1), format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(normalize(response.data), normalize(self.expected_details([Movable.objects.get()])[0]))
        self.test_detail()


class SectorTest(BaseRestTest):

    model = Sector
    test_delete = False

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
                'movables': [
                    reverse('movable-detail', kwargs = dict(pk = process.pk)) for process in obj.movables.all()
                ],
            }
            for obj in objects
        ]


class BlueprintTest(BaseRestTest):

    model = Blueprint
    test_delete = False

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
        # Get celestial
        empire = Empire.objects.get()
        celestial_url = reverse('celestial-detail', kwargs = dict(pk = empire.habitat.get().pk))

        # Issue the build process
        build_url = reverse('blueprint-build', kwargs = dict(pk = empire.blueprint_set.get(base_id = 'constructions/digital-cave').pk))
        response = self.client.post(build_url, dict(celestial = celestial_url), format='json')

        # Check build process APIs
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(normalize(response.data), normalize(ProcessTest().expected_details([Process.objects.get()])[0]))

        return response.data['url']


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
        return [
            {
                'url': reverse('process-detail', kwargs = dict(pk = obj.pk)),
                'start_tick': obj.start_tick,
                'end_tick': obj.end_tick,
                'handler_id': obj.handler_id,
                'data': obj.data,
            }
            for obj in objects
        ]

    def test_delete(self):
        super(ProcessTest, self).test_delete() ## cancel movement process
        super(ProcessTest, self).test_delete() ## cancel build process

        # Check whether movement was aborted
        self.movable.refresh_from_db()
        self.assertEqual(tuple(self.movable.destination), tuple(self.movable.position))


# Do not run the base class as a test
del BaseRestTest
