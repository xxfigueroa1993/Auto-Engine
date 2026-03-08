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

# ── SHARED: NAV (exact Savor theme header structure from theme files) ─────────

NAV_CSS = """
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Jost',sans-serif;background:#f0ebe8;color:#0d0906;min-height:100vh}

/* ── CSS variables from theme files ── */
:root{
  --color-foreground:#0d0906;
  --color-background:#ffffff;
  --color-border:rgba(13,9,6,0.08);
  --color-accent:#c1a3a2;
  --page-width:1200px;
  --header-padding:32px;
  --header-height:64px;
  --drawer-width:100%;
  --drawer-max-width:85vw;
  --drawer-animation-speed:0.3s;
  --icon-size-xs:20px;
  --padding-lg:16px;
  --gap-md:12px;
  --gap-xl:32px;
  /* menu-font-styles.liquid: type_font_primary_link default='heading', type_font_primary_size default='1rem', type_case_primary_link default='none' */
  --menu-top-level-font-family:'Jost',sans-serif;
  --menu-top-level-font-size:1rem;
  --menu-top-level-font-size-desktop:1rem;
  --menu-top-level-font-weight:400;
  --menu-top-level-font-style:normal;
  --menu-top-level-font-case:none;
  --menu-top-level-font-color:#0d0906;
  --menu-top-level-font-color-rgb:13,9,6;
  --menu-top-level-font-line-height:1.2;
  /* drawer uses --menu-font-2xl--size */
  --menu-top-level-font-size-drawer:1.5rem;
  --menu-horizontal-gap:var(--gap-xl,32px);
  --opacity-subdued-text:0.5;
  --layer-menu-drawer:9999;
}

/* ── #header-component — sticky wrapper (header-component.js) ── */
#header-component{
  position:sticky;top:0;z-index:1000;
  background:var(--color-background);
  border-bottom:1px solid var(--color-border);
}

/* ── .header inner row — header-row.liquid: 3-column grid ── */
.header{
  display:grid;
  grid-template-columns:1fr auto 1fr;
  align-items:stretch;
  max-width:var(--page-width,1200px);
  margin:0 auto;
  padding:0 var(--header-padding,32px);
  height:var(--header-height,64px);
}

/* ── header__column — from header-row.liquid ── */
.header__column{display:flex;align-items:center;}
.header__column--left{justify-content:flex-start;gap:0;}
.header__column--center{justify-content:center;height:100%;}
.header__column--right{justify-content:flex-end;}

/* ── header-logo — logo.liquid ── */
.header-logo{
  display:flex;height:100%;align-items:center;justify-content:center;
  text-decoration:none;
  font-size:1rem;
  font-family:'Jost',sans-serif;
  font-weight:600;
  font-style:normal;
  color:var(--color-foreground);
  flex-shrink:0;
}
.header-logo:hover{text-decoration:none;}
.header-logo__image-container{display:flex;align-items:center;}
/* logo.liquid: height from settings.logo_height / settings.logo_height_mobile via CSS vars */
.header-logo__image{
  object-fit:contain;
  height:40px;
  width:auto;
  max-width:180px;
}
@media screen and (max-width:749px){
  .header-logo{padding:0;}
  .header-logo__image{height:32px;}
}

/* ── header-menu / menu-list — from header-menu block + menu-list stylesheet ── */
.header-menu{height:100%;display:flex;align-items:center;}
.header-menu__inner{height:100%;display:flex;align-items:center;}

/* nav.menu-list — the <nav> element */
nav.menu-list{
  display:flex;
  height:100%;
  --menu-horizontal-gap:var(--gap-xl,32px);
}

/* .overflow-menu (the overflow-list component) — treated as ul */
.overflow-menu{
  display:flex;
  height:100%;
  list-style:none;
  margin:0;
  padding:var(--focus-outline-size,4px);
  margin:calc(-1 * var(--focus-outline-size,4px));
  background-color:transparent;
  gap:0;
  margin-inline:calc(-1 * var(--menu-horizontal-gap,32px) / 2);
}

/* menu-list__list — the actual <ul> of nav items */
.menu-list__list{
  display:flex;
  list-style:none;
  margin:0;padding:0;
  height:100%;
  justify-content:var(--grid-area-alignment,center);
}

/* menu-list__list-item — from header-menu block stylesheet */
.menu-list__list-item{
  flex-shrink:0;
  white-space:nowrap;
  display:flex;
  align-items:center;
  height:100%;
  flex-direction:column;
  position:relative;
}
/* ::after creates the hover zone below the link (--header-padding tall) */
.menu-list__list-item:not([slot='overflow'])::after{
  content:'';
  width:100%;
  height:var(--header-padding,16px);
  margin-bottom:calc(-1 * var(--header-padding,16px));
}

/* menu-list__link — from header-menu block stylesheet */
.menu-list__link{
  font-family:var(--menu-top-level-font-family,'Jost',sans-serif);
  font-style:var(--menu-top-level-font-style,normal);
  font-weight:var(--menu-top-level-font-weight,400);
  font-size:var(--menu-top-level-font-size,1rem);
  line-height:var(--menu-top-level-font-line-height,1.2);
  text-transform:var(--menu-top-level-font-case,none);
  color:var(--menu-top-level-font-color,#0d0906);
  text-decoration:none;
  display:flex;
  flex-direction:column;
  justify-content:center;
  cursor:pointer;
  height:100%;
  margin-block:0;
  transition:color 0.2s;
}
@media screen and (min-width:750px){
  .menu-list__link{font-size:var(--menu-top-level-font-size-desktop,1rem);}
}
.menu-list__link:hover,.menu-list__link:focus{
  color:var(--menu-top-level-font-color,#0d0906);
}

/* subdued hover effect — from header-menu block stylesheet :has() rules */
.menu-list__list:has(.menu-list__list-item:hover) .menu-list__link,
.menu-list__list:has(.menu-list__list-item:focus-within) .menu-list__link{
  color:rgba(var(--menu-top-level-font-color-rgb,13,9,6),var(--opacity-subdued-text,0.5));
}
.menu-list__list:has(.menu-list__list-item:hover) .menu-list__list-item:hover .menu-list__link,
.menu-list__list:has(.menu-list__list-item:focus-within) .menu-list__list-item:focus-within .menu-list__link{
  color:var(--menu-top-level-font-color,#0d0906);
}

/* menu-list__link-title padding — from header-menu block stylesheet */
.menu-list__link-title{
  padding-inline:calc(var(--gap-xl,32px) / 2);
}

/* active state — from header-menu block: link.active → menu-list__link--active */
.menu-list__link--active{
  color:var(--color-accent,#c1a3a2) !important;
  box-shadow:inset 0 -2px 0 var(--color-accent,#c1a3a2);
  opacity:1 !important;
}

/* ── header-actions — header-actions.liquid stylesheet ── */
header-actions{
  display:flex;
  /* margin-inline-start: calc(var(--gap-md) * -1) */
  margin-inline-start:calc(-1 * var(--gap-md,12px));
}

/* .header-actions__action — the individual icon buttons/links */
.header-actions__action{
  display:flex;align-items:center;justify-content:center;
  color:var(--color-foreground);
  text-decoration:none;
  padding:0 10px;
  height:var(--header-height,64px);
  position:relative;
  transition:opacity 0.2s;
  background:none;border:none;cursor:pointer;
  opacity:0.65;
}
.header-actions__action:hover{opacity:1;}
.header-actions__action svg{display:block;}

/* account icon exact size from header-actions.liquid */
.account-button__icon{width:15px;height:17px;}

/* cart bubble — from header-actions.liquid stylesheet */
.header-actions__cart-icon{
  --cart-bubble-size:20px;
  --cart-bubble-top:4.5px;
  --cart-bubble-right:2.5px;
  position:relative;
}
.cart-bubble{
  position:absolute;
  width:var(--cart-bubble-size,20px);
  height:var(--cart-bubble-size,20px);
  top:var(--cart-bubble-top,4.5px);
  right:var(--cart-bubble-right,2.5px);
  background:#0d0906;
  color:#fff;
  font-size:9px;
  border-radius:50%;
  display:none;
  align-items:center;justify-content:center;
  padding:0 3px;line-height:1;
}
.cart-bubble.visible{display:flex;}

/* ── header-drawer trigger (hamburger) — header-drawer.liquid ── */
/* Uses <details>/<summary> in real theme. We replicate with a button. */
.header__icon--menu{
  display:none;
  background:none;border:none;cursor:pointer;
  color:var(--color-foreground);
  padding:var(--padding-lg,16px);
  align-items:center;justify-content:center;
  height:var(--header-height,64px);
}
.header__icon--menu svg{
  width:var(--icon-size-xs,20px);
  height:var(--icon-size-xs,20px);
  display:block;
}

/* ── mobile breakpoint (max 749px) — matches theme's 750px breakpoint ── */
@media screen and (max-width:749px){
  .header{
    grid-template-columns:auto 1fr auto;
    padding:0 16px;
  }
  .header__column--center{display:none;}
  .header__icon--menu{display:flex;}
  header-actions{justify-self:flex-end;}
}

/* ── menu-drawer backdrop — header-drawer.liquid: .menu-drawer__backdrop ── */
.menu-drawer__backdrop{
  position:fixed;top:0;left:0;
  width:100vw;height:100dvh;
  backdrop-filter:brightness(0.75);
  z-index:calc(var(--layer-menu-drawer,9999) - 1);
  opacity:0;
  transition:opacity var(--drawer-animation-speed,0.3s) ease;
  pointer-events:none;
}
.menu-drawer__backdrop.open{opacity:1;pointer-events:auto;}

/* ── menu-drawer panel — header-drawer.liquid: .menu-drawer ── */
.menu-drawer{
  position:fixed;
  transform:translateX(-100%);
  visibility:hidden;
  top:0;left:0;
  height:100dvh;
  width:25rem;
  max-width:var(--drawer-max-width,85vw);
  z-index:var(--layer-menu-drawer,9999);
  background-color:var(--color-background,#fff);
  overflow-y:auto;
  display:flex;flex-direction:column;
  border-right:1px solid var(--color-border);
  box-shadow:4px 0 24px rgba(0,0,0,0.12);
  transition:transform var(--drawer-animation-speed,0.3s) ease,visibility var(--drawer-animation-speed,0.3s) ease;
}
.menu-drawer.open{
  transform:translateX(0);
  visibility:visible;
}

/* close button — header-drawer.liquid: .menu-drawer__close-button */
.menu-drawer__close-button{
  position:relative;right:auto;top:auto;
  width:fit-content;height:fit-content;
  color:inherit;
  padding:var(--padding-lg,16px);
  background:none;border:none;cursor:pointer;
  align-self:flex-end;
  display:flex;align-items:center;justify-content:center;
  transition:opacity 0.2s;
}
.menu-drawer__close-button:hover{opacity:0.6;}
.menu-drawer__close-button svg{width:var(--icon-size-xs,20px);height:var(--icon-size-xs,20px);}

/* nav inside drawer */
.menu-drawer__navigation{padding:0;}

/* drawer menu list — header-drawer.liquid: .menu-drawer__menu */
.menu-drawer__menu{
  list-style:none;
  padding-inline:var(--padding-lg,16px);
  margin:0;
}
.menu-drawer__menu.has-submenu{margin-block-end:0.5rem;}

/* each list item */
.menu-drawer__menu > .menu-drawer__list-item{
  display:flex;
  min-height:calc(2 * var(--padding-lg,16px) + var(--icon-size-xs,20px));
}

/* main-list items — header-drawer.liquid: .menu-drawer__menu-item--mainlist */
/* font from menu-font-styles.liquid with menu_type='drawer' → --menu-font-2xl--size */
.menu-drawer__menu-item{
  display:flex;
  padding:2px 0;
  position:relative;
  text-decoration:none;
  justify-content:space-between;
  align-items:center;
  width:100%;
}
.menu-drawer__menu-item--mainlist{
  min-height:calc(2 * var(--padding-lg,16px) + var(--icon-size-xs,20px));
  font-family:var(--menu-top-level-font-family,'Jost',sans-serif);
  font-style:var(--menu-top-level-font-style,normal);
  font-weight:var(--menu-top-level-font-weight,400);
  font-size:var(--menu-top-level-font-size-drawer,1.5rem);
  line-height:1.2;
  text-transform:var(--menu-top-level-font-case,none);
  color:var(--menu-top-level-font-color,#0d0906);
  text-decoration:none;
}
.menu-drawer__menu-item--mainlist:hover{color:var(--menu-top-level-font-color,#0d0906);}
.menu-drawer__menu-item--active{color:var(--color-accent,#c1a3a2) !important;}
.menu-drawer__menu-item-text{overflow:hidden;text-overflow:ellipsis;}
"""

