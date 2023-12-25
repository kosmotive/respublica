"""
Implements the hexagon map logics.

We use the following coordinate system:
https://github.com/stephanh42/hexutil/raw/master/img/hexcoords.png

See for more info: https://github.com/stephanh42/hexutil

This implies the following adjacencies:
```
u ~ v  iff  |d.y| ≤ 1  or  |d.x| ≤ 2
```
"""

from django.db import models

import numpy as np


class World(models.Model):

    now = models.PositiveBigIntegerField(default = 0)

    def tick(self):
        self.now += 1
        self.save()

        from processes.models import Process
        for process in [process for process in Process.objects.filter(end_tick = self.now)]:
            process.handler.finish(process)


def _check_hex_coordinates(c):
    assert np.sum(c) % 2 == 0, f'hex coordinates {tuple(c)} are invalid'


class Positionable(models.Model):

    position_x = models.IntegerField()
    position_y = models.IntegerField()

    def set_position(self, position):
        """
        Immediately changes the position of this object.
        """
        _check_hex_coordinates(position)

        self.position_x = position[0]
        self.position_y = position[1]

    @property
    def position(self):
        return np.asarray((self.position_x, self.position_y), dtype=int)


class Movable(Positionable):

    destination_x = models.IntegerField(null = True)
    destination_y = models.IntegerField(null = True)

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
        _check_hex_coordinates(destination)

        self.destination_x = destination[0]
        self.destination_y = destination[1]
        self.save()

        from processes.models import MovementHandler
        MovementHandler.create_process(world.now, self)

    @property
    def speed(self):
        return 1

    @property
    def destination(self):
        if self.destination_x is None or self.destination_y is None:
            return self.position
        else:
            return np.asarray((self.destination_x, self.destination_y), dtype=int)

    @property
    def next_position(self):
        u = self.position
        v = np.asarray(self.destination, dtype=int)
        _check_hex_coordinates(u)
        _check_hex_coordinates(v)
        d = v - u
        d = d.clip(-2, +2)
        if abs(d[1]) >= 1:
            d = d.clip(-1, +1)
            if np.sum(u + d) % 2 == 1: d[0] -= 1
        _check_hex_coordinates(u + d)
        return u + d


class Sector(Positionable):

    name = models.CharField(max_length = 50, unique = True)


class Celestial(models.Model):

    sector   = models.ForeignKey('Sector', on_delete = models.CASCADE)
    position = models.PositiveSmallIntegerField()
    features = models.JSONField()
