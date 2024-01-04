from django.contrib.auth.models import User
from django.test import TestCase
import numpy as np

from world.models import (
    World,
    Movable,
    Sector,
    Celestial,
    Unveiled,
    hexgrid,
)
from processes.models import (
    Process,
)

from tools.testtools import order_tuple_list


def normalize_hexset_text(text):
    return '\n'.join([line.rstrip() for line in text.split('\n') if len(line.strip()) > 0])


class MovableTest(TestCase):

    def setUp(self):
        self.world = World.objects.create()
        self.movable = Movable.objects.create(
            custom_speed = 1,
            position_x = 0,
            position_y = 0)

    def test_next_position(self):
        self.movable.move_to((2,2))
        self.assertSequenceEqual(self.movable.next_position.tolist(), (1,1))

    def test_trajectory(self):
        self.movable.move_to((2,2))
        self.assertSequenceEqual(np.asarray(self.movable.trajectory).tolist(), np.asarray([(1,1), (2,2)]).tolist())

        self.movable.position_x = 4
        self.movable.position_y = 2
        self.movable.move_to((2,2))

        self.assertSequenceEqual(np.asarray(self.movable.trajectory).tolist(), np.asarray([(2,2)]).tolist())

    def test_speed(self):
        from game.models import Empire, Blueprint, Ship
        player    = User.objects.create(username = 'testuser', password = 'password')
        empire    = Empire.objects.create(name = 'Foos', player = player, origin_x = 0, origin_y = 0, color_hue = 0)
        blueprint = Blueprint.objects.get(empire = empire, base_id = 'ships/colony-ship')
        movable   = Movable.objects.create(position_x = 0, position_y = 0)
        ship = Ship.objects.create(
            blueprint = blueprint,
            movable   = movable)
        self.assertEqual(movable.speed, blueprint.data['speed'])

    def test_move_to_speed1(self):
        self.movable.custom_speed = 1
        self.movable.save()

        # Record the trajectory
        trajectory = list()
        def update_trajectory():
            trajectory.append(tuple(self.movable.position))

        # Move (0,0) -> (1,1) -> (2,2) 
        self.movable.move_to((2,2))
        self.assertSequenceEqual(self.movable.position.tolist(), (0,0))
        self.world.tick()
        self.movable.refresh_from_db()
        self.assertSequenceEqual(self.movable.position.tolist(), (1,1))
        update_trajectory()  ## (1,1)
        self.world.tick()
        self.movable.refresh_from_db()
        self.assertSequenceEqual(self.movable.position.tolist(), (2,2))
        self.assertEqual(len(Process.objects.all()), 0)
        update_trajectory()  ## (2,2)

        # Move (2,2) -> (1,1) or (3,1) -> (2,0) 
        self.movable.move_to((2,0))
        self.assertSequenceEqual(self.movable.position.tolist(), (2,2))
        self.world.tick()
        self.movable.refresh_from_db()
        self.assertIn(self.movable.position.tolist(), [[1,1], [3,1]])
        update_trajectory()  ## (1,1) or (3,1)
        self.world.tick()
        self.movable.refresh_from_db()
        self.assertSequenceEqual(self.movable.position.tolist(), (2,0))
        self.assertEqual(len(Process.objects.all()), 0)
        update_trajectory()  ## (2,0)

        # Don't move 
        self.world.tick()
        self.movable.refresh_from_db()

        # Move (2,0) -> (0,0) -> (-2,0)
        self.movable.move_to((-2,0))
        self.assertSequenceEqual(self.movable.position.tolist(), (2,0))
        self.world.tick()
        self.movable.refresh_from_db()
        self.assertSequenceEqual(self.movable.position.tolist(), (0,0))
        update_trajectory()  ## (0,0)
        self.world.tick()
        self.movable.refresh_from_db()
        self.assertSequenceEqual(self.movable.position.tolist(), (-2,0))
        self.assertEqual(len(Process.objects.all()), 0)
        update_trajectory()  ## (-2,0)

        # Order to move to (2,0), but immediately change to (-1,1)
        self.movable.move_to((2,0))
        self.movable.move_to((-1,1))
        self.assertEqual(len(Process.objects.all()), 1)
        self.world.tick()
        self.movable.refresh_from_db()
        self.assertSequenceEqual(self.movable.position.tolist(), (-1,1))
        self.assertEqual(len(Process.objects.all()), 0)
        update_trajectory()  ## (-1,1)

        return trajectory

    def test_move_to_unveiled(self):
        from game.models import Empire, Blueprint, Ship
        player = User.objects.create(username = 'testuser', password = 'password')
        empire = Empire.objects.create(name = 'Foos', player = player, origin_x = 0, origin_y = 0, color_hue = 0)
        blueprint = Blueprint.objects.get(empire = empire, base_id = 'ships/colony-ship')
        ship = Ship.objects.create(movable = self.movable, blueprint = blueprint)

        # Perform movement
        trajectory = self.test_move_to_speed1()

        # Check unveiled hexes
        expected = [hexgrid.DistanceSet(c, radius=1) for c in trajectory]
        expected = [tuple(c) for c in hexgrid.Union(expected).explicit()]
        actual = [(c.position_x, c.position_y) for c in Unveiled.objects.filter(by_whom = empire)]
        self.assertEqual(frozenset(actual), frozenset(expected))

    def test_move_to_speed2(self):
        self.movable.custom_speed = 2
        self.movable.save()

        # Move (0,0) -> (2,2) 
        self.movable.move_to((2,2))
        self.assertSequenceEqual(self.movable.position.tolist(), (0,0))
        self.world.tick()
        self.movable.refresh_from_db()
        self.assertSequenceEqual(self.movable.position.tolist(), (2,2))
        self.assertEqual(len(Process.objects.all()), 0)

    def test_move_to_speed0(self):
        self.movable.custom_speed = 0.5
        self.movable.save()

        # Move (0,0) -> (1,1) 
        self.movable.move_to((1,1))
        self.assertSequenceEqual(self.movable.position.tolist(), (0,0))
        self.world.tick()
        self.movable.refresh_from_db()
        self.assertSequenceEqual(self.movable.position.tolist(), (0,0))
        self.world.tick()
        self.movable.refresh_from_db()
        self.assertSequenceEqual(self.movable.position.tolist(), (1,1))
        self.assertEqual(len(Process.objects.all()), 0)


