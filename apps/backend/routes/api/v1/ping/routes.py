from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(
    prefix="/api/v1/ping",
    tags=["ping"],
)


class PingResponse(BaseModel):
    message: str


@router.get("/")
async def ping() -> PingResponse:
    """
    Ping the API to check if it is running.
    """

    return PingResponse(message="pong")
