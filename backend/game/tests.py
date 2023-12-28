from django.test import TestCase

from game.models import (
    Empire,
    Blueprint,
    Construction,
    Ship,
)
from world.models import (
    World,
    Movable,
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
        self.construction_blueprint = Blueprint.objects.get(base_id = 'constructions/digital-cave')
        self.ship_blueprint = Blueprint.objects.get(base_id = 'ships/colony-ship')

        sector = Sector.objects.create(position_x = 0, position_y = 0, name = 'Bar')
        self.celestial = Celestial.objects.create(
            sector = sector,
            position = 0,
            features = dict(capacity = 1),
            habitated_by = self.empire)

    def test_requirements(self):
        self.assertEqual(self.construction_blueprint.requirements, list())
        self.assertEqual(self.ship_blueprint.requirements, ['constructions/shipyard'])

    def test_requirements_ok(self):
        self.assertTrue(self.construction_blueprint.requirements_ok(self.celestial))
        self.assertFalse(self.ship_blueprint.requirements_ok(self.celestial))

        Construction.objects.create(blueprint = self.construction_blueprint, celestial = self.celestial)
        self.assertFalse(self.construction_blueprint.requirements_ok(self.celestial))

    def test_build(self):
        self.construction_blueprint.build(self.celestial)

        for _ in range(3):
            self.assertEqual(len(Process.objects.all()), 1)
            self.world.tick()

        self.assertEqual(len(Process.objects.all()), 0)
        self.assertEqual(self.celestial.construction_set.count(), 1)

        construction = self.celestial.construction_set.get()
        self.assertEqual(construction.blueprint.id, self.construction_blueprint.id)

    def test_build_ship(self):
        # Build shipyard to satisfy requirements
        shipyard_blueprint = Blueprint.objects.get(base_id = 'constructions/shipyard')
        Construction.objects.create(blueprint = shipyard_blueprint, celestial = self.celestial)

        # Build ship
        queued = self.ship_blueprint.build(self.celestial)
        self.assertTrue(queued)

        for _ in range(self.ship_blueprint.cost):
            self.assertEqual(len(Process.objects.all()), 1)
            self.world.tick()

        self.assertEqual(len(Process.objects.all()), 0)
        self.assertEqual(Ship.objects.count(), 1)

        ship = self.empire.ship_set.get()
        self.assertEqual(ship.blueprint.id, self.ship_blueprint.id)
        self.assertEqual(ship.owner.id, self.empire.id)

        self.assertEqual(Movable.objects.count(), 1)
        self.assertEqual(tuple(ship.movable.position), tuple(self.celestial.sector.position))
        self.assertEqual(ship.movable.ship_set.count(), 1)
        self.assertEqual(ship.movable.ship_set.get().id, ship.id)
