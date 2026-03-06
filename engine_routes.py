import json, os, threading, time
from flask import request, jsonify

def register_engine_routes(app):

    # Auto-run engine 90 seconds after Flask starts
    def auto_run():
        try:
            time.sleep(90)
            print("🚀 Content engine firing...")
            import sys, importlib
            sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
            ce = importlib.import_module("content_engine")
            ce.run_engine()
        except Exception as e:
            print(f"Auto-run error (non-fatal): {e}")
            # Never crash Flask

    t = threading.Thread(target=auto_run, daemon=True)
    t.daemon = True
    t.start()
    print("✅ Content engine scheduled (90s)")

    @app.route("/api/content-engine/run", methods=["POST","OPTIONS"])
    def content_engine_run():
        if request.method == "OPTIONS":
            return jsonify({"ok":True})
        auth = request.headers.get("X-Admin-Key","") or (request.get_json(silent=True) or {}).get("admin_key","")
        if auth != os.environ.get("ADMIN_KEY","srd_admin_2024"):
            return jsonify({"error":"Unauthorized"}), 401
        def run_async():
            try:
                import importlib, sys
                sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
                ce = importlib.import_module("content_engine")
                ce.run_engine()
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
