#!/bin/bash
set -e

PORT=8888
DIR="/srv/school-ai/var/video-cong-khai/purple-w06-tiktok"
LOG="/var/log/purple-video-tunnel.log"
URL_FILE="/srv/school-ai/var/video-cong-khai/purple-w06-tiktok/public_url.txt"

# Kill old instances on PORT if any
fuser -k ${PORT}/tcp 2>/dev/null || true

# Start Python HTTP server on port 8888 in background
python3 -m http.server ${PORT} --directory "${DIR}" > /var/log/purple-http-server.log 2>&1 &

echo "Started HTTP server on port ${PORT} for ${DIR}"

# Start Cloudflare Tunnel and capture URL
exec /usr/local/bin/cloudflared tunnel --url http://127.0.0.1:${PORT} 2>&1 | while read -r line; do
    echo "$line" >> "$LOG"
    if [[ "$line" =~ (https://[a-zA-Z0-9-]+\.trycloudflare\.com) ]]; then
        ACTIVE_URL="${BASH_REMATCH[1]}"
        echo "$ACTIVE_URL" > "$URL_FILE"
        echo "[TUNNEL READY] $ACTIVE_URL"
    fi
done
