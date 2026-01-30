from fastapi import WebSocket
from typing import Dict


class ConnectionManager:
    def __init__(self):
        # Stores active connections as {email: WebSocket}
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, email: str, websocket: WebSocket):
        """
        Establish a connection with the user.
        """
        await websocket.accept()
        self.active_connections[email] = websocket

    async def disconnect(self, email: str):
        """
        Closes the connection and removes it from the list of active connections.
        """
        if email in self.active_connections:
            del self.active_connections[email]

    async def broadcast(self, message: dict):
        """
        Send a message to all connected users.
        """
        for email, connection in self.active_connections.items():
            try:
                await connection.send_json(message)
            except Exception:
                pass

    def get_all_connected_users(self):
        return list(self.active_connections.keys())


manager = ConnectionManager()
