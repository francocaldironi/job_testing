import cachetools
import time

cache = cachetools.TTLCache(maxsize=100, ttl=300)


def cache_get(key):
    return cache.get(key)


def cache_set(key, value):
    cache[key] = value
