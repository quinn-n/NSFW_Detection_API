from fastapi import FastAPI

from nsfw_detector import predict

app = FastAPI()

__all__ = ("predict",)
