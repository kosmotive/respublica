from django.db import models


class Process(models.Model):

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
        from world.models import Movable

        movable = Movable.objects.get(id = process.data['movable_id'])
        movable.set_position(movable.next_position)

        if (movable.destination == movable.position).all():
            process.delete()
        else:
            process.start_tick = process.end_tick
            process.end_tick = process.start_tick + max((1, int(1 / movable.speed)))
            process.save()

    @staticmethod
    def create_process(start_tick, movable):
        Process.objects.filter(data__movable_id = movable.id).delete()
        Process.objects.create(
            start_tick = start_tick,
            end_tick = start_tick + max((1, int(1 / movable.speed))),
            handler_id = MovementHandler.__qualname__,
            data = dict(movable_id = movable.id))
