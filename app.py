import logging
import time
import functools
from redis import asyncio as aredis
import attrs
import asyncio
import io
from random import randint
import uvloop

import orjson as json
import redis
from aiohttp import web
from PIL import Image, ImageDraw

import os

import dotenv

logger = logging.getLogger(__file__)

dotenv.load_dotenv()

@attrs.define
class Config:
    REDIS_DSN: str

config = Config(os.environ.get("REDIS_DSN"))


asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

def pillow_img_to_png_bytes(img: Image.Image, format="PNG"):
    with io.BytesIO() as output:
        img.save(output, format=format)
        return output.getvalue()


# TODO: validators
@attrs.define(frozen=True)
class RGBAColor:
    r: int = attrs.field(validator=(attrs.validators.ge(0), attrs.validators.lt(256)))
    g: int = attrs.field(validator=(attrs.validators.ge(0), attrs.validators.lt(256)))
    b: int = attrs.field(validator=(attrs.validators.ge(0), attrs.validators.lt(256)))
    a: int = attrs.field(validator=(attrs.validators.ge(0), attrs.validators.lt(256)))

    @property
    def tuple(self):
        return (self.r, self.g, self.b, self.a)

# TODO: validators
@attrs.define(frozen=True)
class CanvasConfig:
    height: int = attrs.field(validator=(attrs.validators.ge(200), attrs.validators.le(1000)))
    width: int = attrs.field(validator=(attrs.validators.ge(200), attrs.validators.le(1000)))
    background_color: RGBAColor


def tile_key(num: int) -> str:
    return f"tile_{num}"


async def put_tile(red: aredis.Redis, ntile: int, pixels: bytes):
    await red.set(tile_key(ntile), pixels)


async def create_place_canvas(req: web.Request):
    if not req.can_read_body:
        return web.HTTPError(reason="canvas config required")
    body = await req.json()
    res: aredis.Redis = req.app['redis']

    try:
        conf = CanvasConfig(**body)
    except ValueError:
        return web.HTTPError(reason="bad body")

    npixels = conf.width * conf.height
    # TODO: magic var
    tile_npixels = npixels // (10_000)

    img = Image.new('P', (100, 100))
    for ntile in range(tile_npixels):
        await put_tile(res, ntile, img.tobytes())
    
    return web.Response()


async def page(req):
    return web.FileResponse("some.html")


def xy_bijection(a: int, b: int) -> int:
    a = 2*a if a >= 0 else -2*a - 1
    b = 2*b if b >= 0 else -2*b - 1
    s = a + b
    return (s * (s + 1)) // 2 + b


async def pick_pixel(req: web.Request):
    hex_color = req.get('color')


def ttl_cache(ttl_seconds: int = 60, maxsize: int = 128):
    def decorator(func):
        @functools.lru_cache(maxsize=maxsize)
        def cached_func(ttl_hash, *args, **kwargs):
            return func(*args, **kwargs)
        
        def wrapper(*args, **kwargs):
            ttl_hash = int(time.time() // ttl_seconds)
            return cached_func(ttl_hash, *args, **kwargs)
        
        wrapper.cache_clear = cached_func.cache_clear
        wrapper.cache_info = cached_func.cache_info
        return wrapper
    return decorator



@ttl_cache(ttl_seconds=2, maxsize=None)
async def get_tile_pixels_bytes(red: aredis.Redis, ntile: int) -> bytes:
    logger.info(f"request tile {ntile}")
    return await red.get(tile_key(ntile))


async def tile_stream(req: web.Request):
    ntile = req.match_info.get('tile')
    if ntile is None:
        return web.HTTPError(reason="tile number required")

    res: aredis.Redis = req.app['redis']

    resp = web.StreamResponse(
        status=200,
        headers={
            "Content-Type": "image/png",
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0",
            "Transfer-Encoding": "chunked",
        },
    )

    await resp.prepare(req)
    tile_pixels = await get_tile_pixels_bytes(res, ntile)
    # TODO: tile size magic var
    img = Image.frombytes('P', (100, 100), data=tile_pixels)

    while True:
        await resp.write(img.tobytes())
        tile_pixels = await get_tile_pixels_bytes(res, ntile)
        img = Image.frombytes('P', (100, 100), tile_pixels)

        await asyncio.sleep(1)

    await resp.write_eof()
    return resp


def get_pixels(img: Image.Image):
    img_core = img.getdata()
    return img_core
    

async def stream(request):
    resp = web.StreamResponse(
        status=200,
        reason="OK",
        headers={
            "Content-Type": "image/png",
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0",
            "Transfer-Encoding": "chunked",
        },
    )
    await resp.prepare(request)
    img = Image.new("RGBA", (100, 100)).convert(
        "P", palette=Image.Palette.ADAPTIVE, colors=32
    )
    total_size = 0

    while True:
        img_bytes = pillow_img_to_png_bytes(img)
        await resp.write(img_bytes)
        total_size += len(img_bytes)
        print(f"Now sended {len(img_bytes)} b, Total: {total_size / 1024} Kb")

        img.putpixel(
            (randint(0, img.width - 1), randint(0, img.height - 1)),
            (
                randint(0, 255),
                randint(0, 255),
                randint(0, 255),
                randint(0, 255),
            ),
        )

        await asyncio.sleep(1)

    await resp.write_eof()
    return resp


async def redis_startup(app: web.Application):
    res = aredis.Redis.from_url(config.REDIS_DSN)
    await res.ping()
    app['redis'] = res


async def redis_cleanup(app: web.Application):
    res: aredis.Redis = app['redis']
    await res.aclose()


if __name__ == "__main__":
    app = web.Application()

    app.router.add_get("/stream/{tile}", tile_stream)
    app.router.add_get("/", page)
    app.router.add_post("/new", create_place_canvas)

    app.on_startup.append(redis_startup)
    app.on_cleanup.append(redis_cleanup)

    web.run_app(app, host="127.0.0.1", port=8080)
