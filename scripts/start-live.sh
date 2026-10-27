#!/usr/bin/env bash
# Start the NetOps Copilot live demo: Batfish (advanced lab) + web app.
# Idempotent: already-running services are left alone. Exit code is 0
# even if Batfish could not start, so a codespace is still usable in
# recorded mode; the script prints exactly what is ready and what is not.
set -u
cd "$(dirname "$0")/.."

batfish_ready() {
  # Any HTTP answer from the coordinator means the service is up
  # (its root path answers 404, which still proves it is listening).
  curl -s -o /dev/null -m 3 "http://127.0.0.1:9996/" 2>/dev/null
}

web_ready() {
  curl -s -o /dev/null -m 3 "http://127.0.0.1:${WEB_PORT:-8000}/api/scenarios" 2>/dev/null
}

# --- Batfish (official image batfish/allinone, port 9996) ---------------
if batfish_ready; then
  echo "Batfish: READY on port 9996 (already running)."
elif command -v docker >/dev/null 2>&1; then
  if docker ps -a --format '{{.Names}}' 2>/dev/null | grep -qx batfish; then
    docker start batfish >/dev/null 2>&1 || true
  else
    docker run -d --name batfish -p 9996:9996 batfish/allinone >/dev/null 2>&1 || true
  fi
  echo "Batfish: container started, warming up (first parse takes a while)..."
  for i in $(seq 1 100); do
    if batfish_ready; then
      echo "Batfish: READY on port 9996."
      break
    fi
    if [ $((i % 10)) -eq 0 ]; then
      echo "Batfish: still warming up (attempt $i/100, ~$((i * 3))s elapsed)..."
    fi
    sleep 3
  done
  if ! batfish_ready; then
    echo "Batfish: NOT READY after ~5 minutes. Live mode will return HTTP 503; use Recorded replay, or check: docker logs batfish"
  fi
else
  echo "Batfish: NOT STARTED (docker unavailable). Live mode needs: docker run -d --name batfish -p 9996:9996 batfish/allinone"
  echo "Batfish: web app will still run in Recorded replay mode."
fi

# --- Web app (127.0.0.1 only; Codespaces forwards port 8000) ------------
if web_ready; then
  echo "Web app: READY on port ${WEB_PORT:-8000} (already running)."
else
  nohup python3 web/app.py > /tmp/netops-web.log 2>&1 &
  sleep 2
  if web_ready; then
    echo "Web app: READY on port ${WEB_PORT:-8000}. Open the Codespaces forwarded port 8000."
  else
    echo "Web app: FAILED to start. See /tmp/netops-web.log"
  fi
fi
