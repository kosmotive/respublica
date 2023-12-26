import math

from django.db import models
from django.db.models import CheckConstraint, Q
import numpy as np

from . import hexmap


class World(models.Model):

    now = models.PositiveBigIntegerField(default = 0)

    def tick(self):
        self.now += 1
        self.save()

        from processes.models import Process
        for process in [process for process in Process.objects.filter(end_tick = self.now)]:
            process.handler.finish(process)


class Positionable(models.Model):

    position_x = models.IntegerField()
    position_y = models.IntegerField()

    def set_position(self, position):
        """
        Immediately changes the position of this object.
        """
        hexmap.check_hex_coordinates(position)

        self.position_x = position[0]
        self.position_y = position[1]

    @property
    def position(self):
        return np.asarray((self.position_x, self.position_y), dtype=int)


class Movable(Positionable):

    destination_x = models.IntegerField(null = True)
    destination_y = models.IntegerField(null = True)

    custom_speed = models.FloatField(null = True, default = None)

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

    def move_to(self, world, destination):
        hexmap.check_hex_coordinates(destination)

        self.destination_x = destination[0]
        self.destination_y = destination[1]
        self.save()

        from processes.models import MovementHandler
        MovementHandler.create_process(world.now, self)

    @property
    def speed(self):
        return 1 if self.custom_speed is None else self.custom_speed

    @property
    def destination(self):
        if self.destination_x is None or self.destination_y is None:
            return self.position
        else:
            return np.asarray((self.destination_x, self.destination_y), dtype=int)

    @property
    def next_position(self):
        u = self.position
        hexmap.check_hex_coordinates(u)
        for _ in range(math.ceil(self.speed)):
            v = np.asarray(self.destination, dtype=int)
            hexmap.check_hex_coordinates(v)
            d = v - u
            d = d.clip(-2, +2)
            if abs(d[1]) >= 1:
                d = d.clip(-1, +1)
                if np.sum(u + d) % 2 == 1: d[0] -= 1
            u += d
            hexmap.check_hex_coordinates(u)
        return u


class Sector(Positionable):

    name = models.CharField(max_length = 50, unique = True)

    def feature(self, feature_name, accumulation='sum'):
        values = [c.features[feature_name] for c in self.celestial__set.all() if feature_name in c.features]
        acc_func = eval(accumuluation)
        return acc_func(values)

    def __str__(self):
        return f'{name} (x={self.position_x} y={self.position_y}, capacity: {self.feature("capacity")})'


class Celestial(models.Model):

    sector   = models.ForeignKey('Sector', on_delete = models.CASCADE)
    position = models.PositiveSmallIntegerField()
    features = models.JSONField()
    habitated_by = models.ForeignKey('game.Empire', on_delete = models.SET_NULL, null = True, default = None)