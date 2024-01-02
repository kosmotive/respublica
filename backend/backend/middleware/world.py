from django.db.utils import OperationalError

from world.models import World


class WorldTickMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        world = World.objects.get()
        world.do_pending_ticks()
        return self.get_response(request)
