import functools
import gevent
from gevent.coros import Semaphore

class RateLimit(object):
    semaphore_class = Semaphore

    def __init__(self, *rates):
        self.semaphores = []
        self.links = []
        self.active = 0

        for rate in rates:
            num, units = rate.split('/')

            if units == 's': units = 1
            elif units == 'm': units = 60
            elif units == 'h': units = 60*60
            else: units = float(units)

            self.semaphores.append((units, self.semaphore_class(int(num))))

        if not rates:
            self.delay = lambda: None
            self.release = lambda: None

    def delay(self):
        self.active += 1

        for units, semaphore in self.semaphores:
            semaphore.acquire()

    def rawlink(self, func, *args, **kwargs):
        self.links.append(functools.partial(func, *args, **kwargs)

    def timeout(self, semaphore):
        semaphore.release()

        if self.links and self.active == 0:
            for link in self.links:
                link()

    def release(self):
        for units, semaphore in self.semaphores:
            #gevent.spawn_later(units, semaphore.release)
            gevent.spawn_later(units, self.timeout, semaphore)

        self.active -= 1

    def __call__(self, func):
        def _ratelimit(*args, **kwargs):
            self.delay()
            try:
                return func(*args, **kwargs)
            finally:
                self.release()
        return _ratelimit

    def __enter__(self):
        self.delay()
        return self

    def __exit__(self, type, value, traceback):
        self.release()

class BoundedRateLimit(RateLimit):
    semaphore_class = BoundedSemaphore

class MultiRateLimit(object):
    ratelimit_class = RateLimit

    def __init__(self, *rates):
        self.ratelimits = {}
        self.rates = rates

    def key(self, k):
        if not k in self.ratelimits:
            self.ratelimits[k] = self.ratelimit_class(*self.rates)
            self.ratelimits[k].rawlink(self.cleanup, k)

        return self.ratelimits[k]

    def cleanup(self, k):
        del self.ratelimits[k]

class BoundedMultiRateLimit(MultiRateLimit):
    ratelimit_class = BoundedRateLimit
