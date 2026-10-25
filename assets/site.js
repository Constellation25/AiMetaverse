/* ============================================================
   Ai Metaverse — shared shell for all static subpages
   Injects: constellation header, nav, mobile menu, footer,
            cookie banner, scroll progress, reveal animations.
   No build step, no dependencies. Works from file:// too.
   ============================================================ */
(function () {
  "use strict";
  var $ = function (s, c) { return (c || document).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || document).querySelectorAll(s)); };
  var reduceMotion = !!(window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches);

  /* ---------- navigation model (single source of truth) ---------- */
  var NAV = [
    { href: 'index.html', label: 'Home' },
    { href: 'why-ai/index.html', label: 'Why AI' },
    { href: 'enterprise/index.html', label: 'AI for Enterprise' },
    { href: 'tools/index.html', label: 'Free AI Tools' },
    { href: 'labs/index.html', label: 'Ai-Labs' },
    { href: 'education/index.html', label: 'Ai_Education' },
    { href: 'worlds/index.html', label: 'Worlds' },
    { href: 'developers/index.html', label: 'Developers' },
    { href: 'apikonnect/index.html', label: 'APIKonnect' },
    { href: 'devzone/index.html', label: 'DevZone' },
    { href: 'communities/index.html', label: 'Find Friends' }
  ];
  var FOOT = [
    {
      title: 'Explore', links: [
        { href: 'index.html', label: 'Home' },
        { href: 'why-ai/index.html', label: 'Why AI' },
        { href: 'enterprise/index.html', label: 'AI for Enterprise' },
        { href: 'tools/index.html', label: 'Free AI Tools Directory' },
        { href: 'labs/index.html', label: 'Access Ai-Labs' },
        { href: 'education/index.html', label: 'Ai_Education' }
      ]
    },
    {
      title: 'Create', links: [
        { href: 'avatar-create/index.html', label: 'Clone Yourself Virtually' },
        { href: 'twin-studio/index.html', label: 'Virtual Twin Studio' },
        { href: 'voice-lipsync/index.html', label: 'Voice &amp; Lip-Sync Studio' },
        { href: 'avatar/index.html', label: 'My Avatar &amp; Agent' },
        { href: 'worlds/index.html', label: 'Virtual Worlds' },
        { href: 'communities/index.html', label: 'Metaverse Communities' },
        { href: 'records/index.html', label: 'Ai.RECORDS — Song Lyrics' },
        { href: 'mars/index.html', label: 'ExploreMars — Virtual Real Estate' },
        { href: 'bitbucks/index.html', label: 'BitBucks — Learn & Earn' },
        { href: 'crm/index.html', label: 'Agentik AI CRM (free)' },
        { href: 'vstore/index.html', label: 'Virtual Store Builder' },
        { href: 'commz/index.html', label: 'Commz — AI Telemarketers' },
        { href: 'app-builder/index.html', label: 'AI App Builder' },
        { href: 'webstudio/index.html', label: 'AI Web Studio' },
        { href: 'faceforge/index.html', label: 'C25 FaceForge (face swap)' },
        { href: 'ai4reelz/index.html', label: 'Ai4Reelz Video Studio' },
        { href: 'metaverse-toolkit/index.html', label: 'Metaverse Creator Toolkit' },
        { href: 'vr-hub/index.html', label: 'VR Hardware Hub' },
        { href: 'metaverse-directory/index.html', label: 'Metaverse World Directory' },
        { href: 'ai-education-hub/index.html', label: 'AI Education & Prompt Hub' },
        { href: 'ai-education/index.html', label: 'aiEDU — Get Educated with AI' },
        { href: 'shop/index.html', label: 'Virtual Shopping Kre8tor' },
        { href: 'shop/index.html#gifts', label: 'AI Gifts &amp; Gadgets Store' },
        { href: 'metabox.html', label: 'Conversate with the Metabox' },
        { href: 'developers/index.html', label: 'Developer &amp; Coding Repo' },
        { href: 'apikonnect/index.html', label: 'APIKonnect — enterprise LLMs & APIs' },
        { href: 'devzone/index.html', label: 'DevZone terminal' }
      ]
    },
    {
      title: 'Company', links: [
        { href: 'contact/index.html', label: 'Contact Us' },
        { href: 'news/index.html', label: 'Ai Metaverse News &amp; Blog' },
        { href: 'signup/index.html', label: 'Sign up' },
        { href: 'signin/index.html', label: 'Sign in' },
        { href: 'privacy/index.html', label: 'Privacy Policy' },
        { href: 'terms/index.html', label: 'Terms and Conditions' }
      ]
    }
  ];

  function canon(pathname) {
    var segs = pathname.split('/').filter(Boolean);
    if (!segs.length) return 'index.html';
    var last = segs[segs.length - 1];
    if (last === '' ) return 'index.html';
    if (last.toLowerCase() === 'index.html') return segs.length > 1 ? segs[segs.length - 2].toLowerCase() + '.html' : 'index.html';
    if (pathname.charAt(pathname.length - 1) === '/') return last.toLowerCase() + '.html';
    return last.toLowerCase();
  }
  var page = canon(location.pathname);
  function isCurrent(href) { return canon(href.split('#')[0]) === page; }

  /* ---------- header ---------- */
  function buildHeader() {
    if ($('#site-header')) return;
    var h = document.createElement('header');
    h.className = 'site-header';
    h.id = 'site-header';
    h.innerHTML =
      '<canvas id="constellation" aria-hidden="true"></canvas>' +
      '<div class="wrap nav">' +
        '<a class="brand" href="index.html" aria-label="Ai Metaverse home">' +
          '<span class="mark"><svg viewBox="0 0 24 24" fill="none" aria-hidden="true">' +
            '<circle cx="12" cy="12" r="8.2" stroke="#070312" stroke-width="2"/>' +
            '<circle cx="12" cy="12" r="3" fill="#070312"/>' +
            '<path d="M12 1.6v3M12 19.4v3M1.6 12h3M19.4 12h3" stroke="#070312" stroke-width="2" stroke-linecap="round"/>' +
          '</svg></span>' +
          '<span class="txt"><span class="name">Ai&nbsp;Metaverse</span><span class="sub">VERSED\'ai</span></span>' +
        '</a>' +
        '<nav class="nav-links" id="primary-nav" aria-label="Primary">' +
          NAV.map(function (n) {
            return '<a href="' + n.href + '"' + (isCurrent(n.href) ? ' class="active"' : '') + '>' + n.label + '</a>';
          }).join('') +
        '</nav>' +
        '<a href="avatar-create.html" class="btn btn-sm nav-cta">Clone Yourself</a>' +
        '<button class="burger" id="burger" aria-expanded="false" aria-controls="mobile-nav" aria-label="Toggle navigation">' +
          '<span></span><span></span><span></span>' +
        '</button>' +
      '</div>' +
      '<div class="mobile-panel" id="mobile-nav"><div class="wrap">' +
        NAV.concat([{ href: 'avatar-create/index.html', label: '★ Clone Yourself Virtually' },
                    { href: 'avatar/index.html', label: 'My Avatar & Agent' },
                    { href: 'shop/index.html', label: 'Virtual Shopping Kre8tor' },
                    { href: 'metabox/index.html', label: 'Metabox Chat' },
                    { href: 'news/index.html', label: 'News & Blog' },
                    { href: 'contact/index.html', label: 'Contact' },
                    { href: 'signup/index.html', label: 'Sign up' }])
          .map(function (n) {
            var cls = n.href === 'avatar-create.html' ? ' class="btn"' : '';
            return '<a href="' + n.href + '"' + cls + '>' + n.label + '</a>';
          }).join('') +
      '</div></div>';
    document.body.insertBefore(h, document.body.firstChild);

    var burger = $('#burger'), panel = $('#mobile-nav');
    burger.addEventListener('click', function () {
      var open = burger.getAttribute('aria-expanded') === 'true';
      burger.setAttribute('aria-expanded', String(!open));
      panel.classList.toggle('open', !open);
    });
    $$('#mobile-nav a').forEach(function (a) {
      a.addEventListener('click', function () {
        panel.classList.remove('open'); burger.setAttribute('aria-expanded', 'false');
      });
    });
  }

  /* ---------- top strip ---------- */
  function buildTopStrip() {
    if ($('#site-strip')) return;
    var d = document.createElement('div');
    d.className = 'topstrip'; d.id = 'site-strip';
    d.innerHTML = '<a href="avatar-create/index.html">★ Start your free trial — take a selfie, record your voice, build your AI agent ★</a>';
    document.body.insertBefore(d, document.body.firstChild);
  }

  /* ---------- footer ---------- */
  function buildFooter() {
    if ($('#site-footer')) return;
    var f = document.createElement('footer');
    f.className = 'site-footer'; f.id = 'site-footer';
    f.innerHTML =
      '<div class="wrap">' +
        '<div class="foot-grid">' +
          '<div class="foot-about">' +
            '<a class="brand" href="index.html">' +
              '<span class="mark"><svg viewBox="0 0 24 24" fill="none" aria-hidden="true">' +
                '<circle cx="12" cy="12" r="8.2" stroke="#070312" stroke-width="2"/>' +
                '<circle cx="12" cy="12" r="3" fill="#070312"/>' +
                '<path d="M12 1.6v3M12 19.4v3M1.6 12h3M19.4 12h3" stroke="#070312" stroke-width="2" stroke-linecap="round"/>' +
              '</svg></span>' +
              '<span class="txt"><span class="name">Ai Metaverse</span><span class="sub">VERSED\'ai</span></span>' +
            '</a>' +
            '<p>A world that revolves around creative intelligence. AI for All — the app hub for AI, metaverse, virtual and augmented reality.</p>' +
            '<p style="margin-top:12px;font-size:13px;color:var(--dim)">1007 Yanceyville Street, Greensboro, NC 27405 · <a href="tel:+13368050229" style="color:var(--muted)">336-805-0229</a></p>' +
            '<div class="socials">' +
              '<a href="news.html" aria-label="News"><svg viewBox="0 0 24 24" fill="none" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"><path d="M4 5h16v14H4z"/><path d="M8 9h8M8 13h5"/></svg></a>' +
              '<a href="developers.html" aria-label="Developers"><svg viewBox="0 0 24 24" fill="none" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"><path d="m8 8-4 4 4 4M16 8l4 4-4 4M13.5 5l-3 14"/></svg></a>' +
              '<a href="labs.html" aria-label="Ai-Labs"><svg viewBox="0 0 24 24" fill="none" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"><path d="M9 3h6M10 3v6L5 19a2 2 0 0 0 1.8 3h10.4A2 2 0 0 0 19 19l-5-10V3"/></svg></a>' +
              '<a href="contact.html" aria-label="Contact"><svg viewBox="0 0 24 24" fill="none" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"><path d="M4 4h16v14H5.5L4 19.5z"/><path d="M8 9h8M8 13h5"/></svg></a>' +
            '</div>' +
          '</div>' +
          FOOT.map(function (col) {
            return '<div><h5>' + col.title + '</h5><ul>' + col.links.map(function (l) {
              return '<li><a href="' + l.href + '"' + (isCurrent(l.href) ? ' style="color:var(--cyan)"' : '') + '>' + l.label + '</a></li>';
            }).join('') + '</ul></div>';
          }).join('') +
        '</div>' +
        '<div class="hashtags"><b>Trending tags</b>' +
          '#fypシ゚viralシ #datavisualization #artificialintelligence #coding #programmers #coder #dataanalytics #aigenerated #generatedimage #aiartcommunity #aiartgenerator #highfashiontiktok #couturetiktok #fy #princess #princessesreels #viral #viraltiktok #pet #petoftiktok #cat #dog #beauty #programmerhumour #pythonprogramming #uidesign #metaverse #web3 #readyplayerme' +
        '</div>' +
        '<div class="foot-bottom">' +
          '<span>Copyright © 2023–2026 Ai Metaverse — All Rights Reserved.</span>' +
          '<span>Powered by <b style="color:var(--txt)">Kre8Tive Koncepts</b></span>' +
        '</div>' +
      '</div>';
    document.body.appendChild(f);
  }

  /* ---------- cookie banner ---------- */
  function buildCookies() {
    if ($('#cookie-banner')) return;
    var stored = null;
    try { stored = localStorage.getItem('aimv_cookies'); } catch (e) {}
    if (stored) return;
    var d = document.createElement('div');
    d.className = 'cookie-banner'; d.id = 'cookie-banner';
    d.setAttribute('role', 'region'); d.setAttribute('aria-label', 'Cookie consent');
    d.innerHTML =
      '<div class="wrap cookie-in">' +
        '<p><b>This website uses cookies.</b> We use them to analyse traffic and optimise your experience. Your avatar, voice sample and birthday stay in this browser only — see the <a href="privacy.html" style="color:var(--cyan);text-decoration:underline">Privacy Policy</a>. By accepting, your data will be aggregated with all other user data.</p>' +
        '<div class="btn-row" style="gap:10px">' +
          '<button class="btn btn-sm" data-cookie="accept">Accept</button>' +
          '<button class="btn btn-sm btn-ghost" data-cookie="decline">Decline</button>' +
        '</div>' +
      '</div>';
    document.body.appendChild(d);
    setTimeout(function () { d.classList.add('show'); }, 1600);
    $$('[data-cookie]', d).forEach(function (b) {
      b.addEventListener('click', function () {
        try { localStorage.setItem('aimv_cookies', b.dataset.cookie); } catch (e) {}
        d.classList.remove('show');
      });
    });
  }

  /* ---------- scroll progress ---------- */
  function buildProgress() {
    if ($('#scroll-progress')) return;
    var d = document.createElement('div');
    d.className = 'scroll-progress'; d.id = 'scroll-progress';
    document.body.appendChild(d);
  }

  /* ---------- constellation (header backdrop) ---------- */
  function constellation() {
    var cvs = document.getElementById('constellation');
    if (!cvs || !cvs.getContext) return;
    var ctx = null;
    try { ctx = cvs.getContext('2d'); } catch (e) { return; }
    if (!ctx) return;
    var header = cvs.parentElement;
    var stars = [], W = 0, H = 0, raf = null, pointer = { x: null, y: null };
    var LINK = 128, PLINK = 165;

    function seed() {
      var r = header.getBoundingClientRect();
      W = Math.max(1, Math.round(r.width)); H = Math.max(1, Math.round(r.height));
      var dpr = Math.min(window.devicePixelRatio || 1, 2);
      cvs.width = W * dpr; cvs.height = H * dpr;
      cvs.style.width = W + 'px'; cvs.style.height = H + 'px';
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      var count = Math.max(24, Math.min(90, Math.round(W * H / 13000)));
      stars = [];
      for (var i = 0; i < count; i++) {
        stars.push({
          x: Math.random() * W, y: Math.random() * H,
          vx: (Math.random() - .5) * .17, vy: (Math.random() - .5) * .13,
          r: Math.random() * 1.45 + .5, p: Math.random() * Math.PI * 2,
          c: Math.random() < .18 ? '255,47,185' : (Math.random() < .35 ? '168,85,247' : '0,240,255')
        });
      }
    }
    function frame() {
      ctx.clearRect(0, 0, W, H);
      for (var i = 0; i < stars.length; i++) {
        var a = stars[i];
        a.x += a.vx; a.y += a.vy; a.p += .021;
        if (a.x < -12) a.x = W + 12; else if (a.x > W + 12) a.x = -12;
        if (a.y < -12) a.y = H + 12; else if (a.y > H + 12) a.y = -12;
        for (var j = i + 1; j < stars.length; j++) {
          var b = stars[j], dx = a.x - b.x, dy = a.y - b.y, d = Math.sqrt(dx * dx + dy * dy);
          if (d < LINK) {
            ctx.strokeStyle = 'rgba(0,240,255,' + ((1 - d / LINK) * .3).toFixed(3) + ')';
            ctx.lineWidth = .7; ctx.beginPath(); ctx.moveTo(a.x, a.y); ctx.lineTo(b.x, b.y); ctx.stroke();
          }
        }
        if (pointer.x !== null) {
          var px = a.x - pointer.x, py = a.y - pointer.y, pd = Math.sqrt(px * px + py * py);
          if (pd < PLINK) {
            ctx.strokeStyle = 'rgba(255,47,185,' + ((1 - pd / PLINK) * .42).toFixed(3) + ')';
            ctx.lineWidth = .85; ctx.beginPath(); ctx.moveTo(a.x, a.y); ctx.lineTo(pointer.x, pointer.y); ctx.stroke();
          }
        }
        var tw = .45 + .55 * Math.abs(Math.sin(a.p));
        ctx.beginPath(); ctx.fillStyle = 'rgba(' + a.c + ',' + (.85 * tw).toFixed(3) + ')';
        ctx.arc(a.x, a.y, a.r, 0, 6.2832); ctx.fill();
        if (a.r > 1.25) {
          ctx.beginPath(); ctx.fillStyle = 'rgba(' + a.c + ',' + (.13 * tw).toFixed(3) + ')';
          ctx.arc(a.x, a.y, a.r * 3.6, 0, 6.2832); ctx.fill();
        }
      }
      raf = requestAnimationFrame(frame);
    }
    function start() { if (raf === null && !reduceMotion) raf = requestAnimationFrame(frame); }
    function stop() { if (raf !== null) { cancelAnimationFrame(raf); raf = null; } }
    seed();
    if (reduceMotion) frame(); else start();
    header.addEventListener('pointermove', function (e) {
      var r = header.getBoundingClientRect(); pointer.x = e.clientX - r.left; pointer.y = e.clientY - r.top;
    });
    header.addEventListener('pointerleave', function () { pointer.x = null; pointer.y = null; });
    window.addEventListener('resize', function () { stop(); seed(); if (!reduceMotion) start(); else frame(); });
    document.addEventListener('visibilitychange', function () { document.hidden ? stop() : start(); });
  }

  /* ---------- ambient background + reveal + progress + back-to-top ---------- */
  function buildAmbient() {
    if ($('.bg-fx')) return;
    var d = document.createElement('div');
    d.className = 'bg-fx'; d.setAttribute('aria-hidden', 'true');
    d.innerHTML = '<div class="grid"></div><div class="orb o1"></div><div class="orb o2"></div><div class="orb o3"></div><div class="noise"></div>';
    document.body.insertBefore(d, document.body.firstChild);
  }
  function reveals() {
    var els = $$('.reveal');
    if (!('IntersectionObserver' in window)) { els.forEach(function (e) { e.classList.add('in'); }); return; }
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } });
    }, { threshold: .1, rootMargin: '0px 0px -40px 0px' });
    els.forEach(function (e) { io.observe(e); });
  }
  function counters() {
    var els = $$('[data-count]');
    if (!els.length) return;
    function run(el) {
      var target = parseFloat(el.dataset.count), suf = el.dataset.suffix || '', dec = parseInt(el.dataset.dec || '0', 10);
      if (reduceMotion) { el.textContent = target.toLocaleString(undefined, { minimumFractionDigits: dec }) + suf; return; }
      var start = null, dur = 1400;
      (function step(ts) {
        if (!start) start = ts;
        var p = Math.min((ts - start) / dur, 1), e = 1 - Math.pow(1 - p, 3);
        el.textContent = (target * e).toLocaleString(undefined, { minimumFractionDigits: dec, maximumFractionDigits: dec }) + suf;
        if (p < 1) requestAnimationFrame(step);
      })(performance.now());
    }
    if (!('IntersectionObserver' in window)) { els.forEach(run); return; }
    var io = new IntersectionObserver(function (en) {
      en.forEach(function (e) { if (e.isIntersecting) { run(e.target); io.unobserve(e.target); } });
    }, { threshold: .5 });
    els.forEach(function (e) { io.observe(e); });
  }
  function buildToTop() {
    if ($('#totop')) return;
    var b = document.createElement('button');
    b.className = 'totop'; b.id = 'totop'; b.setAttribute('aria-label', 'Back to top');
    b.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M12 19V5M6 11l6-6 6 6"/></svg>';
    document.body.appendChild(b);
    b.addEventListener('click', function () { window.scrollTo({ top: 0, behavior: reduceMotion ? 'auto' : 'smooth' }); });
    window.addEventListener('scroll', function () {
      b.classList.toggle('show', window.scrollY > 620);
      var p = $('#scroll-progress');
      if (p) {
        var h = document.documentElement.scrollHeight - window.innerHeight;
        p.style.width = (h > 0 ? (window.scrollY / h) * 100 : 0) + '%';
      }
    }, { passive: true });
  }

  /* ---------- humanoid companion (skip pages that load it themselves) ---------- */
  function injectHumanoid() {
    if (document.querySelector('[data-humanoid]')) return;
    var pre = location.pathname.indexOf('/agents/') !== -1 ? '../assets/' : 'assets/';
    var l = document.createElement('link');
    l.rel = 'stylesheet'; l.href = pre + 'humanoid.css'; l.setAttribute('data-humanoid', 'css');
    document.head.appendChild(l);
    var sc = document.createElement('script');
    sc.src = pre + 'humanoid.js'; sc.defer = true; sc.setAttribute('data-humanoid', 'js');
    document.body.appendChild(sc);
  }

  /* ---------- boot ---------- */
  function boot() {
    buildTopStrip();
    buildHeader();
    buildAmbient();
    buildFooter();
    buildCookies();
    buildProgress();
    buildToTop();
    constellation();
    reveals();
    counters();
    injectHumanoid();
    document.documentElement.classList.add('shell-ready');
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot);
  else boot();

  /* expose for pages that need it */
  window.AIMV = { $: $, $$: $$, reduceMotion: reduceMotion, page: page, NAV: NAV };
})();
