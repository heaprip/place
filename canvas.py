import io
import time
import typing as t

from PIL import Image
from redis import asyncio as aredis


class Canvas:
    def __init__(
        self,
        red: aredis.Redis,
        ttl_seconds: int = 2,
        tile_width: int = 100,
        tile_height: int = 100,
    ):
        self.tile_width = tile_width
        self.tile_height = tile_height
        self.red = red
        self.ttl_seconds = ttl_seconds
        self.previous_cache: t.Dict[int, t.Tuple[float, bytes]] = {}
        self.current_cache: t.Dict[int, t.Tuple[float, bytes]] = {}

    def _tile_key(self, ntile: int) -> str:
        return f"tile_{ntile}"

    async def initialize(self, canvas_width: int, canvas_height: int):
        ntiles = set()
        for x in range(
            (-canvas_width // 2) // self.tile_width,
            (canvas_width // 2) // self.tile_width,
        ):
            for y in range(
                (-canvas_height // 2) // self.tile_height,
                (canvas_height // 2) // self.tile_height,
            ):
                ntiles.add(self.xy_bijection(x, y))
        for ntile in ntiles:
            img = Image.new("RGBA", (self.tile_width, self.tile_height))
            await self.put_tile(ntile, img.tobytes())

    def xy_bijection(self, a: int, b: int) -> int:
        a = 2 * a if a >= 0 else -2 * a - 1
        b = 2 * b if b >= 0 else -2 * b - 1
        s = a + b
        return (s * (s + 1)) // 2 + b

    async def set_pixel(self, x: int, y: int, color: t.Tuple[int, int, int]):
        ntile = self.xy_bijection(x // self.tile_width, y // self.tile_height)

        tile_x = x % self.tile_width
        tile_y = -(y % self.tile_height)

        if tile_x < 0:
            tile_x = self.tile_width + tile_x
        if tile_y > 0:
            tile_y = self.tile_height - tile_y

        tile = await self.get_tile(ntile)
        img = Image.frombytes("RGBA", (self.tile_width, self.tile_height), tile)
        img.putpixel((tile_x, tile_y), color)
        await self.put_tile(ntile, img.tobytes())

    async def put_tile(self, ntile: int, pixels: bytes):
        await self.red.set(self._tile_key(ntile), pixels)

    async def get_tile(self, ntile: int) -> bytes:
        return await self.red.get(self._tile_key(ntile))

    async def get_cached_tile(self, ntile: int) -> bytes:
        if ntile in self.current_cache:
            timestamp, result = self.current_cache[ntile]
            if time.time() - timestamp < self.ttl_seconds:
                return result
            else:
                del self.current_cache[ntile]
        result = await self.get_tile(ntile)
        self.previous_cache[ntile] = self.current_cache.get(ntile)
        self.current_cache[ntile] = (time.time(), result)
        return result

    def _create_delta(self, previous_img: Image.Image, img: Image.Image) -> Image.Image:
        delta_img = Image.new("RGBA", (previous_img.width, previous_img.height))
        old_pixels = previous_img.load()
        new_pixels = img.load()
        delta_pixels = delta_img.load()
        for x in range(previous_img.width):
            for y in range(previous_img.height):
                if new_pixels[x, y] != old_pixels[x, y]:
                    delta_pixels[x, y] = new_pixels[x, y]
                else:
                    delta_pixels[x, y] = (0, 0, 0, 0)
        return delta_img

    async def get_tile_delta(self, ntile: int) -> Image.Image:
        _, current_tile = self.current_cache.get(ntile) or (None, None)
        if current_tile is None:
            current_tile = await self.get_tile(ntile)

        _, previous_tile = self.previous_cache.get(ntile) or (None, None)
        if previous_tile is None:
            previous_tile = await self.get_cached_tile(ntile)

        previous_img = Image.frombytes(
            "P", (self.tile_width, self.tile_height), previous_tile
        )
        img = Image.frombytes("P", (self.tile_width, self.tile_height), current_tile)
        return self._create_delta(previous_img, img)
