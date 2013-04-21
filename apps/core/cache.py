from django.core.cache import cache
from django.conf import settings

"""
def cache_prefix(func):
    def wrapper(key, *args, **kwargs):
        prefix = settings.CACHES['default'].get('KEY_PREFIX', '')
        prefix +=  ":" + key
        return func(key, *args, **kwargs)
    return wrapper

meths = [
    'add', 'get', 'set', 'decr', 'decr_version', 'delete', 'delete_many', 'get_many', 
    'has_key', 'incr', 'incr_version', 'key_func', 'make_key', 'set', 'set_many',
    'validate_key'
]
for m in meths:
    setattr(
        cache, m,
        cache_prefix(getattr(cache, m))
    )
#cache.get = cache_prefix(cache.get)
#cache.set = cache_prefix(cache.set)
"""
