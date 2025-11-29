import asyncio
import websockets
import os
import datetime
from aiohttp import web

SAVE_FRAMES = True
FRAME_DIR = "frames"
os.makedirs(FRAME_DIR, exist_ok=True)

async def recibir_video(websocket):
    print(f"[{datetime.datetime.now()}] ✅ Nueva conexión desde {websocket.remote_address}")
    contador = 0
    try:
        async for mensaje in websocket:
            contador += 1
            print(f"[{datetime.datetime.now()}] 📥 Frame #{contador} recibido ({len(mensaje)} bytes)")
            if SAVE_FRAMES:
                nombre = f"{FRAME_DIR}/frame_{contador:04d}.jpg"
                with open(nombre, "wb") as f:
                    f.write(mensaje)
                print(f"[{datetime.datetime.now()}] 💾 Guardado en {nombre}")
    except websockets.exceptions.ConnectionClosed as e:
        print(f"[{datetime.datetime.now()}] 🔌 Conexión cerrada: código={e.code}, motivo={e.reason}")

# Endpoint HTTP para health check
async def health(request):
    return web.Response(text="Servidor WebSocket activo")

async def main():
    port = int(os.environ.get("PORT", 5000))  # Render asigna el puerto
    print(f"[{datetime.datetime.now()}] 🚀 Iniciando servidor en 0.0.0.0:{port}")

    # Servidor HTTP (para health check)
    app = web.Application()
    app.router.add_get("/", health)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

    # Servidor WebSocket (en el mismo puerto)
    async with websockets.serve(recibir_video, "0.0.0.0", port):
        print(f"[{datetime.datetime.now()}] 🟢 Servidor listo y esperando conexiones...")
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
