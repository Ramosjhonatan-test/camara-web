#!/usr/bin/env bash
set -e

# Instala FFmpeg si no está
if ! command -v ffmpeg >/dev/null 2>&1; then
  apt-get update && apt-get install -y ffmpeg
fi

# Arranca el servidor
python server_wss.py
