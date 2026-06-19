import json, time
from scraper import fetch_all_jobs

def handler(request, response):
    """Vercel serverless function returning job listings as JSON.
    The `request` object is a Vercel request, `response` provides helper methods.
    """
    try:
        jobs = fetch_all_jobs()
        payload = {
            "status": "success",
            "count": len(jobs),
            "last_updated": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),
            "jobs": jobs,
        }
        return response.json(payload)
    except Exception as e:
        return response.json({"status": "error", "message": str(e)}, status_code=500)
