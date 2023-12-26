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


class HexSet:
    """
    Abstract representation of a set of hex fields.

    Realizations must implement the `__contains__` operator to test whether a hex field is contained.
    They also must implement the `bbox` method to obtain a bounding box of the set.
    """

    def __contains__(self, point):
        raise NotImplemented()

    def bbox(self):
        """
        Returns the bounding box of the set.

        :return: `(x_min, x_max, y_min, y_max)`
        """
        raise NotImplemented()

    def explicit(self):
        """
        Obtains explicit representation.
        """
        result = list()
        x_min, x_max, y_min, y_max = self.bbox()
        for q in np.ndindex(x_max - x_min + 1, y_max - y_min + 1):
            p = np.add((x_min, y_min), q)
            if np.sum(p) % 2 == 0 and p in self:
                result.append(p)
        return result


class DistanceSet(HexSet):
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

    def bbox(self):
        x_min, y_min = self.center[0] - 2 * self.radius, self.center[1] - self.radius
        x_max, y_max = self.center[0] + 2 * self.radius, self.center[1] + self.radius
        return x_min, x_max, y_min, y_max

    def __contains__(self, point):
        check_hex_coordinates(point)
        p = np.subtract(point, self.center)
        return all([p in H for H in self.halfspaces])


class Union(HexSet):

    def __init__(self, sets):
        self.sets = sets

    def bbox(self):
        """
        Returns the bounding box of the set (union of the bounding boxes).
        """
        x_min, y_min = [ np.inf] * 2
        x_max, y_max = [-np.inf] * 2
        for s in self.sets:
            bbox = s.bbox()
            x_min = min((x_min, bbox[0]))
            y_min = min((y_min, bbox[2]))
            x_max = max((x_max, bbox[1]))
            y_max = max((y_max, bbox[3]))
        return x_min, x_max, y_min, y_max

    def __contains__(self, point):
        return any([point in s for s in self.sets])


class Intersection(HexSet):

    def __init__(self, sets):
        self.sets = sets

    def bbox(self):
        """
        Returns the bounding box of the set (intersection of the bounding boxes).
        """
        x_min, y_min = [-np.inf] * 2
        x_max, y_max = [ np.inf] * 2
        for s in self.sets:
            bbox = s.bbox()
            x_min = max((x_min, bbox[0]))
            y_min = max((y_min, bbox[2]))
            x_max = min((x_max, bbox[1]))
            y_max = min((y_max, bbox[3]))
        return x_min, x_max, y_min, y_max

    def __contains__(self, point):
        return all([point in s for s in self.sets])


def graph_matrix(hexset):
    """
    Computes the adjacency graph matrix corresponding to the set of hex fields.

    :return: Tuple `G`, hex_list` where `G` is the matrix and `hex_list` is the list of nodes corresponding to the rows and columns of the matrix.
    """
    hex_list = hexset.explicit()
    I = {tuple(v): vidx for vidx, v in enumerate(hex_list)}
    n = len(hex_list)
    G = np.zeros((n, n), int)

    for i in range(n):
        u = hex_list[i]
        for v in Intersection([hexset, DistanceSet(u, 1)]).explicit():
            j = I[tuple(v)]
            if j <= i: continue
            G[i,j] = 1

    G = G + G.T
    return G, hex_list
