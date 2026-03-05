import json, os, threading
from flask import request, jsonify

def register_engine_routes(app):
    # Auto-run engine on startup with random delay (1-6 hours)
    import time, random
    def auto_run():
        delay = random.randint(60, 6 * 60 * 60)  # 1 min to 6 hours
        print(f"⏰ Content engine will auto-run in {delay//60} minutes")
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