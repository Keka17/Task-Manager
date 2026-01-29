from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Request
from typing import Dict

from starlette.responses import HTMLResponse

from app.dependencies.deps import get_current_user_ws
from fastapi.templating import Jinja2Templates

router = APIRouter(prefix="/ws")
templates = Jinja2Templates(directory="app/templates")


class ConnectionManager:
    def __init__(self):
        # Stores active connections as {user_id: WebSocket}
        self.active_connections: Dict[int, WebSocket] = {}

    async def connect(self, user_id: int, websocket: WebSocket):
        """
        Establish a connection with the user.
        """
        await websocket.accept()
        self.active_connections[user_id] = websocket

    async def disconnect(self, user_id: int):
        """
        Closes the connection and removes it from the list of active connections.
        """
        if user_id in self.active_connections:
            del self.active_connections[user_id]

    async def broadcast(self, message: dict):
        for websocket in self.active_connections.values():
            await websocket.send_json(message)


manager = ConnectionManager()


@router.websocket("")
async def board_socket(websocket: WebSocket):
    user = await get_current_user_ws(websocket)
    if not user:
        return

    await manager.connect(user.id, websocket)

    await manager.broadcast({"event": "user_joined", "email": user.email})

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        await manager.disconnect(user.id)
        await manager.broadcast({"event": "user_left", "email": user.email})


@router.get("/enter", response_class=HTMLResponse)
async def board_page(
    request: Request,
):
    return templates.TemplateResponse("board.html", {"request": request})