class CelestialTest(TestCase):

    def setUp(self):
        self.world = World.objects.create()
        self.sector = Sector.objects.create(position_x = 0, position_y = 0, name = 'S')
        self.celestial1 = Celestial.objects.create(sector = self.sector, position = 1, features = dict(capacity = 10))
        self.celestial2 = Celestial.objects.create(sector = self.sector, position = 2, features = dict(capacity = 10))

        from game.models import Empire, Blueprint, Ship
        self.player = User.objects.create(username = 'testuser', password = 'password')
        self.empire = Empire.objects.create(name = 'Foos', player = self.player, origin_x = 0, origin_y = 0, color_hue = 0)
        self.ship = Ship.objects.create(
            blueprint = Blueprint.objects.get(empire = self.empire, base_id = 'ships/colony-ship'),
            movable   = Movable.objects.create(position_x = 0, position_y = 0))

    def test_colonialize_intrasector(self):
        self.celestial2.habitated_by = self.empire
        self.celestial2.save()
        self.ship.delete()
        cost = self.ship.blueprint.data['cost']

        process = self.celestial1.colonialize(self.empire, movable = None)
        self.assertIsNone(self.celestial1.habitated_by)
        self.assertEqual(process.owner, self.empire)
        self.assertEqual(process.end_tick, self.world.now + cost)

        for _ in range(cost):
            self.assertTrue(Process.objects.filter(id = process.id).exists())
            self.world.tick()

        self.celestial1.refresh_from_db()
        self.celestial2.refresh_from_db()

        self.assertFalse(Process.objects.filter(id = process.id).exists())
        self.assertEqual(self.celestial1.habitated_by, self.empire)
        self.assertEqual(self.celestial2.habitated_by, self.empire)

    def test_colonialize_intrasector_already_habitated(self):
        self.ship.delete()
        self.celestial1.habitated_by = self.empire
        self.celestial2.habitated_by = self.empire
        self.celestial1.save()
        self.celestial2.save()
        self.assertRaises(AssertionError, lambda: self.celestial1.colonialize(self.empire, movable = None))

    def test_colonialize_intrasector_foreign(self):
        from game.models import Empire
        player2 = User.objects.create(username = 'testuser2', password = 'password')
        empire2 = Empire.objects.create(name = 'Bars', player = player2, origin_x = 0, origin_y = 0, color_hue = 0)

        self.ship.delete()
        self.celestial2.habitated_by = empire2
        self.celestial2.save()
        self.assertRaises(AssertionError, lambda: self.celestial1.colonialize(self.empire, movable = None))

    def test_colonialize_intersector(self):
        from game.models import Ship

        process = self.celestial1.colonialize(self.empire, self.ship.movable)
        self.assertIsNone(self.celestial1.habitated_by)
        self.assertIsNone(self.celestial2.habitated_by)
        self.assertEqual(process.owner, self.empire)
        self.assertEqual(process.end_tick, self.world.now + 1)

        self.world.tick()
        self.celestial1.refresh_from_db()
        self.celestial2.refresh_from_db()

        self.assertFalse(Process.objects.filter(id = process.id).exists())
        self.assertFalse(Movable.objects.filter(id = self.ship.movable.id).exists())
        self.assertFalse(Ship.objects.filter(id = self.ship.id).exists())
        self.assertEqual(self.celestial1.habitated_by, self.empire)
        self.assertIsNone(self.celestial2.habitated_by)
        self.assertTrue(self.sector.position in self.empire.territory)

    def test_colonialize_intersector_without_ship(self):
        self.ship.blueprint.base_id = 'ships/wrong-ship'
        self.ship.blueprint.save()
        self.assertRaises(AssertionError, lambda: self.celestial1.colonialize(self.empire, self.ship.movable))

    def test_colonialize_intersector_already_habitated(self):
        self.celestial1.habitated_by = self.empire
        self.assertRaises(AssertionError, lambda: self.celestial1.colonialize(self.empire, self.ship.movable))

    def test_colonialize_intersector_foreign(self):
        from game.models import Empire
        player2 = User.objects.create(username = 'testuser2', password = 'password')
        empire2 = Empire.objects.create(name = 'Bars', player = player2, origin_x = 0, origin_y = 0, color_hue = 0)

        self.celestial2.habitated_by = empire2
        self.celestial2.save()
        self.assertRaises(AssertionError, lambda: self.celestial1.colonialize(self.empire, self.ship.movable))


