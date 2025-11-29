import asyncio
import websockets
import os
import datetime

SAVE_FRAMES = True
FRAME_DIR = "frames"
os.makedirs(FRAME_DIR, exist_ok=True)

async def recibir_video(websocket):
    print(f"[{datetime.datetime.now()}] ✅ Nueva conexión desde {websocket.remote_address}")
    contador = 0

    try:
        async for mensaje in websocket:
            contador += 1
            tamaño = len(mensaje)
            print(f"[{datetime.datetime.now()}] 📥 Frame #{contador} recibido ({tamaño} bytes)")

            if SAVE_FRAMES:
                nombre = f"{FRAME_DIR}/frame_{contador:04d}.jpg"
                with open(nombre, "wb") as f:
                    f.write(mensaje)
                print(f"[{datetime.datetime.now()}] 💾 Guardado en {nombre}")

    except websockets.exceptions.ConnectionClosed as e:
        print(f"[{datetime.datetime.now()}] 🔌 Conexión cerrada: código={e.code}, motivo={e.reason}")

    except Exception as e:
        print(f"[{datetime.datetime.now()}] ⚠️ Error inesperado: {e}")

async def main():
    port = int(os.environ.get("PORT", 5000))  # Render asigna el puerto
    print(f"[{datetime.datetime.now()}] 🚀 Iniciando servidor WebSocket en 0.0.0.0:{port}")

    try:
        async with websockets.serve(recibir_video, "0.0.0.0", port):
            print(f"[{datetime.datetime.now()}] 🟢 Servidor listo y esperando conexiones...")
            await asyncio.Future()  # Mantener servidor activo
    except Exception as e:
        print(f"[{datetime.datetime.now()}] ❌ Error al iniciar el servidor: {e}")

if __name__ == "__main__":
    asyncio.run(main())
