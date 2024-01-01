from django.db import models


class Process(models.Model):

    owner      = models.ForeignKey('game.Empire', related_name = 'processes', on_delete = models.SET_NULL, null = True)
    start_tick = models.PositiveBigIntegerField()
    end_tick   = models.PositiveBigIntegerField()
    data       = models.JSONField()
    handler_id = models.CharField(max_length = 200)

    @property
    def handler(self):
        handler_cls = eval(self.handler_id)
        return handler_cls()


class BaseHandler:

    def finish(self, process):
        process.delete()

    def cancel(self, process):
        process.delete()


class MovementHandler(BaseHandler):
    """
    Updates the position of a Movable to the next position towards its destination after time spent corresponding to its speed.
    """

    def finish(self, process):
        movable = self.movable(process)
        movable.set_position(movable.next_position)

        if (movable.destination == movable.position).all():
            process.delete()
        else:
            process.start_tick = process.end_tick
            process.end_tick = process.start_tick + max((1, int(1 / movable.speed)))
            process.save()

    def cancel(self, process):
        movable = self.movable(process)

        # The method `move_to` calls `MovementHandler.create_process` which deletes the process
        movable.move_to(movable.position)

    def movable(self, process):
        from world.models import Movable
        return Movable.objects.get(id = process.data['movable_id'])

    @staticmethod
    def create_process(start_tick, movable):
        Process.objects.filter(data__movable_id = movable.id).delete()
        if (movable.destination == movable.position).all():
            return None
        return Process.objects.create(
            start_tick = start_tick,
            end_tick   = start_tick + max((1, int(1 / movable.speed))),
            owner      = movable.owner,
            handler_id = MovementHandler.__qualname__,
            data = dict(movable_id = movable.id))


class BuildingHandler(BaseHandler):
    """
    Spawns a Construction or Ship when the building process completes.
    """

    def finish(self, process):
        from world.models import Celestial, Movable
        from game.models import Blueprint, Construction, Ship
        celestial = Celestial.objects.get(id = process.data['celestial_id'])
        blueprint = Blueprint.objects.get(id = process.data['blueprint_id'])
        if blueprint.base_id.startswith('constructions/'):
            Construction.objects.create(
                blueprint = blueprint,
                celestial = celestial)
        elif blueprint.base_id.startswith('ships/'):
            Ship.objects.create(
                blueprint = blueprint,
                movable   = Movable.objects.create(position_x = celestial.sector.position_x, position_y = celestial.sector.position_y))
        else:
            raise ValueError(f'invalid blueprint {blueprint.id} with base_id: "{blueprint.base_id}"')
        process.delete()

    @staticmethod
    def create_process(start_tick, blueprint, celestial):
        process = celestial.sector.process
        if process is not None:
            process.handler.cancel(process)
        return Process.objects.create(
            start_tick = start_tick,
            end_tick   = start_tick + blueprint.cost,
            owner      = celestial.habitated_by,
            handler_id = BuildingHandler.__qualname__,
            data = dict(
                blueprint_id = blueprint.id,
                celestial_id = celestial.id))
