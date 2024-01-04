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
            end_tick   = start_tick + blueprint.data['cost'],
            owner      = celestial.habitated_by,
            handler_id = BuildingHandler.__qualname__,
            data = dict(
                blueprint_id = blueprint.id,
                celestial_id = celestial.id))


class ColonizationHandler(BaseHandler):
    """
    Habitates a celestial when the colonization process completes.

    Requires either another already habitated celestial or a colony ship in the same sector as the colonized celestial.
    """

    def finish(self, process):
        from world.models import Celestial
        from game.models import Empire

        # Spawn the colony
        celestial = Celestial.objects.get(id = process.data['celestial_id'])
        empire    = Empire   .objects.get(id = process.data[   'empire_id'])
        assert celestial.habitated_by is None
        celestial.habitated_by = empire
        celestial.save()

        # Delete the process
        process.delete()

        # Consume the colony ship, if one was used
        if self.movable(process) is not None:
            ships_qs = self.movable(process).ship_set.filter(blueprint__base_id = 'ships/colony-ship')
            assert ships_qs.count() >= 1
            ships_qs[0].delete()

    def movable(self, process):
        from world.models import Movable
        movable_id = process.data.get('movable_id', None)
        if movable_id is None:
            return None
        else:
            return Movable.objects.get(id = movable_id)

    @staticmethod
    def create_process(start_tick, empire, celestial, movable):
        from game.models import Blueprint, Empire
        data = dict(
            celestial_id = celestial.id,
            empire_id    = empire.id)

        # Ensure that the celestial is not colonized yet
        assert celestial.habitated_by is None

        # Ensure that no other celestial in the same sector is colonized by a different empire
        assert all((c.habitated_by is None or c.habitated_by == empire for c in celestial.sector.celestial_set.all()))

        # Ensure that the celestial is not in the territory of a different empire
        assert all((celestial.sector.position not in e.territory for e in Empire.objects.all() if e.id != empire.id))

        # Cancel any previous build process in the sector
        process = celestial.sector.process
        if process is not None:
            process.handler.cancel(process)

        # Cancel any previous order of the movable (if a colony ship is used)
        if movable is not None:
            assert (movable.position == celestial.sector.position).all()
            assert  movable.owner.id == empire.id
            assert  movable.ship_set.filter(blueprint__base_id = 'ships/colony-ship').count() >= 1
            Process.objects.filter(data__movable_id = movable.id).delete()
            data['movable_id'] = movable.id

        # Determine how long it is gonna take (1 tick for colony ships, or the cost of the cheapest available colony ship otherwise)
        if movable is not None:
            cost = 1
        else:
            qs = Blueprint.objects.filter(
                empire  = empire,
                base_id = 'ships/colony-ship').order_by('data__cost')
            cost = qs[0].data['cost']

        # Spawn the process
        return Process.objects.create(
            start_tick = start_tick,
            end_tick   = start_tick + cost,
            owner      = empire,
            handler_id = ColonizationHandler.__qualname__,
            data       = data)
