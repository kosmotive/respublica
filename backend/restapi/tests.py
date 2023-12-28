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


def normalize(data):
    if isinstance(data, dict):
        return {key: normalize(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [normalize(value) for value in data]
    elif isinstance(data, str):
        return urlparse(data).path
    elif isinstance(data, np.ndarray):
        return data.tolist()
    else:
        return data


class BaseRestTest(APITestCase):

    def setUp(self):
        generate_test_world(radius = 10, density = 0.5, seed = 0)


class WorldTest(BaseRestTest):

    def expected_details(self, *objects):
        details = [
            {
                'url': reverse('world-detail', kwargs = dict(pk = obj.pk)),
                'now': 1,
                'last_tick_timestamp': round(time.time()),
                'remaining_seconds': 60,
            }
            for obj in objects
        ]
        return normalize(details[0]) if len(objects) == 1 else normalize(details)

    def test_list(self):
        response = self.client.get(reverse('world-list'), format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(normalize(response.data), [self.expected_details(World.objects.get())])

    def test_detail(self):
        url = reverse('world-detail', kwargs = dict(pk = World.objects.get().pk))
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(normalize(response.data), self.expected_details(World.objects.get()))


class MovableTest(BaseRestTest):

    def expected_details(self, *objects):
        details = [
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
        return normalize(details[0]) if len(objects) == 1 else normalize(details)

    def test_list(self):
        response = self.client.get(reverse('movable-list'), format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(normalize(response.data), [self.expected_details(Movable.objects.get())])

    def test_detail(self):
        url = reverse('movable-detail', kwargs = dict(pk = Movable.objects.get().pk))
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(normalize(response.data), self.expected_details(Movable.objects.get()))

    def test_move_to(self):
        url = reverse('movable-move-to', kwargs = dict(pk = Movable.objects.get().pk))
        response = self.client.post(url, dict(x = -3, y = +1), format='json')
        self.test_detail()


class SectorTest(BaseRestTest):

    def expected_details(self, *objects):
        details = [
            {
                'url': reverse('sector-detail', kwargs = dict(pk = obj.pk)),
                'position': obj.position,
                'name': obj.name,
                'celestial_set': [
                    reverse('celestial-detail', kwargs = dict(pk = celestial.pk)) for celestial in obj.celestial_set.all()
                ],
                'processes': [
                    reverse('process-detail', kwargs = dict(pk = process.pk)) for process in obj.processes.all()
                ],
            }
            for obj in objects
        ]
        return normalize(details[0]) if len(objects) == 1 else normalize(details)

    def test_list(self):
        response = self.client.get(reverse('sector-list'), format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(normalize(response.data), self.expected_details(*Sector.objects.all()))

    def test_detail(self):
        sector = Sector.objects.all()[0]
        url = reverse('sector-detail', kwargs = dict(pk = sector.pk))
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(normalize(response.data), self.expected_details(sector))


class CelestialTest(BaseRestTest):

    def expected_details(self, *objects):
        details = [
            {
                'url': reverse('celestial-detail', kwargs = dict(pk = obj.pk)),
                'sector': reverse('sector-detail', kwargs = dict(pk = obj.sector.pk)),
                'position': obj.position,
                'features': obj.features,
                'habitated_by': None if obj.habitated_by is None else reverse('empire-detail', kwargs = dict(pk = obj.habitated_by.pk)),
            }
            for obj in objects
        ]
        return normalize(details[0]) if len(objects) == 1 else normalize(details)

    def test_list(self):
        response = self.client.get(reverse('celestial-list'), format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(normalize(response.data), self.expected_details(*Celestial.objects.all()))

    def test_detail(self):
        celestial = Celestial.objects.all()[0]
        url = reverse('celestial-detail', kwargs = dict(pk = celestial.pk))
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(normalize(response.data), self.expected_details(celestial))


class EmpireTest(BaseRestTest):

    def expected_details(self, *objects):
        details = [
            {
                'url': reverse('empire-detail', kwargs = dict(pk = obj.pk)),
                'name': obj.name,
                'celestial_set': [
                    reverse('celestial-detail', kwargs = dict(pk = celestial.pk)) for celestial in obj.celestial_set.all()
                ],
                'movables': [
                    reverse('movable-detail', kwargs = dict(pk = process.pk)) for process in obj.movables.all()
                ],
            }
            for obj in objects
        ]
        return normalize(details[0]) if len(objects) == 1 else normalize(details)

    def test_list(self):
        response = self.client.get(reverse('empire-list'), format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(normalize(response.data), [self.expected_details(*Empire.objects.all())])

    def test_detail(self):
        empire = Empire.objects.all()[0]
        url = reverse('empire-detail', kwargs = dict(pk = empire.pk))
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(normalize(response.data), self.expected_details(empire))
