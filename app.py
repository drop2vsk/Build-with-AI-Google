from flask import Flask, jsonify, render_template, request
import time
from scraper import fetch_all_jobs

app = Flask(__name__)

# Simple in-memory cache to prevent constant scraping and rate limits
cached_jobs = []
last_fetched_time = 0
CACHE_DURATION = 600  # 10 minutes cache

def get_jobs_data(force_refresh=False):
    global cached_jobs, last_fetched_time
    current_time = time.time()

    # Refresh if cache is empty, expired, or force_refresh is True
    if not cached_jobs or (current_time - last_fetched_time > CACHE_DURATION) or force_refresh:
        print("[App] Fetching fresh job listings...")
        try:
            cached_jobs = fetch_all_jobs()
            last_fetched_time = current_time
        except Exception as e:
            print(f"[App] Error in fetching jobs: {e}")
            # If fetch fails but we have old cached jobs, keep them
            if not cached_jobs:
                cached_jobs = []
    else:
        print("[App] Serving jobs from cache.")
        
    return cached_jobs

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/jobs')
def api_jobs():
    jobs = get_jobs_data()
    return jsonify({
        "status": "success",
        "count": len(jobs),
        "last_updated": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(last_fetched_time)),
        "jobs": jobs
    })

@app.route('/api/refresh')
def api_refresh():
    jobs = get_jobs_data(force_refresh=True)
    return jsonify({
        "status": "success",
        "count": len(jobs),
        "last_updated": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(last_fetched_time)),
        "jobs": jobs
    })

# Vercel exports the Flask app as a WSGI callable "app" automatically.
# No need for the __main__ block; Vercel will handle the server lifecycle.
