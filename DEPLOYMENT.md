# Deployment guide for Lokkatha Orchestrator

The project has two deployable parts with very different hosting needs:

| Piece | What it is | Where it can run |
|---|---|---|
| `frontend/` | React + Vite dashboard (static bundle) | **Vercel / Netlify / any static host** |
| API server (`app/api/run_server.py`) | Long-running Python asyncio server: crawl workers, robots politeness waits, SSE streams | **NOT serverless** — needs a VM / container (Fly.io, Railway, Render, a VPS, or your own machine) |

Serverless platforms (Vercel/Netlify functions) terminate requests in seconds and
do not allow streaming connections or 15-minute crawls, so the crawler backend
must run somewhere persistent.

## 1. Deploy the dashboard to Vercel

From the repository root:

```bash
cd frontend
npm i -g vercel        # once
vercel login           # opens the browser
vercel --prod
```

Or connect the GitHub repo at vercel.com → New Project → set:

- **Root Directory:** `frontend`
- **Framework Preset:** Vite
- **Build Command:** `npm run build`
- **Output Directory:** `dist`

Then add the environment variable:

```
VITE_API_BASE_URL = https://<your-backend-host>     # e.g. https://lokkatha-api.fly.dev
```

- Leave it **unset** for local dev (vite proxies `/api` to `127.0.0.1:8000`).
- Set it to your deployed backend URL for the production build.
- Redeploy after changing it — Vite bakes env vars in at build time.

## 2. Host the API somewhere persistent (pick one)

```bash
# Fly.io (example)
fly launch --no-deploy
fly deploy           # add a Dockerfile exposing port 8080:
#   CMD python -m app.api.run_server --host 0.0.0.0 --port 8080

# Railway / Render: create a Python service with
#   start command: python -m app.api.run_server --host 0.0.0.0 --port $PORT
```

The API server already sends CORS headers (`Access-Control-Allow-Origin: *`),
so the deployed dashboard can talk to it cross-origin.

> Security note: the API currently has no auth. Anyone who discovers the URL
> can start crawls. Before exposing it publicly, put it behind a proxy with
> basic auth or add a token check.

## 3. Local development (unchanged)

```bash
python -m app.api.run_server            # terminal 1 → :8000
cd frontend && npm run dev              # terminal 2 → :5173
```
