from fastapi import APIRouter, WebSocket
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


@router.websocket("/wss")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        await websocket.receive_text()
        await websocket.send_text("pong")
