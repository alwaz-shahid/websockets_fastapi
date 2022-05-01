from fastapi import (
    FastAPI, WebSocket, WebSocketDisconnect,
    Request
)
from pydantic import BaseModel
import uvicorn

# from typing import List

app = FastAPI()


# define endpoint
@app.get("/")
def home():
    return "Welcome Home"


# manager
class SocketManager:
    def __init__(self):
        self.active_connections: list[(WebSocket, str)] = []

    async def connect(self, websocket: WebSocket, user: str):
        await websocket.accept()
        self.active_connections.append((websocket, user))

    def disconnect(self, websocket: WebSocket, user: str):
        self.active_connections.remove((websocket, user))

    async def broadcast(self, data):
        for connection in self.active_connections:
            await connection[0].send_json(data)


manager = SocketManager()


@app.websocket("/api/chat")
async def chat(websocket: WebSocket):
    sender = websocket.cookies.get("X-Authorization")
    if sender:
        await manager.connect(websocket, sender)
        response = {
            "sender": sender,
            "message": "got connected"
        }
        await manager.broadcast(response)
        try:
            while True:
                data = await websocket.receive_json()
                await manager.broadcast(data)
        except WebSocketDisconnect:
            manager.disconnect(websocket, sender)
            response['message'] = "left"
            await manager.broadcast(response)


@app.get("/api/current_user")
def get_user(request: Request):
    return request.cookies.get("X-Authorization")


class RegisterValidator(BaseModel):
    username: str


class Response(BaseModel):
    # username: str
    # password: str
    pass


@app.post("/api/register")
def register_user(user: RegisterValidator, response: Response):
    response.set_cookie(key="X-Authorization", value=user.username, httponly=True)


if __name__ == "__main__":
    uvicorn.run("main:app", port=8000, reload=True, access_log=True)

#
# @app.websocket("/api/chat")
# async def chat(websocket: WebSocket):
#     sender = websocket.cookies.get("X-Authorization")
#     if sender:
#         await manager.connect(websocket, sender)
#         response = {
#             "sender": sender,
#             "message": "got connected"
#         }
#         await manager.broadcast(response)
#         try:
#             while True:
#                 data = await websocket.receive_json()
#                 await manager.broadcast(data)
#         except WebSocketDisconnect:
#             manager.disconnect(websocket, sender)
#             response['message'] = "left"
#             await manager.broadcast(response)
