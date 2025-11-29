import asyncio
import os
import datetime
from aiohttp import web

SAVE_FRAMES = True
FRAME_DIR = "frames"
os.makedirs(FRAME_DIR, exist_ok=True)

async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    print(f"[{datetime.datetime.now()}] ✅ Nueva conexión WebSocket")
    contador = 0

    async for msg in ws:
        if msg.type == web.WSMsgType.BINARY:
            contador += 1
            print(f"[{datetime.datetime.now()}] 📥 Frame #{contador} recibido ({len(msg.data)} bytes)")
            if SAVE_FRAMES:
                nombre = f"{FRAME_DIR}/frame_{contador:04d}.jpg"
                with open(nombre, "wb") as f:
                    f.write(msg.data)
                print(f"[{datetime.datetime.now()}] 💾 Guardado en {nombre}")

    print(f"[{datetime.datetime.now()}] 🔌 Conexión cerrada")
    return ws

async def health(request):
    return web.Response(text="Servidor WebSocket activo")

def main():
    port = int(os.environ.get("PORT", 5000))
    app = web.Application()
    app.router.add_get("/", health)
    app.router.add_get("/ws", websocket_handler)  # WebSocket en /ws

    print(f"[{datetime.datetime.now()}] 🚀 Servidor escuchando en 0.0.0.0:{port}")
    web.run_app(app, host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()
import asyncio
import os
import datetime
from aiohttp import web

SAVE_FRAMES = True
FRAME_DIR = "frames"
os.makedirs(FRAME_DIR, exist_ok=True)

async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    print(f"[{datetime.datetime.now()}] ✅ Nueva conexión WebSocket")
    contador = 0

    async for msg in ws:
        if msg.type == web.WSMsgType.BINARY:
            contador += 1
            print(f"[{datetime.datetime.now()}] 📥 Frame #{contador} recibido ({len(msg.data)} bytes)")
            if SAVE_FRAMES:
                nombre = f"{FRAME_DIR}/frame_{contador:04d}.jpg"
                with open(nombre, "wb") as f:
                    f.write(msg.data)
                print(f"[{datetime.datetime.now()}] 💾 Guardado en {nombre}")

    print(f"[{datetime.datetime.now()}] 🔌 Conexión cerrada")
    return ws

async def health(request):
    return web.Response(text="Servidor WebSocket activo")

def main():
    port = int(os.environ.get("PORT", 5000))
    app = web.Application()
    app.router.add_get("/", health)
    app.router.add_get("/ws", websocket_handler)  # WebSocket en /ws

    print(f"[{datetime.datetime.now()}] 🚀 Servidor escuchando en 0.0.0.0:{port}")
    web.run_app(app, host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()
