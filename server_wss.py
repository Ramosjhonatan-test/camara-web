import asyncio
import os
import datetime
from aiohttp import web

FRAME_DIR = "frames"
os.makedirs(FRAME_DIR, exist_ok=True)
latest_frame = None

async def websocket_handler(request):
    global latest_frame
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    print(f"[{datetime.datetime.now()}] ✅ Nueva conexión WebSocket")

    async for msg in ws:
        if msg.type == web.WSMsgType.BINARY:
            latest_frame = msg.data  # guarda último frame en memoria
            nombre = f"{FRAME_DIR}/frame_latest.jpg"
            with open(nombre, "wb") as f:
                f.write(msg.data)

    return ws

async def mjpeg_stream(request):
    global latest_frame
    response = web.StreamResponse(
        status=200,
        reason='OK',
        headers={'Content-Type': 'multipart/x-mixed-replace; boundary=frame'}
    )
    await response.prepare(request)

    while True:
        if latest_frame:
            await response.write(b"--frame\r\n")
            await response.write(b"Content-Type: image/jpeg\r\n\r\n" + latest_frame + b"\r\n")
        await asyncio.sleep(0.1)  # ~10 fps
    return response

def main():
    port = int(os.environ.get("PORT", 5000))
    app = web.Application()
    app.router.add_get("/ws", websocket_handler)
    app.router.add_get("/stream", mjpeg_stream)
    web.run_app(app, host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()
