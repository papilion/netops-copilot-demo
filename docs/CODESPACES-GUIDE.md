# NetOps Copilot — Codespaces Guide (for first-time users)

This document walks through running the NetOps Copilot live demo in
GitHub Codespaces, click by click, from creation to shutdown. No local
install, no WSL, and no manual Java setup is needed. All you need is a
GitHub account and a browser.

A Korean version of this guide is available at
[CODESPACES-GUIDE.ko.md](CODESPACES-GUIDE.ko.md).

## 0. What is a Codespace?

A Codespace is a development computer inside GitHub's cloud. When you
open one for this repo, you get an environment with Python, Java, and
Batfish already set up, right in your browser. Nothing is installed on
your own PC. A Codespace belongs to your account only. Even though this
repository is public, nobody else can open or start your Codespace. If
someone else wants to try the demo, they must create their own
Codespace under their own account, and the cost comes out of their
account, not yours.

## 1. Creating one for the first time (takes 10–15 minutes)

1. Open the repository on github.com.
   `https://github.com/papilion/netops-copilot-demo`
2. Click the green **Code** button → the **Codespaces** tab → **Create
   codespace**. (Branch: `main`.)
3. Wait for setup to finish. **10–15 minutes is the normal range for
   a first creation**: VM provisioning, dev-container build, Batfish
   image download, and Batfish startup/parsing run one after another.
4. You may close the browser tab while it is being created. Creation
   continues on the server, and you can reopen it later from the
   Codespaces list.
5. **Do not press + repeatedly.** Every + creates a brand-new
   Codespace from scratch, resetting the wait you have already done.

### Watching the creation log

If setup looks stuck, press `Cmd/Ctrl + Shift + P` and choose **View
Creation Log**. It shows where it stopped (for example, downloading
the image, or starting Batfish). The step
`Running postStartCommand... bash scripts/start-live.sh` waits for
Batfish to become ready, so a spinning indicator for a few minutes
there is normal. The script prints progress every 30 seconds.

## 2. Opening the web app (the globe icon)

1. Once the Codespace opens, click the **PORTS** tab at the bottom.
   If you cannot see it, use the top menu View > Ports, or press
   `Cmd/Ctrl + Shift + P` and choose "Ports: Focus on Ports View".
2. Find the row for port **8000**. (Label: NetOps Copilot web app.)
3. Click the **globe icon** ("Open in Browser") on the right side of
   that row. The web app opens in a new browser tab. If the globe icon
   is not visible, right-click the 8000 row and choose "Open in
   Browser".
4. Keep port 8000's visibility **Private**. Clicking the globe does
   not make it public. A Private forwarded address still requires your
   GitHub login to open.

### What if two ports are shown?

- **Only 8000 is normal.** The current configuration forwards only
  8000.
- **If 9996 also appears, that is an older Codespace.** Port 9996 is
  the internal Batfish API, so opening it in a browser returns a 404.
  **A 404 there is normal.** It means Batfish is listening; it does
  not mean Live is broken. Live works through port 8000 alone: the web
  app talks to Batfish on 9996 inside the Codespace.

## 3. Running a live scenario

1. At the top of the web app, choose a **language**: Korean or
   English. Screen text and explanation language change accordingly.
2. Choose a **topology**: simple demo (5 nodes) or advanced lab
   (13 nodes).
3. Choose a **scenario**. The topology diagram marks the test section:
   - **Red dashed line (animated)** = the section under test
   - **Green dashed line** = reroute path or new exit
   - Each node also shows its **ASN and IP** underneath: Loopback for
     internal nodes, announced prefix for external nodes, all taken
     from the real lab configs.
4. Select mode **Live** and click **Run validation**. Recorded replay
   works without a Batfish server, from canned reports.
5. Read the result top to bottom, in this order:
   - **Verdict**: 🟢 ALLOW (safe to change) / 🟡 REVIEW (human check) /
     🔴 BLOCK (do not change)
   - **At a glance**: broken items, unchanged count, and a
     control/protected comparison in three lines. For scenarios with a
     control run and a protected run (like RPKI), this one line shows
     whether the route-map blocked the invalid announcement.
   - **Explanation / Proposed next step**: the explanation and
     proposal that follow the verdict.
   - **Changed evidence**: only the broken routes/flows, in a table.
   - **CLI-style view**: collapsed. Expand it only when you need it.
     It renders Batfish evidence like router output; it is NOT actual
     device output.

### About the verdict (important)

The verdict comes **only from Batfish evidence**. AI never decides
the verdict. AI only explains and proposes after the verdict. Check
the source line:

- Explanation source `Meta Model API` means the model wrote the
  explanation from the evidence.
- Explanation source `local-template (no API call)` means no key is
  configured, so a pre-written template was used instead.
- Proposal source `Meta Model API (refined from rule-based proposal)`
  means the model refined a rule-based proposal.

## 4. Reopening, stopping, and deleting

### Reopening (click the existing Codespace, not +)

- Go to the repository → Code → Codespaces tab, and **click the
  existing Codespace's name**. Clicking the name itself starts it.
  There is no separate ▶ start button.
- Or open the **...** menu next to the name and choose **Start
  codespace**.
- The same works at https://github.com/codespaces.
- **Reopening an existing Codespace takes 2–5 minutes**, unlike the
  10–15 minutes for a new one. That is why you should keep the
  Codespace you created instead of deleting it and making a new one.

