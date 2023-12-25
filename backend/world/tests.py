from django.test import TestCase
from world.models import (
    World,
    Movable,
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

    def test_move_to(self):
        self.movable.move_to(self.world, (2,2))
        self.assertSequenceEqual(self.movable.position.tolist(), (0,0))
        self.world.tick()
        self.movable.refresh_from_db()
        self.assertSequenceEqual(self.movable.position.tolist(), (1,1))
        self.world.tick()
        self.movable.refresh_from_db()
        self.assertSequenceEqual(self.movable.position.tolist(), (2,2))
        self.assertEqual(len(Process.objects.all()), 0)

        self.movable.move_to(self.world, (2,0))
        self.assertSequenceEqual(self.movable.position.tolist(), (2,2))
        self.world.tick()
        self.movable.refresh_from_db()
        self.assertIn(self.movable.position.tolist(), [[1,1], [3,1]])
        self.world.tick()
        self.movable.refresh_from_db()
        self.assertSequenceEqual(self.movable.position.tolist(), (2,0))
        self.assertEqual(len(Process.objects.all()), 0)

        self.world.tick()
        self.movable.refresh_from_db()

        self.movable.move_to(self.world, (-2,0))
        self.assertSequenceEqual(self.movable.position.tolist(), (2,0))
        self.world.tick()
        self.movable.refresh_from_db()
        self.assertSequenceEqual(self.movable.position.tolist(), (0,0))
        self.world.tick()
        self.movable.refresh_from_db()
        self.assertSequenceEqual(self.movable.position.tolist(), (-2,0))
        self.assertEqual(len(Process.objects.all()), 0)
