from django.test import TestCase

from world.models import (
    World,
    Movable,
    hexmap,
)
from processes.models import (
    Process,
)


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


def order_tuple_list(items):
    return sorted([tuple(item) for item in items], key = lambda item: str(item))


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
