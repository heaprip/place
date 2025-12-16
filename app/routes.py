import asyncio
import datetime
import io

from aiohttp import web
from PIL import Image

from app.canvas import Canvas
from app.schemas import CanvasConfig, Pixel, RGBColor


def pillow_img_to_png_bytes(img: Image.Image, format="PNG"):
    with io.BytesIO() as output:
        img.save(output, format=format)
        return output.getvalue()


async def get_health_route(req: web.Request):
    resp = web.Response()
    return resp


async def get_page_route(req):
    return web.FileResponse("template.html")


async def get_tile_route(req: web.Request):
    ntile = req.match_info.get("tile")
    if ntile is None:
        return web.HTTPError(reason="tile number required")
    canvas: Canvas = req.app["canvas"]

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
    tile_bytes = await canvas.get_tile(ntile)
    # TODO: tile size magic var

    img = Image.frombytes(
        "RGB", (canvas.tile_width, canvas.tile_height), data=tile_bytes
    )
    img_png = pillow_img_to_png_bytes(img)
    await resp.write(img_png)
    return resp


async def post_place_canvas_route(req: web.Request):
    if not req.can_read_body:
        return web.HTTPError(reason="canvas config required")
    body = await req.json()
    canvas: Canvas = req.app["canvas"]

    try:
        conf = CanvasConfig(**body)
    except ValueError:
        return web.HTTPError(reason="bad body")

    npixels = conf.width * conf.height
    # TODO: magic var
    tile_npixels = npixels // (10_000)

    img = Image.new("RGB", (100, 100))
    for ntile in range(tile_npixels):
        await canvas.put_tile(ntile, img.tobytes())

    return web.Response()


async def post_pixel_route(req: web.Request):
    if not req.can_read_body:
        return web.HTTPError(reason="pixel body required")
    body = await req.json()
    pixel = Pixel(x=body["x"], y=body["y"], color=RGBColor(**body["color"]))

    canvas: Canvas = req.app["canvas"]

    await canvas.set_pixel(pixel.x, pixel.y, pixel.color.tuple)

    return web.Response()


async def get_tile_delta_stream_route(req: web.Request):
    ntile = req.match_info.get("tile")
    if ntile is None:
        return web.HTTPError(reason="tile number required")
    canvas: Canvas = req.app["canvas"]

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
    # TODO: tile size magic var

    after_hour = datetime.datetime.now() + datetime.timedelta(hours=1)
    while datetime.datetime.now() <= after_hour:
        delta_img = await canvas.get_tile_delta(ntile)
        await resp.write(pillow_img_to_png_bytes(delta_img))

        await asyncio.sleep(1)

    await resp.write_eof()
    return resp
