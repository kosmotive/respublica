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

import numpy as np


def check_hex_coordinates(c):
    assert np.sum(c) % 2 == 0, f'hex coordinates {tuple(c)} are invalid'


class Halfspace:

    def __init__(self, normal, distance, normalize=False):
        self.normal = (normal / np.linalg.norm(normal)) if normalize else normal
        self.distance = distance

    def __contains__(self, point):
        return np.dot(self.normal, point) <= self.distance


class DistanceSet:
    """
    Sub-level set of the distance function on the hexagon map (offset by radius).

    Implemented using an implicit representation of the set.
    """

    def __init__(self, center, radius):
        self.center = center
        self.radius = radius

        # The resulting set is a hexagon, that is a convex polygon (or intersection of halfspaces)
        self.halfspaces = [
            Halfspace(normal = (-1, 1), distance = self.radius * 2), ## top-left edge
            Halfspace(normal = ( 0, 1), distance = self.radius),     ## top edge
            Halfspace(normal = ( 1, 1), distance = self.radius * 2), ## top-right edge
            Halfspace(normal = ( 1,-1), distance = self.radius * 2), ## bottom-right edge
            Halfspace(normal = ( 0,-1), distance = self.radius),     ## bottom edge
            Halfspace(normal = (-1,-1), distance = self.radius * 2), ## bottom-left edge
        ]

    def __contains__(self, point):
        check_hex_coordinates(point)
        p = np.subtract(point, self.center)
        return all([p in H for H in self.halfspaces])

    def explicit(self):
        """
        Obtains explicit representation.
        """
        result = list()
        x_min, y_min = self.center[0] - 2 * self.radius, self.center[1] - self.radius
        x_max, y_max = self.center[0] + 2 * self.radius, self.center[1] + self.radius
        for q in np.ndindex(x_max - x_min + 1, y_max - y_min + 1):
            p = np.add((x_min, y_min), q)
            if np.sum(p) % 2 == 0 and p in self:
                result.append(p)
        return result
