from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Request, Depends
from starlette.responses import HTMLResponse

from app.dependencies.deps import get_current_user_ws
from app.core.websocket_manager import manager
from app.core.templates import templates

router = APIRouter(prefix="/ws")


@router.websocket("")
async def websocket_endpoint(
    websocket: WebSocket, user: dict = Depends(get_current_user_ws)
):
    if user is None:
        return

    email = user["sub"]

    await manager.connect(email, websocket)
    connected_users = manager.get_all_connected_users()
    await websocket.send_json({"event": "already_logged_in", "users": connected_users})
    await manager.broadcast({"event": "user_joined", "email": email})

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        await manager.disconnect(email)
        await manager.broadcast({"event": "user_exit", "email": email})
    except Exception as e:
        print(f"An error occured: {e}")


@router.get("/enter", response_class=HTMLResponse)
async def board_page(
    request: Request,
):
    """Displays a task board page."""
    return templates.TemplateResponse("board.html", {"request": request})
