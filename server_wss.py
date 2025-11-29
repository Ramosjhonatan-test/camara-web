import asyncio
import websockets
import os
import datetime

SAVE_FRAMES = True
FRAME_DIR = "frames"
os.makedirs(FRAME_DIR, exist_ok=True)

async def recibir_video(websocket):
    print(f"[{datetime.datetime.now()}] Conexión desde {websocket.remote_address}")
    contador = 0

    try:
        async for mensaje in websocket:
            contador += 1
            print(f"📥 Frame recibido #{contador} ({len(mensaje)} bytes)")

            if SAVE_FRAMES:
                nombre = f"{FRAME_DIR}/frame_{contador:04d}.jpg"
                with open(nombre, "wb") as f:
                    f.write(mensaje)

    except websockets.exceptions.ConnectionClosed:
        print(f"[{datetime.datetime.now()}] Conexión cerrada")

async def main():
    port = int(os.environ.get("PORT", 5000))  # Render asigna el puerto
    print(f"🚀 Servidor WebSocket escuchando en 0.0.0.0:{port}")
    async with websockets.serve(recibir_video, "0.0.0.0", port):
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