### Stopping

- Closing the browser tab does not stop it immediately. After a
  period of inactivity it stops automatically (30 minutes by default).
- To stop it yourself, go to the Codespaces list, open the **...**
  menu for that Codespace, and choose **Stop codespace**.
- Stopping usually takes under a minute. If it still shows
  "Stopping..." for a long time, refresh the browser (F5) and check
  the status at https://github.com/codespaces.

### Deleting

- In the Codespaces list, open **...** and choose **Delete**.
- **Caution**: before deleting, check the terminal with
  `git status` for uncommitted changes in that Codespace. Uncommitted
  work is lost on delete. Committed work is already in the repository,
  so it is safe.
- Codespace names (like `dark crematorium`) are random names GitHub
  assigns; they mean nothing. Tell a new Codespace from an old one by
  the number of forwarded ports.

## 5. Costs (personal accounts)

- A GitHub Free personal account includes **120 core-hours + 15 GB
  of storage per month** free. GitHub Pro includes 180 core-hours +
  20 GB.
- Compute time is core count × active time. One hour on a 2-core
  Codespace consumes 2 core-hours, so the Free quota is **60 real
  hours** on a 2-core machine.
- Compute is charged **only while the Codespace is running**. A
  stopped Codespace incurs no compute charge. Storage is charged while
  a Codespace exists (even when stopped). This demo repository is
  small, so it fits comfortably inside the 15 GB quota.
- If you have not registered a payment method, usage is simply
  blocked once the quota is used up. No money is charged automatically.
  If you have registered a payment method and exceed the quota, you
  are billed from then on (around $0.18 per hour for 2 cores, and
  $0.07 per GB per month for storage).
- Keeping two Codespaces running doubles compute consumption, so Stop
  or Delete the one you are not using.
- Check usage under GitHub Settings → Billing, and the Codespace list
  at https://github.com/codespaces.

## 6. Region (there is no Korea datacenter)

- A Codespace's region is chosen automatically based on location.
  The closest option from Korea is Southeast Asia (Singapore).
  There is no Korea datacenter for Codespaces.
- Install/download speed depends on the Codespace server's internet
  connection, not on your home internet. Being in Korea does not make
  installation slow by itself.
- To fix the region manually, go to your GitHub profile → Settings →
  Codespaces → Region, choose Set manually, and select Southeast Asia.

## 7. Turning on Meta AI explanations (optional)

The verdict and live validation work fully without a key; only the
explanation falls back to rule-based text. To see real Meta AI
explanations:

1. Find your API key at dev.meta.ai. **Never paste a key into chat
   or into a repository file.**
2. On github.com, go to the repository → Settings → Secrets and
   variables → Codespaces → New codespace secret. Name it
   `META_API_KEY` and set its value to the key.
3. Stop the Codespace and start it again. An already-running web app
   cannot pick up the key.
4. Run Live again. The explanation source should now read
   `Meta Model API`.
- For a one-off test, you can also export the key in the Codespace
  terminal and restart the web app. That does not persist after the
  Codespace stops, and the key remains in terminal history, so the
  Secrets method above is the proper one.
- Turning on the key does not change the verdict. The verdict still
  comes only from Batfish evidence. Token cost per scenario is tiny,
  on the order of one cent.

## 8. Troubleshooting (common symptoms)

| Symptom | Cause / fix |
|---|---|
| Topology / scenario selection does not appear at all | Old JavaScript is cached, or the code was not pulled. In the Codespace terminal run `git pull`, then **hard-refresh the browser (Ctrl+Shift+R)**. If it still does not appear, restart the web app. (`pkill -f "web/app.py"`, then `bash scripts/start-live.sh`) |
| Live returns 503 | Batfish is not ready yet. Wait a moment and try again, or run `bash scripts/start-live.sh` in the terminal. If it still fails, check `docker logs batfish`. |
| postStart looks stuck for a long time | Batfish startup/parsing may be in progress. Check View Creation Log to see where it stopped. A first creation can take 10–15 minutes. If the same line does not move for 20–25 minutes, Stop and start it once more. |
| Opening port 9996 shows 404 | Normal. 9996 is not a web page; it is the internal Batfish API. Open only port 8000. |
| Installation repeats every time | You are creating a new Codespace each time, not reopening the existing one. Click the existing name, not +. |
| Explanation is only rule-based text | No key is configured. Follow section 7 (Secrets). |
| No start icon is visible | There is no separate start button. Clicking the Codespace name starts it. |

## 9. Safety rules (please follow them)

- This demo server is local-only (127.0.0.1) with no authentication.
  **Do not change port 8000 to Public.**
- All demo data is fictional (RFC 5737, AS 64496–64501). Never paste
  real production settings, real customer prefixes, or real company
  configs into a public demo.
- Never put API keys or passwords in repository files, chat messages,
  or screenshots. Manage keys only through Codespaces Secrets.
- This tool only validates. It never applies a change to a router,
  and a human makes the final decision. A verdict is valid only within
  its watched scope.

## 10. Quick summary (all you need to remember)

1. Code → Codespaces → Create codespace (first time: 10–15 minutes)
2. PORTS tab → globe icon on port 8000 (keep it Private)
3. Choose language → topology → scenario → Live → Run validation
4. Read in order: verdict → at a glance → explanation/proposal
5. Next time, click the existing Codespace name (2–5 minutes); + means
   creating a new one