NAV_HTML = """
<!-- menu-drawer backdrop (header-drawer.liquid: .menu-drawer__backdrop) -->
<div class="menu-drawer__backdrop" id="srd-backdrop" onclick="srdCloseDrawer()"></div>

<!-- menu-drawer panel (header-drawer.liquid: .menu-drawer) -->
<div class="menu-drawer" id="srd-drawer" role="dialog" aria-modal="true" aria-label="Menu">
  <!-- close button (.menu-drawer__close-button) -->
  <button class="menu-drawer__close-button" onclick="srdCloseDrawer()" type="button" aria-label="Close menu">
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
      <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
    </svg>
  </button>
  <!-- nav (.menu-drawer__navigation) with menu-font-styles drawer vars -->
  <nav class="menu-drawer__navigation" aria-label="Navigation">
    <ul class="menu-drawer__menu has-submenu" role="list">
      <li class="menu-drawer__list-item">
        <a href="https://supportrd.com" class="menu-drawer__menu-item menu-drawer__menu-item--mainlist">
          <span class="menu-drawer__menu-item-text">Home</span>
        </a>
      </li>
      <li class="menu-drawer__list-item">
        <a href="https://supportrd.com/collections/all" class="menu-drawer__menu-item menu-drawer__menu-item--mainlist">
          <span class="menu-drawer__menu-item-text">Catalog</span>
        </a>
      </li>
      <li class="menu-drawer__list-item">
        <a href="https://supportrd.com/pages/contact" class="menu-drawer__menu-item menu-drawer__menu-item--mainlist">
          <span class="menu-drawer__menu-item-text">Contact</span>
        </a>
      </li>
      <li class="menu-drawer__list-item">
        <a href="https://supportrd.com/pages/hair-dashboard" class="menu-drawer__menu-item menu-drawer__menu-item--mainlist">
          <span class="menu-drawer__menu-item-text">Dashboard</span>
        </a>
      </li>
      <li class="menu-drawer__list-item">
        <a href="https://supportrd.com/pages/custom-order" class="menu-drawer__menu-item menu-drawer__menu-item--mainlist">
          <span class="menu-drawer__menu-item-text">Custom Order</span>
        </a>
      </li>
      <li class="menu-drawer__list-item">
        <a href="https://hairtips.supportrd.com/blog" class="menu-drawer__menu-item menu-drawer__menu-item--mainlist menu-drawer__menu-item--active">
          <span class="menu-drawer__menu-item-text">Blog</span>
        </a>
      </li>
    </ul>
  </nav>
</div>

<!-- header-component (header-row.liquid: 3-column grid) -->
<div id="header-component">
  <div class="header" role="banner">

    <!-- LEFT: hamburger (header-drawer.liquid) + logo (logo.liquid) -->
    <div class="header__column header__column--left" data-testid="header-top-left">
      <!-- hamburger: header-drawer.liquid summary.header__icon--menu -->
      <button
        class="header__icon header__icon--menu"
        onclick="srdOpenDrawer()"
        aria-label="Menu"
        aria-expanded="false"
        aria-controls="srd-drawer"
        type="button"
      >
        <!-- icon-menu.svg -->
        <svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round">
          <line x1="2" y1="5" x2="18" y2="5"/>
          <line x1="2" y1="10" x2="18" y2="10"/>
          <line x1="2" y1="15" x2="18" y2="15"/>
        </svg>
      </button>
      <!-- logo: logo.liquid a.header-logo > span.header-logo__image-container > img.header-logo__image -->
      <a href="https://supportrd.com" class="header-logo" aria-label="SupportRD">
        <span class="header-logo__image-container header-logo__image-container--original" data-testid="header-logo">
          <img
            src="https://cdn.shopify.com/s/files/1/0593/2715/2208/files/woman-waking-up.jpg?v=1771636828"
            alt="SupportRD"
            class="header-logo__image"
          >
        </span>
      </a>
    </div>

    <!-- CENTER: desktop nav (header-menu block) -->
    <div class="header__column header__column--center" data-testid="header-top-center">
      <div class="header-menu">
        <div class="header-menu__inner">
          <!-- nav.menu-list with menu-font-styles inline vars (menu_type='mega_menu') -->
          <nav class="menu-list" aria-label="Primary navigation">
            <!-- overflow-list renders as ul.overflow-menu > li.menu-list__list-item -->
            <ul class="overflow-menu menu-list__list" role="list" data-testid="header-menu-overflow-list">
              <li class="menu-list__list-item" role="presentation">
                <a href="https://supportrd.com" class="menu-list__link">
                  <span class="menu-list__link-title">Home</span>
                </a>
              </li>
              <li class="menu-list__list-item" role="presentation">
                <a href="https://supportrd.com/collections/all" class="menu-list__link">
                  <span class="menu-list__link-title">Catalog</span>
                </a>
              </li>
              <li class="menu-list__list-item" role="presentation">
                <a href="https://supportrd.com/pages/contact" class="menu-list__link">
                  <span class="menu-list__link-title">Contact</span>
                </a>
              </li>
              <li class="menu-list__list-item" role="presentation">
                <a href="https://supportrd.com/pages/hair-dashboard" class="menu-list__link">
                  <span class="menu-list__link-title">Dashboard</span>
                </a>
              </li>
              <li class="menu-list__list-item" role="presentation">
                <a href="https://supportrd.com/pages/custom-order" class="menu-list__link">
                  <span class="menu-list__link-title">Custom Order</span>
                </a>
              </li>
              <li class="menu-list__list-item" role="presentation">
                <a href="https://hairtips.supportrd.com/blog" class="menu-list__link menu-list__link--active" aria-current="page">
                  <span class="menu-list__link-title">Blog</span>
                </a>
              </li>
            </ul>
          </nav>
        </div>
      </div>
    </div>

    <!-- RIGHT: header-actions (header-actions.liquid) -->
    <div class="header__column header__column--right" data-testid="header-top-right">
      <header-actions>
        <!-- search -->
        <a href="https://supportrd.com/search" class="header-actions__action" aria-label="Search">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
          </svg>
        </a>
        <!-- account: exact SVG path from header-actions.liquid -->
        <a href="https://supportrd.com/account/login" class="header-actions__action" aria-label="Account">
          <svg xmlns="http://www.w3.org/2000/svg" width="15" height="17" viewBox="0 0 15 17" fill="none" class="account-button__icon">
            <path stroke="currentColor" stroke-linejoin="round" stroke-width="1.3"
              d="M10.375 3.813a3.063 3.063 0 1 1-6.125 0 3.063 3.063 0 0 1 6.125 0ZM7.313 9.5c-3.667 0-6.24 2.691-6.563 6.125h13.125C13.552 12.191 10.979 9.5 7.312 9.5Z"/>
          </svg>
        </a>
        <!-- cart: icon-cart.svg + cart-bubble (header-actions.liquid) -->
        <a href="https://supportrd.com/cart" class="header-actions__action header-actions__cart-icon" aria-label="Cart" aria-describedby="cart-bubble-text">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
            <path d="M6 2L3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4z"/>
            <line x1="3" y1="6" x2="21" y2="6"/>
            <path d="M16 10a4 4 0 0 1-8 0"/>
          </svg>
          <span class="cart-bubble" id="cart-count" id="cart-bubble-text"></span>
        </a>
      </header-actions>
    </div>

  </div>
</div>

<script>
(function(){
  function srdOpenDrawer(){
    var d=document.getElementById('srd-drawer');
    var b=document.getElementById('srd-backdrop');
    d.classList.add('open');
    b.classList.add('open');
    document.body.style.overflow='hidden';
  }
  function srdCloseDrawer(){
    var d=document.getElementById('srd-drawer');
    var b=document.getElementById('srd-backdrop');
    d.classList.remove('open');
    b.classList.remove('open');
    document.body.style.overflow='';
  }
  window.srdOpenDrawer=srdOpenDrawer;
  window.srdCloseDrawer=srdCloseDrawer;
  document.addEventListener('keydown',function(e){if(e.key==='Escape')srdCloseDrawer();});
  // cart count from supportrd.com/cart.js
  fetch('https://supportrd.com/cart.js')
    .then(function(r){return r.json();})
    .then(function(d){
      if(d.item_count>0){
        var el=document.getElementById('cart-count');
        if(el){el.textContent=d.item_count;el.classList.add('visible');}
      }
    }).catch(function(){});
})();
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
