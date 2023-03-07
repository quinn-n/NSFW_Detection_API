from typing import Union

import uvicorn
import click

from api import predict, app
from api.functions import download_image
from config import PORT
from api.cache import async_cache

model = predict.load_model("nsfw_detector/nsfw_model.h5")


@app.get("/")
async def detect_nsfw(url: str):
    if not url:
        return {"ERROR": "URL PARAMETER EMPTY"}
    return await classify(url)


@async_cache(30 * 60)
async def classify(url: str) -> dict[str, dict[str, Union[float, bool]]]:
    image = await download_image(url)
    if image is None:
        return {"ERROR": "IMAGE SIZE TOO LARGE OR INCORRECT URL"}
    results = predict.classify(model, image.name)
    image.close()
    hentai = results["data"]["hentai"]
    sexy = results["data"]["sexy"]
    porn = results["data"]["porn"]
    drawings = results["data"]["drawings"]
    neutral = results["data"]["neutral"]
    if neutral >= 25:
        results["data"]["is_nsfw"] = False
        return results
    elif (sexy + porn + hentai) >= 70:
        results["data"]["is_nsfw"] = True
        return results
    elif drawings >= 40:
        results["data"]["is_nsfw"] = False
        return results
    else:
        results["data"]["is_nsfw"] = False
        return results


@click.command()
@click.option(
    "--local",
    "-l",
    default=False,
    is_flag=True,
    type=bool,
    help="Runs api without ssl for local testing",
)
def run_app(local: bool) -> None:
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=PORT,
        log_level="debug",
        ssl_keyfile=".certificates/privkey.pem" if not local else None,
        ssl_certfile=".certificates/fullchain.pem" if not local else None,
    )


if __name__ == "__main__":
    run_app()
