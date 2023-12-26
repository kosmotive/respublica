from django.db import models

from world import hexmap
from game.blueprints import base_blueprints


class Empire(models.Model):

    name = models.CharField(max_length = 100)

    @property
    def habitated_sectors(self):
        from world.models import Sector
        return Sector.objects.filter(celestial__habitated_by = self.id)

    @property
    def territory(self):
        atoms = list()
        for sector in self.habitated_sectors:
            atom = hexmap.DistanceSet(center = sector.position, radius = 1)
            atoms.append(atom)
        return hexmap.Union(atoms)

    def save(self, *args, **kwargs):
        is_newly_created = not self.pk
        super(Empire, self).save(*args, **kwargs)

        # If the empire is newly created, then also create its base blueprints
        if is_newly_created:
            for base_id in base_blueprints:
                Blueprint.objects.create(
                    base_id = base_id,
                    empire = self)


class Blueprint(models.Model):

    base_id = models.CharField(max_length = 100)
    empire = models.ForeignKey('Empire', on_delete = models.CASCADE)

    @property
    def base(self):
        bp_type, bp_name = self.base_id.split('/')
        return base_blueprints[bp_type][bp_name]

    @property
    def cost(self):
        return self.base.cost

    @property
    def size(self):
        return self.base.size


class Construction(models.Model):

    blueprint = models.ForeignKey('Blueprint', on_delete = models.PROTECT)
    celestial = models.ForeignKey('world.Celestial', on_delete = models.CASCADE)
