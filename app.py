from flask import Flask, jsonify, render_template, request
import time
from scraper import fetch_all_jobs

app = Flask(__name__, static_folder="static", template_folder="templates")

# In‑memory cache for job listings
cached_jobs = []
last_fetched_time = 0
CACHE_DURATION = 600  # seconds (10 min)

def _get_jobs(force_refresh: bool = False):
    """Return cached jobs, refreshing if needed.
    Args:
        force_refresh: When True, ignore cache and scrape again.
    """
    global cached_jobs, last_fetched_time
    now = time.time()
    if force_refresh or not cached_jobs or (now - last_fetched_time > CACHE_DURATION):
        print("[Vercel] Refreshing job cache …")
        try:
            cached_jobs = fetch_all_jobs()
            last_fetched_time = now
        except Exception as exc:  # pragma: no‑cover
            print(f"[Vercel] Scraper error: {exc}")
            if not cached_jobs:
                cached_jobs = []
    else:
        print("[Vercel] Serving jobs from cache")
    return cached_jobs

# ----------------------------------------------------------------------
# UI routes
# ----------------------------------------------------------------------
@app.route("/")
def index():
    """Render the main dashboard page."""
    return render_template("index.html")

# ----------------------------------------------------------------------
# API routes (JSON)
# ----------------------------------------------------------------------
@app.route("/api/jobs")
def api_jobs():
    jobs = _get_jobs()
    return jsonify({
        "status": "success",
        "count": len(jobs),
        "last_updated": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(last_fetched_time)),
        "jobs": jobs,
    })

@app.route("/api/refresh")
def api_refresh():
    jobs = _get_jobs(force_refresh=True)
    return jsonify({
        "status": "success",
        "count": len(jobs),
        "last_updated": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(last_fetched_time)),
        "jobs": jobs,
    })

# Note: Vercel will import this file and use the `app` object as the WSGI handler.
