import time
import random

from django.conf import settings


class SimulNetworkJitter:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if settings.SIMUL_NETWORK_JITTER:
            random.seed(time.time())
            time.sleep(random.uniform(0, 1))
            ret = self.get_response(request)
            time.sleep(random.uniform(0, 1))
            return ret
        else:
            return self.get_response(request)
