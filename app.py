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

# ── SHARED: PAGE LOADER (exact Shopify Savor theme snippet) ──────────────────

PAGE_LOADER = """<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;1,300;1,400&display=swap" rel="stylesheet">
<style>
  #srd-loader{position:fixed;inset:0;background:#f0ebe8;z-index:99999;display:flex;align-items:center;justify-content:center;}
  #srd-loader-canvas{position:absolute;inset:0;width:100%;height:100%;}
  .srd-logo-wrap{position:relative;z-index:2;display:flex;flex-direction:column;align-items:center;gap:18px;opacity:0;animation:srdLogoReveal 1.2s cubic-bezier(0.22,1,0.36,1) 0.4s forwards;}
  .srd-emblem{width:72px;height:72px;}
  .srd-divider-line{width:48px;height:1px;background:linear-gradient(90deg,transparent,#c1a3a2,transparent);opacity:0;animation:srdFadeIn 0.8s ease 1.0s forwards;}
  .srd-brand-script{font-family:'Cormorant Garamond',serif;font-style:italic;font-weight:300;font-size:clamp(13px,2vw,16px);letter-spacing:0.32em;text-transform:uppercase;color:#9d7f6a;opacity:0;animation:srdFadeUp 0.8s ease 1.1s forwards;}
  .srd-dot-row{position:absolute;bottom:44px;left:50%;transform:translateX(-50%);display:flex;gap:7px;z-index:3;opacity:0;animation:srdFadeUp 0.6s ease 1.3s forwards;}
  .srd-dot{width:4px;height:4px;border-radius:50%;background:rgba(193,163,162,0.25);transition:background 0.3s ease,transform 0.3s ease;}
  .srd-dot.active{background:#c1a3a2;transform:scale(1.4);}
  #srd-loader.srd-exit{animation:srdDissolve 0.9s cubic-bezier(0.4,0,0.2,1) forwards;}
  @keyframes srdLogoReveal{0%{opacity:0;transform:scale(0.92)}100%{opacity:1;transform:scale(1)}}
  @keyframes srdFadeIn{to{opacity:1}}
  @keyframes srdFadeUp{0%{opacity:0;transform:translateY(6px)}100%{opacity:1;transform:translateY(0)}}
  @keyframes srdDissolve{0%{opacity:1;transform:scale(1)}100%{opacity:0;transform:scale(1.04)}}
</style>
<div id="srd-loader">
  <canvas id="srd-loader-canvas"></canvas>
  <div class="srd-logo-wrap">
    <svg class="srd-emblem" viewBox="0 0 72 72" fill="none">
      <circle cx="36" cy="36" r="34" stroke="#c1a3a2" stroke-width="0.6" opacity="0.5"/>
      <circle cx="36" cy="36" r="26" stroke="#c1a3a2" stroke-width="0.4" opacity="0.3"/>
      <path d="M28 14 C26 22,32 28,30 36 C28 44,22 48,24 58" stroke="#c1a3a2" stroke-width="1.2" stroke-linecap="round" fill="none" opacity="0.9"/>
      <path d="M36 12 C35 20,39 26,37 36 C35 46,31 50,33 60" stroke="#9d7f6a" stroke-width="1.4" stroke-linecap="round" fill="none"/>
      <path d="M44 14 C46 22,40 28,42 36 C44 44,50 48,48 58" stroke="#c1a3a2" stroke-width="1.2" stroke-linecap="round" fill="none" opacity="0.9"/>
      <path d="M31 13 C29 21,34 27,33 35 C32 43,27 47,28 57" stroke="#d4b8b4" stroke-width="0.5" stroke-linecap="round" fill="none" opacity="0.5"/>
      <path d="M41 13 C43 21,38 27,39 35 C40 43,45 47,44 57" stroke="#d4b8b4" stroke-width="0.5" stroke-linecap="round" fill="none" opacity="0.5"/>
      <circle cx="36" cy="8" r="1.2" fill="#c1a3a2" opacity="0.6"/>
      <circle cx="36" cy="64" r="1.2" fill="#c1a3a2" opacity="0.6"/>
      <circle cx="8" cy="36" r="0.8" fill="#c1a3a2" opacity="0.4"/>
      <circle cx="64" cy="36" r="0.8" fill="#c1a3a2" opacity="0.4"/>
    </svg>
    <div class="srd-divider-line"></div>
    <div class="srd-brand-script">Professional Hair Care</div>
  </div>
  <div class="srd-dot-row">
    <div class="srd-dot" id="srd-d0"></div>
    <div class="srd-dot" id="srd-d1"></div>
    <div class="srd-dot" id="srd-d2"></div>
    <div class="srd-dot" id="srd-d3"></div>
    <div class="srd-dot" id="srd-d4"></div>
  </div>
</div>
<script>
(function(){
  var cv=document.getElementById('srd-loader-canvas'),ctx=cv.getContext('2d');
  function rsz(){cv.width=window.innerWidth;cv.height=window.innerHeight;}rsz();
  window.addEventListener('resize',rsz);
  function S(){this.i();}
  S.prototype.i=function(){this.x=Math.random()*cv.width;this.y=-60-Math.random()*200;this.len=100+Math.random()*200;this.wave=(Math.random()-.5)*40;this.spd=.18+Math.random()*.35;this.w=.3+Math.random()*.8;this.a=.04+Math.random()*.10;this.off=Math.random()*Math.PI*2;this.dr=(Math.random()-.5)*.3;var c=[[193,163,162],[157,127,106],[210,185,178],[180,155,145]];this.rgb=c[Math.floor(Math.random()*c.length)];};
  S.prototype.u=function(){this.y+=this.spd;this.x+=this.dr;if(this.y>cv.height+60)this.i();};
  S.prototype.d=function(t){var n=20;ctx.beginPath();ctx.moveTo(this.x,this.y);for(var i=1;i<=n;i++){var p=i/n;ctx.lineTo(this.x+Math.sin(p*Math.PI*2+t*.008+this.off)*this.wave*p,this.y+p*this.len);}ctx.strokeStyle='rgba('+this.rgb[0]+','+this.rgb[1]+','+this.rgb[2]+','+this.a+')';ctx.lineWidth=this.w;ctx.lineCap='round';ctx.stroke();};
  var ss=[];for(var i=0;i<55;i++){var s=new S();s.y=Math.random()*cv.height;ss.push(s);}
  var t=0;function ani(){t++;ctx.clearRect(0,0,cv.width,cv.height);ss.forEach(function(s){s.u();s.d(t);});requestAnimationFrame(ani);}ani();
  var ds=[0,1,2,3,4].map(function(i){return document.getElementById('srd-d'+i);});
  var st=0;[600,1200,1900,2800,3800].forEach(function(ms){setTimeout(function(){ds.forEach(function(d){d.classList.remove('active');});if(ds[st])ds[st].classList.add('active');st++;},ms);});
  var ex=false;
  function doExit(){if(ex)return;ex=true;ds.forEach(function(d){d.classList.add('active');});setTimeout(function(){var el=document.getElementById('srd-loader');el.classList.add('srd-exit');setTimeout(function(){el.style.display='none';},900);},200);}
  window.addEventListener('load',function(){setTimeout(doExit,1200);});
  setTimeout(doExit,4500);
})();
</script>"""

