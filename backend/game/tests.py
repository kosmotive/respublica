from django.test import TestCase

from game.models import (
    Empire,
)
from world.models import (
    World,
    Sector,
    Celestial,
)

from tools.testtools import order_tuple_list


class EmpireTest(TestCase):

    def setUp(self):
        self.world = World.objects.create()
        self.empire = Empire.objects.create(name = 'Foos')

        sector1 = Sector.objects.create(position_x =  1, position_y =  1, name = 'S1')
        sector2 = Sector.objects.create(position_x = -1, position_y = -1, name = 'S2')
        sector3 = Sector.objects.create(position_x =  1, position_y = -1, name = 'S3')

        Celestial.objects.create(
            sector = sector1,
            position = 0,
            features = dict(),
            habitated_by = self.empire)

        Celestial.objects.create(
            sector = sector2,
            position = 0,
            features = dict(),
            habitated_by = self.empire)

    def test_territory(self):
        actual = order_tuple_list(self.empire.territory.explicit())
        expected = order_tuple_list([
                ( 0, 0),
                (-1,-1),
                ( 1,-1),
                ( 0,-2),
                (-2,-2),
                (-3,-1),
                (-2, 0),
                (-1, 1),
                ( 0, 2),
                ( 2, 2),
                ( 3, 1),
                ( 2, 0),
                ( 1, 1),
            ])
        self.assertSequenceEqual(actual, expected)
