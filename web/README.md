# NetOps Copilot — Web App (local only)

A browser UI for the same validation the CLI runners do. Standard
library only (no FastAPI, no pip installs). It reuses the policy,
parsing, CLI rendering and proposal helpers from `copilot.py` and
`advanced/advanced.py` — it does not duplicate the policy and it does
not write demo-output report files.

## Simplest way: GitHub Codespaces (no local install)

No WSL, no manual Java or jar setup. The lab configs are in this
repo under `labs/`, and the codespace provides Python, Java,
pybatfish, and the Batfish service.

1. Open https://github.com/papilion/netops-copilot-demo on github.com.
2. Click the green **Code** button, then the **Codespaces** tab, then
   **Create codespace** (on branch `main`).
3. Wait for setup to finish. The first build pulls the official
   Batfish image (`batfish/allinone`) and can take several minutes;
   `scripts/start-live.sh` then starts Batfish on port 9996 and this
   web app on port 8000.
4. In the Codespaces **Ports** tab, open the forwarded port **8000**
   (keep its visibility **Private** — do not make it Public).
5. In the web UI, select topology **Advanced**, select a scenario,
   set mode **Live**, and click **Run**.

If Live mode returns HTTP 503, Batfish is not up yet: wait a minute
and try again, or run `bash scripts/start-live.sh` in the codespace
terminal. If Docker is unavailable in the codespace, the only manual
step is `docker run -d --name batfish -p 9996:9996 batfish/allinone`
followed by `bash scripts/start-live.sh`; recorded mode works with
no Batfish at all. A real Codespaces boot was not run from the
machine that built this repo, so the first creation is the proof run
— see `.devcontainer/README.md` for exactly what is automatic and
what is not yet verified.

## Run (local clone)

```text
python3 web/app.py
# open http://127.0.0.1:8000/
# WEB_PORT=8080 python3 web/app.py   (to change the port)
```

## Modes

- **Recorded replay** (default): canned Batfish impact reports in
  `demo-data/` and `advanced/demo-data-advanced/`. Works with no
  Batfish server. Labelled "recorded replay" everywhere in the UI.
- **Live**: the Batfish service on port 9996. If Batfish is
  unreachable the API returns HTTP 503 with the exact start command
  and does NOT silently fall back to recorded. The UI shows the error
  and offers the recorded-replay button instead.

## Fallback: local PC (WSL) — live Batfish (one at a time)

If you are not using Codespaces, run Batfish yourself (WSL on
Windows, since the lab paths are Linux-style). The simple lab and
the advanced lab share Batfish port 9996, so only one Batfish
service runs at a time. Stop one before starting the other. This
server never auto-starts Batfish.

```text
~/workspace/batfish-lab/start-batfish.sh
~/workspace/batfish-lab-advanced/start-batfish-advanced.sh
```

## Endpoints

- `GET /` — the single-page UI (`web/static/index.html`).
- `GET /api/scenarios` — 11 scenarios (simple 3 + advanced 8) with
  title and intent. No verdict expectation is revealed before a run.
- `POST /api/validate` — JSON `{"scenario": "<name>", "mode":
  "live"|"recorded", "lang": "ko"}`. Returns verdict, violations,
  notes, evidence rows, `cli_view`, proposed next step and
  `evidence_source`.
- `GET /docs/*.png` — the topology diagrams from `docs/`.

## AI explanation

The verdict always comes from Batfish evidence, never from the model.
The explanation and proposal shown in the UI are rule-based text,
unless the server was started with `META_API_KEY` set, in which case
the existing Meta path may refine them server-side. The key is never
sent to the browser, never shown in the UI and never logged. Without
a key the UI says "Meta API not configured on this server" — never a
fake model answer.

## Security and scope (read before sharing this server)

- Local only: it binds 127.0.0.1 and has no authentication. Do NOT
  expose it to the internet or a shared network without adding auth.
- Validation only: it never applies a change to a router. A human
  decides.
- Demo data is fictional (RFC 5737, AS 64496-64501). Never paste
  production configs into a public demo.
- The verdict covers the watched scope only. Unwatched prefixes and
  flows, traffic volume, latency, convergence time and vendor bugs are
  outside what Batfish evidence proves.
