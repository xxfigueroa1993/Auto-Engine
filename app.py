import os, json, datetime, threading, random, re
from flask import Flask, request, jsonify, Response

app = Flask(__name__)

HAIR_ADVISOR_URL = "https://ai-hair-advisor.onrender.com"

# ── FETCH BLOG FROM AI-HAIR-ADVISOR ──────────────────────────────────────────

def fetch_blog_posts():
    import urllib.request as urlreq
    try:
        req = urlreq.Request(f"{HAIR_ADVISOR_URL}/api/blog-posts",
                             headers={"User-Agent": "auto-engine/1.0"})
        with urlreq.urlopen(req, timeout=8) as r:
            return json.loads(r.read().decode())
    except Exception as e:
        print(f"Blog fetch error: {e}")
        return []

def fetch_blog_post(handle):
    import urllib.request as urlreq
    try:
        req = urlreq.Request(f"{HAIR_ADVISOR_URL}/api/blog-post/{handle}",
                             headers={"User-Agent": "auto-engine/1.0"})
        with urlreq.urlopen(req, timeout=8) as r:
            return json.loads(r.read().decode())
    except Exception as e:
        print(f"Blog post fetch error: {e}")
        return None

# ── BLOG INDEX ────────────────────────────────────────────────────────────────

@app.route("/blog")
def blog_index():
    posts = fetch_blog_posts()

    cards = ""
    for p in posts:
        date = p.get("date","")[:10]
        cards += f"""
        <article class="post-card">
          <a href="/blog/{p['handle']}">
            <h2>{p['title']}</h2>
            <p class="meta">{p.get('meta','')}</p>
            <span class="date">{date}</span>
          </a>
        </article>"""

    if not cards:
        cards = '<p class="empty">No posts yet — check back soon.</p>'

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Hair Care Journal — SupportRD</title>
<meta name="description" content="Expert hair care tips, routines and advice from SupportRD.">
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,600;1,400&family=Jost:wght@300;400;500&display=swap" rel="stylesheet">
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:'Jost',sans-serif;background:#f0ebe8;color:#0d0906;min-height:100vh}}
header{{background:#fff;border-bottom:1px solid rgba(193,163,162,0.2)}}
.site-nav{{display:flex;justify-content:space-between;align-items:center;padding:14px 32px;border-bottom:1px solid rgba(193,163,162,0.15)}}
.nav-left{{display:flex;gap:24px;flex-wrap:wrap;align-items:center}}
.nav-right{{display:flex;gap:18px;align-items:center}}
.site-nav a{{font-family:'Jost',sans-serif;font-size:12px;letter-spacing:0.12em;text-transform:uppercase;color:#0d0906;text-decoration:none;opacity:0.6;transition:opacity 0.2s}}
.site-nav a:hover,.site-nav a.active{{opacity:1;color:#c1a3a2}}
.nav-right a{{opacity:0.6;display:flex;align-items:center;position:relative}}
.nav-right a:hover{{opacity:1}}
.cart-count{{position:absolute;top:-6px;right:-8px;background:#c1a3a2;color:#fff;font-size:9px;width:14px;height:14px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-family:'Jost',sans-serif}}
.header-brand{{text-align:center;padding:40px 24px 32px}}
.header-brand h1{{font-family:'Cormorant Garamond',serif;font-size:42px;font-style:italic;color:#0d0906}}
.header-brand p{{font-size:13px;color:rgba(0,0,0,0.4);margin-top:8px;letter-spacing:0.08em}}
.container{{max-width:900px;margin:0 auto;padding:40px 24px}}
.section-label{{font-size:11px;color:#c1a3a2;letter-spacing:0.14em;text-transform:uppercase;margin-bottom:12px}}
.section-title{{font-family:'Cormorant Garamond',serif;font-size:30px;font-style:italic;margin-bottom:24px;color:#0d0906}}
.post-card{{background:#fff;border-radius:16px;margin-bottom:20px;transition:transform 0.2s;box-shadow:0 2px 12px rgba(0,0,0,0.06)}}
.post-card:hover{{transform:translateY(-2px)}}
.post-card a{{display:block;padding:28px 32px;text-decoration:none;color:inherit}}
.post-card h2{{font-family:'Cormorant Garamond',serif;font-size:24px;color:#0d0906;margin-bottom:8px;line-height:1.3}}
.post-card .meta{{font-size:13px;color:rgba(0,0,0,0.45);line-height:1.6;margin-bottom:12px}}
.post-card .date{{font-size:11px;color:#c1a3a2;letter-spacing:0.08em}}
.empty{{text-align:center;color:rgba(0,0,0,0.3);padding:60px;font-size:14px}}
footer{{text-align:center;padding:40px;font-size:12px;color:rgba(0,0,0,0.3)}}
footer a{{color:#c1a3a2;text-decoration:none}}
</style>
</head>
<body>
<header>
  <nav class="site-nav">
    <div class="nav-left">
      <a href="https://supportrd.com">Home</a>
      <a href="https://supportrd.com/collections/all">Catalog</a>
      <a href="https://supportrd.com/pages/contact">Contact</a>
      <a href="https://supportrd.com/pages/hair-dashboard">Dashboard</a>
      <a href="https://supportrd.com/pages/custom-order">Custom Order</a>
      <a href="https://hairtips.supportrd.com/blog" class="active">Blog</a>
    </div>
    <div class="nav-right">
      <a href="https://supportrd.com/search" title="Search">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
      </a>
      <a href="https://supportrd.com/account/login" title="Sign In">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
      </a>
      <a href="https://supportrd.com/cart" title="Cart" class="cart-link">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M6 2L3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4z"/><line x1="3" y1="6" x2="21" y2="6"/><path d="M16 10a4 4 0 0 1-8 0"/></svg>
        <span class="cart-count" id="cart-count"></span>
      </a>
    </div>
  </nav>
  <div class="header-brand">
    <h1>Hair Care Journal</h1>
    <p>Expert tips, routines and advice from SupportRD</p>
  </div>
</header>
<div class="container">
  <div class="section-label">&#10022; Expert guides</div>
  <div class="section-title">Hair Care Journal</div>
  {cards}
</div>
<footer><a href="https://supportrd.com">← Back to SupportRD</a> &nbsp;·&nbsp; <a href="https://ai-hair-advisor.onrender.com">Try Aria AI →</a></footer>
<script>
fetch("https://supportrd.com/cart.js")
  .then(function(r){{return r.json();}})
  .then(function(d){{
    var count=d.item_count;
    if(count>0){{var el=document.getElementById("cart-count");if(el)el.textContent=count;}}
  }}).catch(function(){{}});
</script>
</body></html>"""


# ── INDIVIDUAL BLOG POST ──────────────────────────────────────────────────────

@app.route("/blog/<handle>")
def blog_post(handle):
    post = fetch_blog_post(handle)
    if not post:
        return "<h2>Post not found</h2>", 404

    date = post.get("date","")[:10]
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{post['title']} — SupportRD</title>
<meta name="description" content="{post.get('meta','')}">
<link rel="canonical" href="https://hairtips.supportrd.com/blog/{handle}">
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,600;1,400&family=Jost:wght@300;400;500&display=swap" rel="stylesheet">
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:'Jost',sans-serif;background:#f0ebe8;color:#0d0906}}
header{{background:#fff;border-bottom:1px solid rgba(193,163,162,0.2)}}
.site-nav{{display:flex;justify-content:space-between;align-items:center;padding:14px 32px;border-bottom:1px solid rgba(193,163,162,0.15)}}
.nav-left{{display:flex;gap:24px;flex-wrap:wrap;align-items:center}}
.nav-right{{display:flex;gap:18px;align-items:center}}
.site-nav a{{font-family:'Jost',sans-serif;font-size:12px;letter-spacing:0.12em;text-transform:uppercase;color:#0d0906;text-decoration:none;opacity:0.6;transition:opacity 0.2s}}
.site-nav a:hover,.site-nav a.active{{opacity:1;color:#c1a3a2}}
.nav-right a{{opacity:0.6;display:flex;align-items:center;position:relative}}
.nav-right a:hover{{opacity:1}}
.cart-count{{position:absolute;top:-6px;right:-8px;background:#c1a3a2;color:#fff;font-size:9px;width:14px;height:14px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-family:'Jost',sans-serif}}
.container{{max-width:720px;margin:0 auto;padding:48px 24px}}
.post-date{{font-size:11px;color:#c1a3a2;letter-spacing:0.1em;margin-bottom:16px}}
.post-body{{background:#fff;border-radius:20px;padding:48px;box-shadow:0 2px 20px rgba(0,0,0,0.06);line-height:1.8;font-size:15px}}
.post-body h1{{font-family:'Cormorant Garamond',serif;font-size:36px;font-style:italic;margin-bottom:24px;line-height:1.2}}
.post-body h2{{font-family:'Cormorant Garamond',serif;font-size:24px;margin:32px 0 12px}}
.post-body p{{margin-bottom:16px;color:rgba(0,0,0,0.75)}}
.post-body a{{color:#c1a3a2}}
.cta{{background:#c1a3a2;color:#fff;text-align:center;padding:32px;border-radius:16px;margin-top:32px}}
.cta h3{{font-family:'Cormorant Garamond',serif;font-size:24px;font-style:italic;margin-bottom:8px}}
.cta a{{display:inline-block;margin-top:16px;padding:12px 28px;background:#fff;color:#c1a3a2;border-radius:30px;text-decoration:none;font-size:11px;letter-spacing:0.12em;text-transform:uppercase}}
footer{{text-align:center;padding:32px;font-size:12px;color:rgba(0,0,0,0.3)}}
footer a{{color:#c1a3a2;text-decoration:none}}
</style>
</head>
<body>
<header>
  <nav class="site-nav">
    <div class="nav-left">
      <a href="https://supportrd.com">Home</a>
      <a href="https://supportrd.com/collections/all">Catalog</a>
      <a href="https://supportrd.com/pages/contact">Contact</a>
      <a href="https://supportrd.com/pages/hair-dashboard">Dashboard</a>
      <a href="https://supportrd.com/pages/custom-order">Custom Order</a>
      <a href="https://hairtips.supportrd.com/blog">Blog</a>
    </div>
    <div class="nav-right">
      <a href="https://supportrd.com/search" title="Search">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
      </a>
      <a href="https://supportrd.com/account/login" title="Sign In">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
      </a>
      <a href="https://supportrd.com/cart" title="Cart">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M6 2L3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4z"/><line x1="3" y1="6" x2="21" y2="6"/><path d="M16 10a4 4 0 0 1-8 0"/></svg>
        <span class="cart-count" id="cart-count"></span>
      </a>
    </div>
  </nav>
</header>
<div class="container">
  <div class="post-date">{date}</div>
  <div class="post-body">{post['html']}</div>
  <div class="cta">
    <h3>Get your personalized hair routine</h3>
    <p style="font-size:13px;opacity:0.9">Tell Aria about your hair and get expert advice tailored to you.</p>
    <a href="https://ai-hair-advisor.onrender.com">Chat with Aria Free →</a>
  </div>
</div>
<footer><a href="https://supportrd.com">SupportRD</a> &nbsp;·&nbsp; <a href="/blog">More Articles</a></footer>
<script>
fetch("https://supportrd.com/cart.js")
  .then(function(r){{return r.json();}})
  .then(function(d){{
    var count=d.item_count;
    if(count>0){{var el=document.getElementById("cart-count");if(el)el.textContent=count;}}
  }}).catch(function(){{}});
</script>
</body></html>"""


# ── SITEMAP ───────────────────────────────────────────────────────────────────

@app.route("/sitemap.xml")
def sitemap():
    base_url = "https://hairtips.supportrd.com"
    urls = [f"""  <url>
    <loc>{base_url}/blog</loc>
    <changefreq>daily</changefreq>
    <priority>0.8</priority>
  </url>"""]
    try:
        posts = fetch_blog_posts()
        for p in posts:
            date = p.get("date","")[:10]
            urls.append(f"""  <url>
    <loc>{base_url}/blog/{p["handle"]}</loc>
    <lastmod>{date}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.7</priority>
  </url>""")
    except:
        pass
    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{chr(10).join(urls)}
</urlset>"""
    return Response(xml, mimetype="application/xml")


# ── ROBOTS ────────────────────────────────────────────────────────────────────

@app.route("/robots.txt")
def robots():
    return Response("""User-agent: *
Allow: /blog
Disallow: /api

Sitemap: https://hairtips.supportrd.com/sitemap.xml
""", mimetype="text/plain")


# ── GOOGLE VERIFY ─────────────────────────────────────────────────────────────

@app.route("/google65f6d985572e55c5.html")
def google_verify():
    return "google-site-verification: google65f6d985572e55c5.html"


# ── PING ──────────────────────────────────────────────────────────────────────

@app.route("/api/ping", methods=["GET"])
def ping():
    return jsonify({"ok": True, "status": "awake"})


# ── CORS ──────────────────────────────────────────────────────────────────────

@app.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        from flask import make_response
        resp = make_response("", 200)
        resp.headers["Access-Control-Allow-Origin"]  = "*"
        resp.headers["Access-Control-Allow-Headers"] = "Content-Type"
        resp.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        return resp

@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"]  = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return response


# ── KEEP-ALIVE ────────────────────────────────────────────────────────────────

def _keep_alive():
    import time, urllib.request as _urlreq
    time.sleep(60)
    while True:
        time.sleep(600)
        try: _urlreq.urlopen("https://auto-engine.onrender.com/api/ping", timeout=10)
        except: pass

threading.Thread(target=_keep_alive, daemon=True).start()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