class HexSetTest(TestCase):

    def test_text(self):
        set1 = hexgrid.DistanceSet(( 1, 1), 1)
        set2 = hexgrid.DistanceSet((-1,-1), 2)
        union_set = hexgrid.Union([set1, set2])
        actual = union_set.text()
        expected = \
"""
  o o o  
 o o o o 
o o o o o
 o o o o 
  o o o o
     o o
"""
        self.assertEqual(normalize_hexset_text(actual), normalize_hexset_text(expected))


class DistanceSetTest(TestCase):

    def test_explicit(self):
        D1 = order_tuple_list([
            ( 0, 0),
            (-2, 0),
            (-1, 1),
            ( 1, 1),
            ( 2, 0),
            ( 1,-1),
            (-1,-1),
        ])
        D2 = order_tuple_list(D1 + [
            (-4, 0),
            (-3, 1),
            (-2, 2),
            ( 0, 2),
            ( 2, 2),
            ( 3, 1),
            ( 4, 0),
            ( 3,-1),
            ( 2,-2),
            ( 0,-2),
            (-2,-2),
            (-3,-1),
        ])
        D3 = order_tuple_list(D2 + [
            (-6, 0),
            (-5, 1),
            (-4, 2),
            (-3, 3),
            (-1, 3),
            ( 1, 3),
            ( 3, 3),
            ( 4, 2),
            ( 5, 1),
            ( 6, 0),
            ( 5,-1),
            ( 4,-2),
            ( 3,-3),
            ( 1,-3),
            (-1,-3),
            (-3,-3),
            (-4,-2),
            (-5,-1),
        ])
        self.assertSequenceEqual(order_tuple_list(hexgrid.DistanceSet((0,0), 1).explicit()), D1)
        self.assertSequenceEqual(order_tuple_list(hexgrid.DistanceSet((0,0), 2).explicit()), D2)
        self.assertSequenceEqual(order_tuple_list(hexgrid.DistanceSet((0,0), 3).explicit()), D3)


class UnionTest(TestCase):

    def setUp(self):
        self.set1 = hexgrid.DistanceSet(( 1, 1), 1)
        self.set2 = hexgrid.DistanceSet((-1,-1), 2)

    def test_explicit(self):
        make_set  = lambda items: frozenset([tuple(item) for item in items])
        union_set = hexgrid.Union([self.set1, self.set2])
        actual   = order_tuple_list(union_set.explicit())
        expected = order_tuple_list(make_set(self.set1.explicit()) | make_set(self.set2.explicit()))
        self.assertSequenceEqual(actual, expected)


