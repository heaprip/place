import asyncio
import logging
import os

import attrs
import dotenv
import uvloop
from aiohttp import web
from redis import asyncio as aredis

from canvas import Canvas
from routes import (
    get_page_route,
    get_tile_delta_stream_route,
    get_tile_route,
    post_pixel_route,
    post_place_canvas_route,
)

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

logger = logging.getLogger(__file__)

dotenv.load_dotenv()


@attrs.define
class Config:
    REDIS_DSN: str


config = Config(os.environ.get("REDIS_DSN"))


async def redis_startup(app: web.Application):
    res = aredis.Redis.from_url(config.REDIS_DSN)
    await res.ping()
    app["redis"] = res


async def redis_cleanup(app: web.Application):
    res: aredis.Redis = app["redis"]
    await res.aclose()


async def canvas_startup(app: web.Application):
    canvas = Canvas(app["redis"], 1, 100, 100)
    await canvas.initialize(1000, 1000)
    app["canvas"] = canvas


# TODO: ...
async def canvas_cleanup(app: web.Application): ...


if __name__ == "__main__":
    app = web.Application()

    app.router.add_get("/tile/{tile}", get_tile_route)
    app.router.add_get("/tile/{tile}/stream", get_tile_delta_stream_route)
    app.router.add_get("/", get_page_route)
    app.router.add_post("/new", post_place_canvas_route)
    app.router.add_post("/pixel", post_pixel_route)

    app.on_startup.append(redis_startup)
    app.on_startup.append(canvas_startup)

    app.on_cleanup.append(redis_cleanup)
    app.on_cleanup.append(canvas_cleanup)

    web.run_app(app, host="127.0.0.1", port=8080)
