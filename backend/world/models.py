import time
import multiprocessing

from django.db import models, transaction
from django.db.models import CheckConstraint, Q
from django.db.models.signals import post_delete
from django.dispatch import receiver
import numpy as np

from . import hexgrid
from . import git


# Lock used to synchronize `world.do_pending_ticks` within a single process (transactions should prevent race conditions across processes)
_world_lock = multiprocessing.Lock()


class World(models.Model):

    now = models.PositiveBigIntegerField(default = 0)
    last_tick_timestamp = models.PositiveBigIntegerField(null = True)
    tickrate = models.FloatField(default = 0)
    version  = models.JSONField(null = True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                name = 'world_singleton',
                check = models.Q(id = 1),
            ),
        ]

    def tick(self):
        self.now += 1
        self.last_tick_timestamp = round(time.time())
        self.save()

        from processes.models import Process
        for process in [process for process in Process.objects.filter(end_tick = self.now)]:
            process.handler.finish(process)

    @property
    def seconds_between_ticks(self):
        return np.inf if self.tickrate == 0 else round(60 ** 2 // self.tickrate)

    @property
    def seconds_passed_since_last_tick(self):
        return round(time.time()) - self.last_tick_timestamp

    @property
    def pending_ticks(self):
        pending_ticks = self.seconds_passed_since_last_tick // self.seconds_between_ticks
        assert isinstance(pending_ticks, int)
        return pending_ticks

    @transaction.atomic()
    def do_pending_ticks(self):
        _world_lock.acquire()
        try:
            for _ in range(self.pending_ticks):
                self.tick()
        finally:
            _world_lock.release()

    @property
    def remaining_seconds(self):
        return int(self.seconds_between_ticks - self.seconds_passed_since_last_tick)

    def save(self, *args, **kwargs):
        assert self.seconds_between_ticks > 1

        is_newly_created = (self.now < 1)
        super(World, self).save(*args, **kwargs)

        # If the world is newly created, then do an initial tick to initialize the fields
        if is_newly_created:
            self.version = git.get_head_info()
            self.tick()


class Positionable(models.Model):

    position_x = models.IntegerField()
    position_y = models.IntegerField()

    class Meta:
        abstract = True  ## do not create a table for this class

    def set_position(self, position):
        """
        Immediately changes the position of this object.
        """
        hexgrid.check_hex_coordinates(position)

        self.position_x = position[0]
        self.position_y = position[1]

    @property
    def position(self):
        return np.asarray((self.position_x, self.position_y), dtype=int)


class Movable(Positionable):

    destination_x = models.IntegerField(null = True)
    destination_y = models.IntegerField(null = True)

    custom_speed = models.FloatField(null = True, default = None)
    name = models.CharField(max_length = 50, default = 'Unnamed');

    class Meta:
        constraints = [
                CheckConstraint(
                    check = Q(custom_speed__isnull=True) | Q(custom_speed__gt=0.0),
                    name='custom_speed null or negative')
            ]

    def set_position(self, position):
        """
        Immediately changes the position of this object.
        """
        Positionable.set_position(self, position)

        if (self.position == self.destination).all():
            self.destination_x = None
            self.destination_y = None

        self.save()

        # Unveil the neighborhood
        if self.owner is not None:
            Unveiled.unveil(self.owner, self.position, 1)

    def move_to(self, destination):
        hexgrid.check_hex_coordinates(destination)

        self.destination_x = destination[0]
        self.destination_y = destination[1]
        self.save()

        from processes.models import MovementHandler
        return MovementHandler.create_process(World.objects.get().now, self)

    @property
    def speed(self):
        if self.custom_speed is None:
            assert self.ship_set.count() > 0
            slowest_ship = self.ship_set.order_by('blueprint__data__speed')[0]
            return slowest_ship.blueprint.data['speed']
        else:
            return self.custom_speed

    @property
    def destination(self):
        if self.destination_x is None or self.destination_y is None:
            return self.position
        else:
            return np.asarray((self.destination_x, self.destination_y), dtype=int)

    @property
    def next_position(self):
        return hexgrid.get_next_position_towards(self.position, self.destination, self.speed)

    @property
    def trajectory(self):
        return hexgrid.get_trajectory_towards(self.position, self.destination, self.speed)

    @property
    def owner(self):
        if self.ship_set.count() == 0: return None
        return self.ship_set.all()[0].owner

    @property
    def process(self):
        from processes.models import Process
        try:
            return Process.objects.get(data__movable_id = self.id)
        except Process.DoesNotExist:
            return None

    @receiver(post_delete, sender = 'game.Ship')
    def delete_if_empty(sender, instance, **kwargs):
        if instance.movable.ship_set.count() == 0:
            instance.movable.delete()


class Sector(Positionable):

    name = models.CharField(max_length = 50, unique = True)

    def feature(self, feature_name, accumulation='sum'):
        values = [c.features[feature_name] for c in self.celestial_set.all() if feature_name in c.features]
        acc_func = eval(accumulation)
        return acc_func(values)

    def __str__(self):
        return f'{self.name} (x={self.position_x} y={self.position_y}, capacity: {self.feature("capacity")})'

    @property
    def process(self):
        from processes.models import Process
        processes = Process.objects.filter(data__celestial_id__in = self.celestial_set.values_list('id', flat=True))
        if processes.count() == 1:
            return processes[0]
        else:
            assert processes.count() == 0


class Celestial(models.Model):

    sector   = models.ForeignKey('Sector', on_delete = models.CASCADE)
    position = models.PositiveSmallIntegerField()
    features = models.JSONField()
    habitated_by = models.ForeignKey('game.Empire', on_delete = models.SET_NULL, related_name = 'habitat', null = True, default = None)

    @property
    def capacity(self):
        return self.features.get('capacity', 0)

    @property
    def remaining_capacity(self):
        occupied_capacity = sum((c.blueprint.data.get('size') for c in self.construction_set.all()))
        return self.capacity - occupied_capacity

    def colonialize(self, empire, movable):
        from processes.models import ColonializationHandler
        return ColonializationHandler.create_process(World.objects.get().now, empire, self, movable)


class Unveiled(Positionable):

    by_whom = models.ForeignKey('game.Empire', on_delete = models.CASCADE, related_name = 'unveiled')

    class Meta:
        unique_together = ('position_x', 'position_y', 'by_whom')

    @staticmethod
    def unveil(empire, center, radius):
        ds = hexgrid.DistanceSet(center, radius)
        for c in ds.explicit():
            Unveiled.objects.update_or_create(
                position_x = c[0],
                position_y = c[1],
                by_whom = empire)
