import time
from pymongo import Connection

class Cache(object):
    """A function decorator that memoizes return value in db cache.
    * Up to the user to remove expired cache items.
    * Only works on class member functions.
    * Function must be called with keyword arguments only.
    """
    @classmethod
    def initialize(
            cls,
            database='cache',
            collection='results',
            ttl=10):

        cls.database = database
        cls.collection = collection
        cls.ttl = ttl

        cls.coll = Connection()[database][collection]

    def clean_cache(self, cutoff=None):
        if cutoff is None:
            cutoff = time.time()

        self.coll.remove({'expiry': {'$lt': cutoff}})

    def __init__(self, keyfunc, ttl=None):
        self.keyfunc = keyfunc

        if ttl is None:
            self.ttl = Cache.ttl
        else:
            self.ttl = ttl

    def __call__(self, prefix='', ttl=None):
        if callable(prefix):
            func = prefix
            prefix = ''
        else:
            func = None

        if ttl is None:
            ttl = self.ttl

        def decorator(func):
            def _cache(instance, **kwargs):
                key = getattr(instance, self.keyfunc)(self, func, kwargs)
                key = prefix + key
                doc = self.coll.find_one({'key': key})

                if doc:
                    # use cached value
                    return doc['result']

                result = func(instance, **kwargs)

                expiry = time.time() + ttl
                self.coll.insert(
                        {'key': key, 'result': result, 'expiry': expiry})

                return result
            return _cache

        if not func is None:
            return decorator(func)
        else:
            return decorator
