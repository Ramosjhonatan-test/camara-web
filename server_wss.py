import asyncio
import os
import datetime
from aiohttp import web

# Carpeta para guardar frames (opcional, para evidencia)
FRAME_DIR = "frames"
os.makedirs(FRAME_DIR, exist_ok=True)

# Variable global para mantener el último frame en memoria
latest_frame = None

# Handler WebSocket: recibe frames desde el cliente
async def websocket_handler(request):
    global latest_frame
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    print(f"[{datetime.datetime.now()}] ✅ Nueva conexión WebSocket")
    contador = 0

    async for msg in ws:
        if msg.type == web.WSMsgType.BINARY:
            contador += 1
            latest_frame = msg.data  # guarda último frame en memoria
            # Guardar también en disco (opcional, para evidencia)
            nombre = f"{FRAME_DIR}/frame_latest.jpg"
            with open(nombre, "wb") as f:
                f.write(msg.data)
            print(f"[{datetime.datetime.now()}] 📥 Frame #{contador} recibido ({len(msg.data)} bytes)")

    print(f"[{datetime.datetime.now()}] 🔌 Conexión cerrada")
    return ws

# Endpoint de health check
async def health(request):
    return web.Response(text="Servidor WebSocket activo")

# Endpoint MJPEG streaming
async def mjpeg_stream(request):
    global latest_frame
    response = web.StreamResponse(
        status=200,
        reason='OK',
        headers={'Content-Type': 'multipart/x-mixed-replace; boundary=frame'}
    )
    await response.prepare(request)

    try:
        while True:
            if latest_frame:
                await response.write(b"--frame\r\n")
                await response.write(b"Content-Type: image/jpeg\r\n\r\n" + latest_frame + b"\r\n")
            # Intervalo optimizado: 0.05s ≈ 20 fps
            await asyncio.sleep(0.05)
    except (asyncio.CancelledError, ConnectionResetError, web.HTTPException):
        print(f"[{datetime.datetime.now()}] 🔌 Cliente desconectado del stream")
    finally:
        try:
            await response.write_eof()
        except Exception:
            pass
    return response

def main():
    port = int(os.environ.get("PORT", 5000))
    app = web.Application()
    app.router.add_get("/", health)
    app.router.add_get("/ws", websocket_handler)   # WebSocket para recibir frames
    app.router.add_get("/stream", mjpeg_stream)    # MJPEG streaming público
    app.router.add_static('/frames', path=FRAME_DIR, name='frames')  # opcional: acceso a frames guardados

    print(f"[{datetime.datetime.now()}] 🚀 Servidor escuchando en 0.0.0.0:{port}")
    web.run_app(app, host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()
