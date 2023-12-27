from django.test import TestCase
import numpy as np

from world.models import (
    World,
    Movable,
    hexmap,
)
from processes.models import (
    Process,
)

from tools.testtools import order_tuple_list


class MovableTest(TestCase):

    def setUp(self):
        self.world = World.objects.create()
        self.movable = Movable.objects.create(
            position_x = 0,
            position_y = 0)

    def test_next_position(self):
        self.movable.move_to(self.world, (2,2))
        self.assertSequenceEqual(self.movable.next_position.tolist(), (1,1))

    def test_move_to_speed1(self):
        self.movable.custom_speed = 1
        self.movable.save()

        # Move (0,0) -> (1,1) -> (2,2) 
        self.movable.move_to(self.world, (2,2))
        self.assertSequenceEqual(self.movable.position.tolist(), (0,0))
        self.world.tick()
        self.movable.refresh_from_db()
        self.assertSequenceEqual(self.movable.position.tolist(), (1,1))
        self.world.tick()
        self.movable.refresh_from_db()
        self.assertSequenceEqual(self.movable.position.tolist(), (2,2))
        self.assertEqual(len(Process.objects.all()), 0)

        # Move (2,2) -> (1,1) or (3,1) -> (2,0) 
        self.movable.move_to(self.world, (2,0))
        self.assertSequenceEqual(self.movable.position.tolist(), (2,2))
        self.world.tick()
        self.movable.refresh_from_db()
        self.assertIn(self.movable.position.tolist(), [[1,1], [3,1]])
        self.world.tick()
        self.movable.refresh_from_db()
        self.assertSequenceEqual(self.movable.position.tolist(), (2,0))
        self.assertEqual(len(Process.objects.all()), 0)

        # Don't move 
        self.world.tick()
        self.movable.refresh_from_db()

        # Move (2,0) -> (0,0) -> (-2,0)
        self.movable.move_to(self.world, (-2,0))
        self.assertSequenceEqual(self.movable.position.tolist(), (2,0))
        self.world.tick()
        self.movable.refresh_from_db()
        self.assertSequenceEqual(self.movable.position.tolist(), (0,0))
        self.world.tick()
        self.movable.refresh_from_db()
        self.assertSequenceEqual(self.movable.position.tolist(), (-2,0))
        self.assertEqual(len(Process.objects.all()), 0)

        # Order to move to (2,0), but immediately change to (-1,1)
        self.movable.move_to(self.world, (2,0))
        self.movable.move_to(self.world, (-1,1))
        self.assertEqual(len(Process.objects.all()), 1)
        self.world.tick()
        self.movable.refresh_from_db()
        self.assertSequenceEqual(self.movable.position.tolist(), (-1,1))
        self.assertEqual(len(Process.objects.all()), 0)

    def test_move_to_speed2(self):
        self.movable.custom_speed = 2
        self.movable.save()

        # Move (0,0) -> (2,2) 
        self.movable.move_to(self.world, (2,2))
        self.assertSequenceEqual(self.movable.position.tolist(), (0,0))
        self.world.tick()
        self.movable.refresh_from_db()
        self.assertSequenceEqual(self.movable.position.tolist(), (2,2))
        self.assertEqual(len(Process.objects.all()), 0)

    def test_move_to_speed0(self):
        self.movable.custom_speed = 0.5
        self.movable.save()

        # Move (0,0) -> (1,1) 
        self.movable.move_to(self.world, (1,1))
        self.assertSequenceEqual(self.movable.position.tolist(), (0,0))
        self.world.tick()
        self.movable.refresh_from_db()
        self.assertSequenceEqual(self.movable.position.tolist(), (0,0))
        self.world.tick()
        self.movable.refresh_from_db()
        self.assertSequenceEqual(self.movable.position.tolist(), (1,1))
        self.assertEqual(len(Process.objects.all()), 0)


class HexSetTest(TestCase):

    def test_text(self):
        set1 = hexmap.DistanceSet(( 1, 1), 1)
        set2 = hexmap.DistanceSet((-1,-1), 2)
        union_set = hexmap.Union([set1, set2])
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
        self.assertEqual(actual, expected.strip())


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
        self.assertSequenceEqual(order_tuple_list(hexmap.DistanceSet((0,0), 1).explicit()), D1)
        self.assertSequenceEqual(order_tuple_list(hexmap.DistanceSet((0,0), 2).explicit()), D2)
        self.assertSequenceEqual(order_tuple_list(hexmap.DistanceSet((0,0), 3).explicit()), D3)


class UnionTest(TestCase):

    def setUp(self):
        self.set1 = hexmap.DistanceSet(( 1, 1), 1)
        self.set2 = hexmap.DistanceSet((-1,-1), 2)

    def test_explicit(self):
        make_set  = lambda items: frozenset([tuple(item) for item in items])
        union_set = hexmap.Union([self.set1, self.set2])
        actual   = order_tuple_list(union_set.explicit())
        expected = order_tuple_list(make_set(self.set1.explicit()) | make_set(self.set2.explicit()))
        self.assertSequenceEqual(actual, expected)


class IntersectionTest(TestCase):

    def setUp(self):
        self.set1 = hexmap.DistanceSet(( 1, 1), 1)
        self.set2 = hexmap.DistanceSet((-1,-1), 2)

    def test_explicit(self):
        make_set  = lambda items: frozenset([tuple(item) for item in items])
        union_set = hexmap.Intersection([self.set1, self.set2])
        actual   = order_tuple_list(union_set.explicit())
        expected = order_tuple_list(make_set(self.set1.explicit()) & make_set(self.set2.explicit()))
        self.assertSequenceEqual(actual, expected)


class hexmap_Test(TestCase):

    def setUp(self):
        self.set = hexmap.DistanceSet((0,0), 1)

    def test_graph_matrix(self):
        G_actual, hex_list = hexmap.graph_matrix(self.set)
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
