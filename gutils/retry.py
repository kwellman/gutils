import logging

class Retry(object):
    def __init__(self, tries=3, exceptions=[]):
        assert isinstance(tries, int), 'tries must be an integer'
        assert tries > 0, 'tries must larger than 0'

        self.tries = 3
        self.exceptions = exceptions

    def __call__(self, func):
        def _retry(*args, **kwargs):
            for i in range(self.tries):
                try:
                    return func(*args, **kwargs)
                except Exception, e:
                    logging.exception('Retry')

                    if self.exceptions:
                        if e in self.exceptions:
                            continue
                        raise
                    else:
                        continue
            else:
                raise e

        return _retry
