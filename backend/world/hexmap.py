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
    """

    def __init__(self, center, radius):
        self.center = center
        self.radius = radius

    def explicit(self):
        """
        Obtains explicit representation.
        """

        # The resulting set is a hexagon, that is a convex polygon (or intersection of halfspaces)
        halfspaces = [
            Halfspace(normal = (-1, 1), distance = self.radius * 2), ## top-left edge
            Halfspace(normal = ( 0, 1), distance = self.radius),     ## top edge
            Halfspace(normal = ( 1, 1), distance = self.radius * 2), ## top-right edge
            Halfspace(normal = ( 1,-1), distance = self.radius * 2), ## bottom-right edge
            Halfspace(normal = ( 0,-1), distance = self.radius),     ## bottom edge
            Halfspace(normal = (-1,-1), distance = self.radius * 2), ## bottom-left edge
        ]
        
        result = list()
        for dx in range(-2 * self.radius, 2 * self.radius + 1):
            for dy in range(-self.radius, self.radius + 1):
                p = (self.center[0] + dx, self.center[1] + dy)
                if np.sum(p) % 2 == 0 and all([(dx, dy) in H for H in halfspaces]):
                    result.append(p)
        return result
