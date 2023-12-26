from django.db import models

from world import hexmap


class Empire(models.Model):

    name = models.CharField(max_length = 100)

    @property
    def habitated_sectors(self):
        from world.models import Sector
        return Sector.objects.filter(celestial_set__habitated_by = self.id)

    @property
    def territory(self):
        atoms = list()
        for sector in habitated_sectors:
            atom = hexmap.DistanceSet(center = sector.position, radius = 1)
            atoms.append(atom)
        return hexmap.Union(atoms)
