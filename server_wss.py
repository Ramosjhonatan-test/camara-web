import asyncio
import os
import datetime
import subprocess
from aiohttp import web, WSMsgType

HLS_DIR = "hls"
os.makedirs(HLS_DIR, exist_ok=True)

ffmpeg_proc = None

FFMPEG_ARGS = [
    "ffmpeg",
    "-loglevel", "warning",
    "-re",
    "-f", "image2pipe",
    "-vcodec", "mjpeg",
    "-i", "pipe:0",
    "-vf", "scale=1280:720:flags=bicubic",
    "-c:v", "libx264",
    "-preset", "veryfast",
    "-tune", "zerolatency",
    "-profile:v", "high",
    "-b:v", "2500k",
    "-maxrate", "3000k",
    "-bufsize", "5000k",
    "-g", "48",
    "-sc_threshold", "0",
    "-f", "hls",
    "-hls_time", "2",
    "-hls_list_size", "6",
    "-hls_flags", "delete_segments+append_list+independent_segments",
    "-hls_segment_type", "mpegts",
    "-hls_segment_filename", os.path.join(HLS_DIR, "seg_%03d.ts"),
    os.path.join(HLS_DIR, "index.m3u8"),
]

async def start_ffmpeg():
    global ffmpeg_proc
    if ffmpeg_proc and ffmpeg_proc.poll() is None:
        return
    for f in os.listdir(HLS_DIR):
        try:
            os.remove(os.path.join(HLS_DIR, f))
        except Exception:
            pass
    ffmpeg_proc = subprocess.Popen(
        FFMPEG_ARGS,
        stdin=subprocess.PIPE,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT,
        bufsize=0,
    )
    print(f"[{datetime.datetime.now()}] 🚀 FFmpeg iniciado")

async def websocket_handler(request):
    global ffmpeg_proc
    ws = web.WebSocketResponse(max_msg_size=10 * 1024 * 1024)
    await ws.prepare(request)
    print(f"[{datetime.datetime.now()}] ✅ WebSocket conectado")

    await start_ffmpeg()
    recibidos = 0

    try:
        async for msg in ws:
            if msg.type == WSMsgType.BINARY:
                recibidos += 1
                if ffmpeg_proc and ffmpeg_proc.poll() is None:
                    try:
                        ffmpeg_proc.stdin.write(msg.data)
                        ffmpeg_proc.stdin.flush()
                    except BrokenPipeError:
                        await start_ffmpeg()
                if recibidos % 30 == 0:
                    print(f"[{datetime.datetime.now()}] 📥 Frames recibidos: {recibidos}")
    finally:
        print(f"[{datetime.datetime.now()}] 🔌 WebSocket cerrado")
    return ws

async def health(request):
    return web.Response(text="Servidor HLS activo")

def main():
    port = int(os.environ.get("PORT", 5000))
    app = web.Application()
    app.router.add_get("/", health)
    app.router.add_get("/ws", websocket_handler)
    app.router.add_static("/hls", path=HLS_DIR, name="hls")

    print(f"[{datetime.datetime.now()}] 🎯 Escuchando en 0.0.0.0:{port}")
    web.run_app(app, host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()
