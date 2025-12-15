import time
import typing as t


def async_ttl_cache(ttl_seconds: int):
    def decorator(func: t.Callable) -> t.Callable:
        cache: t.Dict[tuple, tuple[float, t.Any]] = {}

        async def wrapper(*args, **kwargs) -> t.Any:
            key = (args, tuple(sorted(kwargs.items())))

            if key in cache:
                timestamp, result = cache[key]
                if time.time() - timestamp < ttl_seconds:
                    return result
                else:
                    del cache[key]

            result = await func(*args, **kwargs)
            cache[key] = (time.time(), result)
            return result

        return wrapper

    return decorator
