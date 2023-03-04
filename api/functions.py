from config import MAX_IMAGE_SIZE, CUSTOM_HEADERS
from random import randint
from tempfile import NamedTemporaryFile
import aiohttp
import aiofiles

MAX_IMAGE_SIZE = MAX_IMAGE_SIZE * 1000000


async def download_image(url: str) -> NamedTemporaryFile:
    async with aiohttp.ClientSession() as session:
        url_headers = get_headers_for_url(url)
        async with session.get(url, headers=url_headers) as resp:
            if resp.status == 200:
                if int(resp.headers["Content-Length"]) > MAX_IMAGE_SIZE:
                    return False
                f = NamedTemporaryFile("wb")
                f.write(await resp.read())
                f.flush()
            else:
                return False
    return f


def get_headers_for_url(url: str) -> dict[str, str]:
    """Returns custom headers for a given URL"""
    for k, v in CUSTOM_HEADERS.items():
        if k in url:
            return v
    return {}
