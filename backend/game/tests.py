from django.test import TestCase

from game.models import (
    Empire,
    Blueprint,
    Construction,
)
from world.models import (
    World,
    Sector,
    Celestial,
)
from processes.models import (
    Process,
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


class BlueprintTest(TestCase):

    def setUp(self):
        self.world = World.objects.create()
        self.empire = Empire.objects.create(name = 'Foos')
        self.digital_cave_blueprint = Blueprint.objects.get(base_id = 'constructions/digital-cave')

        sector = Sector.objects.create(position_x = 0, position_y = 0, name = 'Bar')
        self.celestial = Celestial.objects.create(
            sector = sector,
            position = 0,
            features = dict(capacity = 1),
            habitated_by = self.empire)

    def test_requirements(self):
        self.assertEqual(self.digital_cave_blueprint.requirements, list())
        self.assertEqual(Blueprint.objects.get(base_id = 'ships/colony-ship').requirements, ['shipyard'])

    def test_requirements_ok(self):
        self.assertTrue(self.digital_cave_blueprint.requirements_ok(self.celestial))
        self.assertFalse(Blueprint.objects.get(base_id = 'ships/colony-ship').requirements_ok(self.celestial))

        Construction.objects.create(blueprint = self.digital_cave_blueprint, celestial = self.celestial)
        self.assertFalse(self.digital_cave_blueprint.requirements_ok(self.celestial))

    def test_build(self):
        self.digital_cave_blueprint.build(self.world, self.celestial)

        for _ in range(3):
            self.assertEqual(len(Process.objects.all()), 1)
            self.world.tick()

        self.assertEqual(len(Process.objects.all()), 0)
        self.assertEqual(self.celestial.construction_set.count(), 1)

        digital_cave = self.celestial.construction_set.all()[0]
        self.assertEqual(digital_cave.blueprint.id, self.digital_cave_blueprint.id)