# ── SHARED: NAV (exact Savor theme header structure) ─────────────────────────

NAV_CSS = """
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Jost',sans-serif;background:#f0ebe8;color:#0d0906;min-height:100vh}
#header-component{position:sticky;top:0;z-index:1000;background:#fff;border-bottom:1px solid rgba(0,0,0,0.08);}
.header{display:flex;align-items:center;justify-content:space-between;max-width:1200px;margin:0 auto;padding:0 32px;height:64px;}
.header__column--left{display:flex;align-items:center;gap:8px;}
.header__logo a{font-family:'Cormorant Garamond',serif;font-size:22px;font-style:italic;color:#0d0906;text-decoration:none;letter-spacing:0.04em;white-space:nowrap;}
.header__column--center{display:flex;align-items:center;flex:1;justify-content:center;}
.menu-list{display:flex;list-style:none;gap:0;margin:0;padding:0;align-items:center;}
.menu-list__list-item{position:relative;}
.menu-list__link{display:flex;align-items:center;padding:0 14px;height:64px;text-decoration:none;color:#0d0906;font-family:'Jost',sans-serif;font-size:12px;font-weight:500;letter-spacing:0.10em;text-transform:uppercase;transition:color 0.2s;white-space:nowrap;}
.menu-list__link:hover{color:#c1a3a2;}
.menu-list__link--active{color:#c1a3a2;box-shadow:inset 0 -2px 0 #c1a3a2;}
.header__column--right{display:flex;align-items:center;}
header-actions{display:flex;align-items:center;}
.header-actions__action{display:flex;align-items:center;justify-content:center;color:#0d0906;opacity:0.65;text-decoration:none;padding:0 10px;height:64px;position:relative;transition:opacity 0.2s;background:none;border:none;cursor:pointer;}
.header-actions__action:hover{opacity:1;}
.header-actions__action svg{width:20px;height:20px;display:block;}
.header-actions__cart-icon{position:relative;}
.cart-bubble{position:absolute;top:12px;right:6px;background:#c1a3a2;color:#fff;font-size:9px;font-family:'Jost',sans-serif;min-width:16px;height:16px;border-radius:8px;display:none;align-items:center;justify-content:center;padding:0 3px;}
.cart-bubble.visible{display:flex;}
.header-drawer-trigger{display:none;background:none;border:none;cursor:pointer;padding:10px;color:#0d0906;}
@media(max-width:768px){
  .header__column--center{display:none;}
  .header-drawer-trigger{display:flex;align-items:center;}
  .header{padding:0 16px;}
}
.menu-drawer-overlay{display:none;position:fixed;inset:0;background:rgba(0,0,0,0.4);z-index:9998;opacity:0;transition:opacity 0.3s;}
.menu-drawer-overlay.open{display:block;opacity:1;}
.menu-drawer{position:fixed;top:0;left:0;height:100dvh;width:280px;background:#fff;z-index:9999;transform:translateX(-100%);transition:transform 0.3s ease;display:flex;flex-direction:column;overflow-y:auto;box-shadow:4px 0 20px rgba(0,0,0,0.12);}
.menu-drawer.open{transform:translateX(0);}
.menu-drawer__close-button{display:flex;justify-content:flex-end;padding:20px 20px 8px;background:none;border:none;cursor:pointer;color:#0d0906;font-size:20px;align-self:flex-end;}
.menu-drawer__menu{list-style:none;padding:0 0 24px;margin:0;}
.menu-drawer__menu-item{display:flex;align-items:center;padding:14px 28px;text-decoration:none;color:#0d0906;font-family:'Jost',sans-serif;font-size:12px;font-weight:500;letter-spacing:0.10em;text-transform:uppercase;border-bottom:1px solid rgba(193,163,162,0.12);transition:color 0.2s;}
.menu-drawer__menu-item:hover,.menu-drawer__menu-item.active{color:#c1a3a2;}
"""

