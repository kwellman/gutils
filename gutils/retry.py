import logging
import gevent

class Retry(object):
    def __init__(self, tries=3, delay=None, exceptions=[]):
        assert isinstance(tries, int), 'tries must be an integer'
        assert tries > 0, 'tries must larger than 0'

        self.tries = tries
        self.exceptions = exceptions
        self.delay = delay

    def __call__(self, func):
        def _retry(*args, **kwargs):
            for i in xrange(self.tries):
                try:
                    return func(*args, **kwargs)
                except Exception, e:
                    logging.exception('Retry')

                    if self.exceptions and not e in self.exceptions:
                        raise

                    if self.delay and not i+1 == self.tries:
                        gevent.sleep(self.delay)

            else:
                raise e

        return _retry

class ExponentialRetry(Retry):
    def __init__(self, tries=3, delay=None, backoff=2, truncate=None,
                 exceptions=[]):
        self.backoff = backoff
        self.truncate = truncate
        Retry.__init__(self, tries, delay, exceptions)

    def __call__(self, func):
        def _retry(*args, **kwargs):
            delay = self.delay

            for i in xrange(self.tries):
                try:
                    return func(*args, **kwargs)
                except Exception, e:
                    logging.exception('Retry')

                    if self.exceptions and not e in self.exceptions:
                        raise

                    if delay and not i+1 == self.tries:
                        gevent.sleep(delay)

                        if self.truncate and delay >= self.truncate:
                            delay = self.truncate
                        else:
                            delay *= self.backoff

            else:
                raise e

        return _retry

class InfiniteRetry(object):
    def __init__(self, delay=None, backoff=1, truncate=None, exceptions=[]):
        self.delay = delay
        self.backoff = backoff
        self.truncate = truncate
        self.exceptions = exceptions

    def __call__(self, func):
        def _retry(*args, **kwargs):
            delay = self.delay

            while True:
                try:
                    return func(*args, **kwargs)
                except Exception, e:
                    logging.exception('Retry')

                    if self.exceptions and not e in self.exceptions:
                        raise

                    if delay:
                        gevent.sleep(delay)

                        if self.truncate and delay >= self.truncate:
                            delay = self.truncate
                        else:
                            delay *= self.backoff

        return _retry