class IntersectionTest(TestCase):

    def setUp(self):
        self.set1 = hexgrid.DistanceSet(( 1, 1), 1)
        self.set2 = hexgrid.DistanceSet((-1,-1), 2)

    def test_explicit(self):
        make_set  = lambda items: frozenset([tuple(item) for item in items])
        union_set = hexgrid.Intersection([self.set1, self.set2])
        actual   = order_tuple_list(union_set.explicit())
        expected = order_tuple_list(make_set(self.set1.explicit()) & make_set(self.set2.explicit()))
        self.assertSequenceEqual(actual, expected)


class graph_matrix_Test(TestCase):

    def setUp(self):
        self.set = hexgrid.DistanceSet((0,0), 1)

    def test_graph_matrix(self):
        G_actual = hexgrid.graph_matrix(self.set)
        hex_list = self.set.explicit()
        n = len(hex_list)
        I = {tuple(u): uidx for uidx, u in enumerate(hex_list)}
        G_expected = np.zeros((n, n), int)

        G_expected[I[(-2, 0)], I[(-1, 1)]] = 1
        G_expected[I[(-2, 0)], I[( 0, 0)]] = 1
        G_expected[I[(-2, 0)], I[(-1,-1)]] = 1

        G_expected[I[(-1, 1)], I[(-2, 0)]] = 1
        G_expected[I[(-1, 1)], I[( 0, 0)]] = 1
        G_expected[I[(-1, 1)], I[( 1, 1)]] = 1

        G_expected[I[( 1, 1)], I[(-1, 1)]] = 1
        G_expected[I[( 1, 1)], I[( 0, 0)]] = 1
        G_expected[I[( 1, 1)], I[( 2, 0)]] = 1

        G_expected[I[( 2, 0)], I[( 1, 1)]] = 1
        G_expected[I[( 2, 0)], I[( 0, 0)]] = 1
        G_expected[I[( 2, 0)], I[( 1,-1)]] = 1

        G_expected[I[( 1,-1)], I[( 2, 0)]] = 1
        G_expected[I[( 1,-1)], I[( 0, 0)]] = 1
        G_expected[I[( 1,-1)], I[(-1,-1)]] = 1

        G_expected[I[(-1,-1)], I[( 1,-1)]] = 1
        G_expected[I[(-1,-1)], I[( 0, 0)]] = 1
        G_expected[I[(-1,-1)], I[(-2, 0)]] = 1

        G_expected = (G_expected + G_expected.T).clip(0, 1) ## this is to add the reverse edges to (0,0)
        self.assertEqual(G_actual.tolist(), G_expected.tolist())


class ClusteringTest(TestCase):

    def test_labelmap(self):
        # Test strongly connected set
        set1 = hexgrid.DistanceSet(( 1, 1), 1)
        set2 = hexgrid.DistanceSet((-1,-1), 2)
        union_set = hexgrid.Union([set1, set2])
        c = hexgrid.Clustering(union_set)
        expected = \
"""
  0 0 0  
 0 0 0 0 
0 0 0 0 0
 0 0 0 0 
  0 0 0 0
     0 0
"""
        self.assertEqual(normalize_hexset_text(c.text()), normalize_hexset_text(expected))

        # Test weakly connected set
        set1 = hexgrid.DistanceSet((-2, 0), 1)
        set2 = hexgrid.DistanceSet(( 4, 0), 1)
        union_set = hexgrid.Union([set1, set2])
        c = hexgrid.Clustering(union_set)
        expected = \
"""
 0 0   1 1 
0 0 0 1 1 1
 0 0   1 1
"""
        self.assertEqual(normalize_hexset_text(c.text()), normalize_hexset_text(expected))

        # Test disconnected set
        set1 = hexgrid.DistanceSet((-2, 0), 2)
        set2 = hexgrid.DistanceSet(( 7, 1), 2)
        union_set = hexgrid.Union([set1, set2])
        c = hexgrid.Clustering(union_set)
        expected = \
"""
  0 0 0           
 0 0 0 0   1 1 1  
0 0 0 0 0 1 1 1 1 
 0 0 0 0 0 1 1 1 1
  0 0 0   1 1 1 1 
           1 1 1
"""
        self.assertEqual(normalize_hexset_text(c.text()), normalize_hexset_text(expected))