NAV_HTML = """<div class="menu-drawer-overlay" id="srd-overlay" onclick="srdCloseDrawer()"></div>
<div class="menu-drawer" id="srd-drawer">
  <button class="menu-drawer__close-button" onclick="srdCloseDrawer()" aria-label="Close menu">&#10005;</button>
  <ul class="menu-drawer__menu">
    <li><a href="https://supportrd.com" class="menu-drawer__menu-item">Home</a></li>
    <li><a href="https://supportrd.com/collections/all" class="menu-drawer__menu-item">Catalog</a></li>
    <li><a href="https://supportrd.com/pages/contact" class="menu-drawer__menu-item">Contact</a></li>
    <li><a href="https://supportrd.com/pages/hair-dashboard" class="menu-drawer__menu-item">Dashboard</a></li>
    <li><a href="https://supportrd.com/pages/custom-order" class="menu-drawer__menu-item">Custom Order</a></li>
    <li><a href="https://hairtips.supportrd.com/blog" class="menu-drawer__menu-item active">Blog</a></li>
  </ul>
</div>
<div id="header-component">
  <div class="header">
    <div class="header__column--left">
      <button class="header-drawer-trigger" onclick="srdOpenDrawer()" aria-label="Open menu">
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="18" x2="21" y2="18"/></svg>
      </button>
      <div class="header__logo"><a href="https://supportrd.com">SupportRD</a></div>
    </div>
    <div class="header__column--center">
      <ul class="menu-list" role="list" aria-label="Primary navigation">
        <li class="menu-list__list-item"><a href="https://supportrd.com" class="menu-list__link"><span class="menu-list__link-title">Home</span></a></li>
        <li class="menu-list__list-item"><a href="https://supportrd.com/collections/all" class="menu-list__link"><span class="menu-list__link-title">Catalog</span></a></li>
        <li class="menu-list__list-item"><a href="https://supportrd.com/pages/contact" class="menu-list__link"><span class="menu-list__link-title">Contact</span></a></li>
        <li class="menu-list__list-item"><a href="https://supportrd.com/pages/hair-dashboard" class="menu-list__link"><span class="menu-list__link-title">Dashboard</span></a></li>
        <li class="menu-list__list-item"><a href="https://supportrd.com/pages/custom-order" class="menu-list__link"><span class="menu-list__link-title">Custom Order</span></a></li>
        <li class="menu-list__list-item"><a href="https://hairtips.supportrd.com/blog" class="menu-list__link menu-list__link--active"><span class="menu-list__link-title">Blog</span></a></li>
      </ul>
    </div>
    <div class="header__column--right">
      <header-actions>
        <a href="https://supportrd.com/search" class="header-actions__action" aria-label="Search">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
        </a>
        <a href="https://supportrd.com/account/login" class="header-actions__action" aria-label="Account">
          <svg viewBox="0 0 15 17" fill="none" width="15" height="17"><path stroke="currentColor" stroke-linejoin="round" stroke-width="1.3" d="M10.375 3.813a3.063 3.063 0 1 1-6.125 0 3.063 3.063 0 0 1 6.125 0ZM7.313 9.5c-3.667 0-6.24 2.691-6.563 6.125h13.125C13.552 12.191 10.979 9.5 7.312 9.5Z"/></svg>
        </a>
        <a href="https://supportrd.com/cart" class="header-actions__action header-actions__cart-icon" aria-label="Cart">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><path d="M6 2L3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4z"/><line x1="3" y1="6" x2="21" y2="6"/><path d="M16 10a4 4 0 0 1-8 0"/></svg>
          <span class="cart-bubble" id="cart-count"></span>
        </a>
      </header-actions>
    </div>
  </div>
</div>
<script>
function srdOpenDrawer(){document.getElementById('srd-drawer').classList.add('open');document.getElementById('srd-overlay').classList.add('open');document.body.style.overflow='hidden';}
function srdCloseDrawer(){document.getElementById('srd-drawer').classList.remove('open');document.getElementById('srd-overlay').classList.remove('open');document.body.style.overflow='';}
fetch("https://supportrd.com/cart.js").then(function(r){return r.json();}).then(function(d){if(d.item_count>0){var el=document.getElementById('cart-count');if(el){el.textContent=d.item_count;el.classList.add('visible');}}}).catch(function(){});
</script>"""

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
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,600;1,300;1,400&family=Jost:wght@300;400;500&display=swap" rel="stylesheet">
{PAGE_LOADER}
<style>
{NAV_CSS}
.header-brand{{text-align:center;padding:48px 24px 36px;background:#f0ebe8;}}
.header-brand h1{{font-family:'Cormorant Garamond',serif;font-size:clamp(32px,5vw,48px);font-style:italic;font-weight:400;color:#0d0906;}}
.header-brand p{{font-size:13px;color:rgba(0,0,0,0.4);margin-top:10px;letter-spacing:0.10em;text-transform:uppercase;}}
.container{{max-width:900px;margin:0 auto;padding:40px 24px;}}
.section-label{{font-size:11px;color:#c1a3a2;letter-spacing:0.18em;text-transform:uppercase;margin-bottom:10px;}}
.section-title{{font-family:'Cormorant Garamond',serif;font-size:30px;font-style:italic;margin-bottom:28px;color:#0d0906;}}
.post-card{{background:#fff;border-radius:16px;margin-bottom:20px;transition:transform 0.2s,box-shadow 0.2s;box-shadow:0 2px 12px rgba(0,0,0,0.05);border:1px solid rgba(193,163,162,0.12);}}
.post-card:hover{{transform:translateY(-3px);box-shadow:0 8px 28px rgba(0,0,0,0.10);}}
.post-card a{{display:block;padding:28px 32px;text-decoration:none;color:inherit;}}
.post-card h2{{font-family:'Cormorant Garamond',serif;font-size:24px;color:#0d0906;margin-bottom:8px;line-height:1.3;}}
.post-card .meta{{font-size:13px;color:rgba(0,0,0,0.45);line-height:1.6;margin-bottom:12px;}}
.post-card .date{{font-size:11px;color:#c1a3a2;letter-spacing:0.08em;}}
.empty{{text-align:center;color:rgba(0,0,0,0.3);padding:60px;font-size:14px;}}
footer{{text-align:center;padding:40px;font-size:12px;color:rgba(0,0,0,0.3);border-top:1px solid rgba(193,163,162,0.12);}}
footer a{{color:#c1a3a2;text-decoration:none;}}
</style>
</head>
<body>
{NAV_HTML}
<div class="header-brand">
  <h1>Hair Care Journal</h1>
  <p>Expert tips, routines and advice from SupportRD</p>
</div>
<div class="container">
  <div class="section-label">&#10022; Expert guides</div>
  <div class="section-title">Latest Articles</div>
  {cards}
</div>
<footer><a href="https://supportrd.com">← Back to SupportRD</a> &nbsp;·&nbsp; <a href="https://ai-hair-advisor.onrender.com">Try Aria AI →</a></footer>
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
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,600;1,300;1,400&family=Jost:wght@300;400;500&display=swap" rel="stylesheet">
{PAGE_LOADER}
<style>
{NAV_CSS}
.container{{max-width:720px;margin:0 auto;padding:48px 24px;}}
.post-date{{font-size:11px;color:#c1a3a2;letter-spacing:0.10em;margin-bottom:16px;text-transform:uppercase;}}
.post-body{{background:#fff;border-radius:20px;padding:48px;box-shadow:0 2px 20px rgba(0,0,0,0.06);line-height:1.8;font-size:15px;border:1px solid rgba(193,163,162,0.12);}}
.post-body h1{{font-family:'Cormorant Garamond',serif;font-size:36px;font-style:italic;font-weight:400;margin-bottom:24px;line-height:1.2;color:#0d0906;}}
.post-body h2{{font-family:'Cormorant Garamond',serif;font-size:24px;font-weight:400;margin:32px 0 12px;color:#0d0906;}}
.post-body p{{margin-bottom:16px;color:rgba(0,0,0,0.75);}}
.post-body a{{color:#c1a3a2;}}
.cta{{background:linear-gradient(135deg,#c1a3a2,#9d7f6a);color:#fff;text-align:center;padding:36px;border-radius:16px;margin-top:32px;}}
.cta h3{{font-family:'Cormorant Garamond',serif;font-size:26px;font-style:italic;font-weight:400;margin-bottom:8px;}}
.cta p{{font-size:13px;opacity:0.9;line-height:1.6;}}
.cta a{{display:inline-block;margin-top:16px;padding:12px 28px;background:#fff;color:#c1a3a2;border-radius:30px;text-decoration:none;font-size:11px;letter-spacing:0.14em;text-transform:uppercase;font-family:'Jost',sans-serif;}}
footer{{text-align:center;padding:32px;font-size:12px;color:rgba(0,0,0,0.3);border-top:1px solid rgba(193,163,162,0.12);}}
footer a{{color:#c1a3a2;text-decoration:none;}}
@media(max-width:600px){{.post-body{{padding:28px 20px;}}}}
</style>
</head>
<body>
{NAV_HTML}
<div class="container">
  <div class="post-date">{date}</div>
  <div class="post-body">{post['html']}</div>
  <div class="cta">
    <h3>Get your personalized hair routine</h3>
    <p>Tell Aria about your hair and get expert advice tailored to you.</p>
    <a href="https://ai-hair-advisor.onrender.com">Chat with Aria Free →</a>
  </div>
</div>
<footer><a href="https://supportrd.com">SupportRD</a> &nbsp;·&nbsp; <a href="/blog">← More Articles</a></footer>
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
