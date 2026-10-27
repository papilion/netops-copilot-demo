# NetOps Copilot in GitHub Codespaces

This folder makes the live demo runnable from github.com alone, with
no local install, no WSL, and no manual Java or jar setup.

## What creation does automatically

- Base image: Python 3.12, with Java 21 and Docker-in-Docker features.
- `postCreateCommand` (`.devcontainer/setup.sh`): installs `pybatfish`
  with pip and pulls the official Batfish image `batfish/allinone`
  (documented in the Batfish README as `docker pull batfish/allinone`,
  run with `-p 9996:9996`). No jar is stored in this repo.
- `postStartCommand` (`scripts/start-live.sh`): starts the Batfish
  container if Docker is available, then starts the web app on port
  8000 (bound to 127.0.0.1 inside the codespace; Codespaces port
  forwarding is the only external access).

## If Docker is unavailable in the codespace

This was not verified from a machine without Codespaces access, so
treat it as the one remaining manual step, not as an automatic one:

```text
docker run -d --name batfish -p 9996:9996 batfish/allinone
bash scripts/start-live.sh
```

Then open the forwarded port 8000. If Batfish is still not up, the
web app returns HTTP 503 for Live mode (with the start command) and
does not silently fall back — use Recorded replay instead, which
needs no Batfish at all.

## Ports: only 8000 is forwarded

Only port 8000 (the web app) is forwarded to the browser. Port 9996
is the Batfish coordinator API, used internally by the web app and
pybatfish — it is not a web page, so opening it in a browser returns
a 404. That 404 is normal: it proves Batfish is listening, and it
does not affect Live mode, which runs entirely through port 8000.
The devcontainer sets port 9996 to `onAutoForward: ignore` so it no
longer appears as a second forwarded port.

## Opening the web app (first-time users)

Do not type an address by hand. In the Codespaces window, click the
**PORTS** tab at the bottom, find the port **8000** row, and click
the **globe icon** on the right side of that row ("Open in
Browser"). That opens the web app in a new browser tab. If the globe
is not visible, right-click the 8000 row and choose "Open in
Browser". The globe only opens the page for you — it does not make
the port Public, and the forwarded address still requires your
GitHub login.

## Port visibility

Keep the forwarded port 8000 **Private** (the Codespaces default for
your own codespace). Do not change it to Public: this demo web app
has no authentication, binds 127.0.0.1 only, and never applies a
change to a router. It is a validation demo, not a shared service.

## Verification status

Live mode in Codespaces was confirmed working by the project owner
on 2026-10-27: the web app on forwarded port 8000 runs Live
scenarios end to end. The Docker-unavailable fallback above is
still documented for codespaces where Docker is not available;
recorded mode still works with zero setup in that case.
