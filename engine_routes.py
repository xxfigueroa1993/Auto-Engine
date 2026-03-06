import json, os, threading
from flask import request, jsonify

def keep_alive():
    """Ping server every 14 min to prevent Render free tier sleep."""
    import time, urllib.request
    url = os.environ.get("RENDER_EXTERNAL_URL", "")
    if not url:
        return
    def ping():
        while True:
            time.sleep(14 * 60)
            try:
                urllib.request.urlopen(url + "/api/ping", timeout=10)
                print("✅ Keep-alive ping sent")
            except Exception as e:
                print(f"⚠️ Keep-alive failed: {e}")
    threading.Thread(target=ping, daemon=True).start()
    print("✅ Keep-alive started")

def register_engine_routes(app):
    # Auto-run engine on startup with delay so Flask starts first
    import time, random
    def auto_run():
        time.sleep(30)  # Wait 30s for Flask to fully start
        keep_alive()    # Start keep-alive after Flask is up
        delay = 60      # Then wait 1 minute before running engine
        print(f"⏰ Content engine will auto-run in 1 minute")
        time.sleep(delay)
        try:
            from content_engine import run_engine
            run_engine()
        except Exception as e:
            print(f"Auto-run error: {e}")
    threading.Thread(target=auto_run, daemon=True).start()
    print("✅ Content engine auto-run scheduled")


    @app.route("/api/content-engine/run", methods=["POST","OPTIONS"])
    def content_engine_run():
        if request.method == "OPTIONS":
            return jsonify({"ok":True})
        auth = request.headers.get("X-Admin-Key","") or (request.get_json(silent=True) or {}).get("admin_key","")
        if auth != os.environ.get("ADMIN_KEY","srd_admin_2024"):
            return jsonify({"error":"Unauthorized"}), 401
        def run_async():
            try:
                from content_engine import run_engine
                run_engine()
            except Exception as e:
                print(f"Content engine error: {e}")
        threading.Thread(target=run_async, daemon=True).start()
        return jsonify({"ok": True, "message": "Content engine started"})

    @app.route("/api/content-engine/log", methods=["GET"])
    def content_engine_log():
        auth = request.args.get("admin_key","")
        if auth != os.environ.get("ADMIN_KEY","srd_admin_2024"):
            return jsonify({"error":"Unauthorized"}), 401
        try:
            with open("/tmp/content_engine_log.json","r") as f:
                log = json.load(f)
            return jsonify({"ok": True, "runs": log[::-1]})
        except:
            return jsonify({"ok": True, "runs": [], "message": "No runs yet"})

    @app.route("/api/content-engine/status", methods=["GET"])
    def content_engine_status():
        auth = request.args.get("admin_key","")
        if auth != os.environ.get("ADMIN_KEY","srd_admin_2024"):
            return jsonify({"error":"Unauthorized"}), 401
        try:
            with open("/tmp/content_engine_log.json","r") as f:
                log = json.load(f)
            return jsonify({"ok": True, "last_run": log[-1] if log else None, "total_runs": len(log)})
        except:
            return jsonify({"ok": True, "last_run": None, "total_runs": 0})
