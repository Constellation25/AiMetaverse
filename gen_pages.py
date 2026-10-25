import re
#!/usr/bin/env python3
# Generates the static subpages of the Ai Metaverse site.
# Every page is a real, self-contained .html file that shares assets/site.css + assets/site.js.
import io, os, datetime

ROOT = os.path.dirname(os.path.abspath(__file__))
FACE_B64 = open(os.path.join(ROOT,'assets','face-small.jpg'),'rb').read() and __import__('base64').b64encode(open(os.path.join(ROOT,'assets','face-small.jpg'),'rb').read()).decode()
ORB_B64 = __import__('base64').b64encode(open(os.path.join(ROOT,'assets','face-orb.jpg'),'rb').read()).decode()


# ---------- self-contained inlining (GitHub Pages: every page must stand alone) ----------
def _rd(p):
    with io.open(os.path.join(ROOT, p), encoding='utf-8') as f:
        return f.read()
FACE_URL = 'data:image/jpeg;base64,' + FACE_B64
ORB_URL = 'data:image/jpeg;base64,' + ORB_B64
SITE_CSS = _rd('assets/site.css')
HUM_CSS = _rd('assets/humanoid.css').replace('url("face-orb.jpg")', 'url("%s")' % ORB_URL).replace('url("face-real.jpg")', 'url("%s")' % FACE_URL)
SITE_JS = _rd('assets/site.js')
HUM_JS = _rd('assets/humanoid.js')
AVA_JS = _rd('assets/avatar.js')
FACES_SNIPPET = 'window.AIMV_FACES={real:"%s"};' % FACE_URL
def inline_css():
    return '<style>\n' + SITE_CSS + '\n' + HUM_CSS + '\n</style>\n'
def inline_js(scripts=()):
    out = '<script data-humanoid="js">\n' + SITE_JS + '\n' + FACES_SNIPPET + '\n' + HUM_JS + '\n</script>\n'
    if 'avatar' in scripts:
        out += '<script>\n' + AVA_JS + '\n</script>\n'
    return out

FAV = ("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Crect width='64' height='64' rx='16' fill='%23070312'/%3E"
       "%3Ccircle cx='32' cy='32' r='17' fill='none' stroke='%2300f0ff' stroke-width='4'/%3E%3Ccircle cx='32' cy='32' r='6' fill='%23ff2fb9'/%3E%3C/svg%3E")

def head(title, desc):
    INLINE_CSS = inline_css()
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>{title}</title>
<meta name="description" content="{desc}" />
<meta name="theme-color" content="#070312" />
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="icon" href="{FAV}">
</head>
<body>
<div class="scroll-progress" id="scroll-progress"></div>
"""

def hero(crumb, crumb_href, eyebrow, h1, grad, lead, btns=""):
    return f"""<main>
<section class="page-hero">
  <div class="wrap">
    <nav class="crumbs" aria-label="Breadcrumb"><a href="index.html">Home</a><span class="sep">/</span><span class="current">{crumb}</span></nav>
    <span class="eyebrow"><span class="dot"></span> {eyebrow}</span>
    <h1>{h1} <span class="grad-text">{grad}</span></h1>
    <p class="prose" style="font-size:clamp(1rem,1.7vw,1.15rem)">{lead}</p>
    {btns}
  </div>
</section>
"""

def foot(extra="", scripts=()):
    INLINE_JS = inline_js(scripts)
    return f"""</main>
{INLINE_JS}
{extra}</body>
</html>
"""

def sec(sid, inner, cls="sec"):
    return f'<section class="{cls}" id="{sid}"><div class="wrap">{inner}</div></section>\n'

def shead(eyebrow, h2, grad, lead, center=True):
    c = " center" if center else ""
    return f"""<div class="sec-head{c} reveal">
      <span class="eyebrow"><span class="dot"></span> {eyebrow}</span>
      <h2 class="h-lg">{h2} <span class="grad-text">{grad}</span></h2>
      <p class="lead">{lead}</p>
    </div>"""


KNOWN = ['index.html','why-ai.html','enterprise.html','tools.html','labs.html','education.html',
         'worlds.html','shop.html','metabox.html','news.html','contact.html','signup.html','signin.html',
         'privacy.html','terms.html','developers.html','avatar-create.html','avatar.html','apikonnect.html',
         'devzone.html','records.html','mars.html','bitbucks.html','crm.html','vstore.html','commz.html','app-builder.html','webstudio.html','faceforge.html','ai4reelz.html','metaverse-toolkit.html','vr-hub.html','metaverse-directory.html','ai-education-hub.html','agents/agent.html',
         'ai-education.html','prompter.html','twin-studio.html','voice-lipsync.html']
def _dirmap(k): return 'index.html' if k=='index.html' else k[:-5]+'/index.html'
def dirform(html, ownflat):
    import re as _re
    for k in sorted(KNOWN, key=len, reverse=True):
        d = _dirmap(k)
        html = _re.sub(r'href="%s#([^"]*)"' % _re.escape(k), lambda m: 'href="%s#%s"' % (d, m.group(1)), html)
        html = html.replace('href="%s"' % k, 'href="%s"' % d)
    html = _re.sub(r'href="#([^"]+)"', lambda m: 'href="%s#%s"' % (ownflat, m.group(1)), html)
    return html
CHARSET = '<meta charset="UTF-8" />\n'
def with_base(html, base):
    return html.replace(CHARSET, CHARSET + '<base href="%s" />\n' % base, 1)
def depth(name): return name.count('/')
def emit(name, html):
    flat = with_base(html, '../' * depth(name) or './')
    folder = with_base(html, '../' * (depth(name) + 1))
    with io.open(os.path.join(ROOT, name), 'w', encoding='utf-8') as f: f.write(flat)
    fdir = os.path.join(ROOT, name[:-5], 'index.html')
    os.makedirs(os.path.dirname(fdir), exist_ok=True)
    with io.open(fdir, 'w', encoding='utf-8') as f: f.write(folder)
    print('%-24s %6d + %6d bytes (flat + folder)' % (name, len(flat), len(folder)))

P = {}

# ============================================================ WHY AI
P['why-ai.html'] = dict(
 title="Why AI — Seven Pillars of the Ai Metaverse | Ai Metaverse",
 desc="Social features, AI tools, digital economy, VR, enterprise, gaming and infrastructure: the seven pillars of the Ai Metaverse, expanded.",
 body=hero("Why AI", None, "Why AI", "Seven pillars,", "one metaverse",
   "Everything the Ai Metaverse does falls into seven families of capability. Open any pillar to see exactly what is inside — no marketing fog, just the feature list.")
 + sec("pillars", shead("The pillars", "Key features &amp; services of the", "Ai Metaverse",
     "Tap any pillar to expand the full list.") + """
<details class="acc reveal" open><summary><span class="num">01</span>Social &amp; Interactive Features</summary><div class="acc-b"><ul>
<li>Interact with other users and <b>AI-powered entities</b> in a realistic and engaging way</li>
<li>Virtual remote meetings and collaboration</li>
<li>Virtual concerts and events</li>
<li>Virtual shopping and immersive shopping experiences</li>
<li>Social network with <b>free speech</b> and revenue opportunities through digital asset creation and trading</li>
</ul></div></details>
<details class="acc reveal"><summary><span class="num">02</span>AI-Powered Tools &amp; Services</summary><div class="acc-b"><ul>
<li><b>Craiyon:</b> AI art generator that turns text prompts into images</li>
<li>Product recommendation systems based on user preferences and behavior</li>
<li>Plagiarism analyzer for written content</li>
<li>Bird species prediction based on characteristics</li>
<li>AI model building, training, validation, testing and deployment</li>
</ul></div></details>
<details class="acc reveal"><summary><span class="num">03</span>Digital Payment &amp; Economy</summary><div class="acc-b"><ul>
<li>Customer-driven, seamless and secure digital payment ecosystem</li>
<li>Decentralized ecosystem with a democratic and equitable economy</li>
<li>Blockchain-based game and metaverse world for buying, selling and trading virtual assets</li>
</ul></div></details>
<details class="acc reveal"><summary><span class="num">04</span>Virtual Reality &amp; Experiences</summary><div class="acc-b"><ul>
<li>Virtual reality experiences through Cardboard</li>
<li>Virtual world creation with little to no human input</li>
<li>Wearable consumer head-mounted displays with AI-powered sensors</li>
<li>3D scanning technology that reconstructs real-world objects into virtual versions</li>
</ul></div></details>
<details class="acc reveal"><summary><span class="num">05</span>Enterprise &amp; Professional Solutions</summary><div class="acc-b"><ul>
<li>Enterprise metaverse solutions to build <b>digital twins</b> of offices and retail storefronts</li>
<li>Professional metaverse platform for training, workshops, events, conferences and team collaboration</li>
</ul></div></details>
<details class="acc reveal"><summary><span class="num">06</span>Gaming &amp; Entertainment</summary><div class="acc-b"><ul>
<li>Next-generation gaming metaverse from the convergence of blockchain, real-time visuals, multiplayer video games and decentralized financial technologies</li>
<li>Online game platform where users can build and access games</li>
<li>Social VR platform featuring virtual venues, interactive experiences and digital content</li>
</ul></div></details>
<details class="acc reveal"><summary><span class="num">07</span>Infrastructure &amp; Technology</summary><div class="acc-b"><ul>
<li>Supercomputing to build the metaverse of the future</li>
<li>AI-powered chatbots and digital humans for interactive experiences</li>
<li>Natural language processing for global communication within the metaverse</li>
</ul></div></details>
""")
 + sec("value", shead("Unlock the future of technology", "Where innovative technology meets", "immersive experiences",
     "We're dedicated to pushing the boundaries of human existence, creating new possibilities for connection and collaboration.") + """
<div class="value-grid">
  <article class="value reveal"><span class="vi">✳</span><h3>Empowering Individuals &amp; Businesses</h3><p>With a focus on excellence and efficiency we provide cutting-edge virtual and artificial solutions. Our state-of-the-art AI models — over <b style="color:var(--txt)">20,000</b> of them — are designed to help you work smarter, not harder.</p></article>
  <article class="value reveal"><span class="vi">⚡</span><h3>Streamline Your Workflow</h3><p>Say goodbye to manual work. Our models assist with natural language processing, code generation and translation across your whole stack.</p></article>
  <article class="value reveal"><span class="vi">◎</span><h3>Join the AiMetAVerse Community</h3><p>Connect with AI enthusiasts, attend exclusive events and enjoy free storage cloud services. Upgraded users unlock our most advanced models and tools.</p></article>
  <article class="value reveal"><span class="vi">▲</span><h3>Turn Ambitions into Realities</h3><p>Don't wait — stop dreaming and start achieving. Build your world, launch your store, deploy your agent.</p><a class="btn btn-sm btn-ghost" style="margin-top:16px" href="avatar-create.html">Clone yourself virtually</a></article>
</div>
<div class="callout reveal" style="margin-top:30px"><b>Try it on yourself:</b> open the companion bubble in the corner and say “why AI?” — the humanoid answers from this very page.</div>
""")
)

# ============================================================ ENTERPRISE
P['enterprise.html'] = dict(
 title="AI for Enterprise — Custom Agent Models & Digital Twins | Ai Metaverse",
 desc="Purpose-driven custom agent models, digital twins of offices and storefronts, training platforms and biometric payments for business.",
 body=hero("AI for Enterprise", None, "AI for Enterprise", "Purpose-driven agents,", "built for your tasks",
   "The Ai-Metaverse landscape dominates the market by helping the world deploy custom-built agent models for dedicated tasks — plus digital twins, professional event spaces and secure payments.")
 + sec("pipe", shead("How an agent ships", "From task definition to", "deployment in five steps",
     "The same pipeline powers every enterprise engagement.") + """
<div class="grid-2">
  <div class="panel reveal"><div class="kv">
    <div><span class="k">1 · Define</span><span class="v">Dedicated task + success metrics</span></div>
    <div><span class="k">2 · Build</span><span class="v">Custom agent model in Ai-Labs</span></div>
    <div><span class="k">3 · Train</span><span class="v">Validated against your own data</span></div>
    <div><span class="k">4 · Test</span><span class="v">Inside a digital twin of your space</span></div>
    <div><span class="k">5 · Deploy</span><span class="v">Web, mobile, VR and voice channels</span></div>
  </div></div>
  <div class="panel reveal">
    <h3>What enterprises get</h3>
    <ul class="prose"><li>Digital twins of offices and retail storefronts</li>
    <li>Professional platform for training, workshops, events, conferences and team collaboration</li>
    <li>Free AI CRM and AI telemarketers that never sleep</li>
    <li>Biometric verification &amp; payments with <a href="https://mybuyo-biometric-saas.vercel.app" target="_blank" rel="noopener noreferrer" style="color:var(--cyan)">MyBUY'o</a>, BitBucks round-up rewards</li>
    <li>Supercomputing infrastructure and NLP for global teams</li></ul>
    <div class="btn-row" style="margin-top:18px"><a class="btn" href="contact.html">Talk to enterprise sales</a><a class="btn btn-ghost" href="avatar-create.html">Forge a pilot agent</a></div>
  </div>
</div>
<div class="tbl-wrap reveal" style="margin-top:26px"><table class="tbl">
<tr><th>Engagement</th><th>Typical scope</th><th>Deliverable</th></tr>
<tr><td>Retail twin</td><td>Scan storefront, mirror catalogue in-world</td><td>Immersive store + checkout agent</td></tr>
<tr><td>Support agent</td><td>Your knowledge base + voice sample</td><td>Persona-matched agent page + spec</td></tr>
<tr><td>Training world</td><td>Workshop rooms, certification flows</td><td>Private environment on Planet.Ai</td></tr>
<tr><td>Telemarketing</td><td>Outbound scripts + CRM hooks</td><td>24/7 calling agents with reporting</td></tr>
</table></div>
""")
)

# ============================================================ TOOLS
TOOLS = [
 ("MagicStudio", "Make beautiful images, with the magic of AI", "Remove backgrounds, extend canvases and generate product-ready visuals from a single prompt.", "https://magicstudio.com", ["AI-driven experiences","Personalized content","Interactive media"]),
 ("Wordtune", "Reach your professional potential", "Everyone has tons of work to get through. Choose Wordtune Generative AI to speed up their tasks. Trusted by over 2 million users from 100+ countries.", "https://www.wordtune.com", ["2M+ users","100+ countries","Rewrite","Summarize"]),
 ("Acrolinx", "Make your writing standards… STANDARD", "Whether a company has written 100,000 words or 1 billion, Acrolinx makes sure each one reflects your style guide.", "https://www.acrolinx.com", ["Style guide","Governance"]),
 ("Brandwatch", "Understand + engage at the speed of social", "Forbes 100 most valuable brands trust Brandwatch — the social suite built for our fast-moving world.", "https://www.brandwatch.com", ["Forbes 100 trusted","Listening"]),
 ("Craiyon", "Free AI image generator", "Text prompt in, nine royalty-free images out. Built in-house since 2022 by our own model and research team.", "labs.html", ["Free","Royalty-free"]),
 ("Zoom AI Companion", "AI-powered collaboration platform", "Zoom AI Companion for Zoom Phone, Team Chat, Events and Contact Center. Ask AI Companion anything inside Zoom Workplace.", "https://www.zoom.com", ["Phone","Team Chat","Events"]),
]
TOOLS2 = [
 ("Re-Face AI", "Videos &amp; face swaps", "Swap identities into short-form video for social, ads and entertainment with consent-safe pipelines.", "labs.html"),
 ("Ai.Records", "Song lyrics &amp; music", "Write, structure and produce original lyrics and tracks for your metaverse venue or brand.", "labs.html"),
 ("AI AppBuilder", "Prompt-to-mobile-app", "Describe the app you want; get screens, logic and a build you can ship to stores.", "enterprise.html"),
 ("MyBUY'o", "Biometric verification &amp; payments", "Enroll once, pay with your face or voice across the virtual retail network.", "https://mybuyo-biometric-saas.vercel.app"),
 ("Plagiarism Analyzer", "Written content checks", "Scan drafts for originality before you publish to your blog, store or metaverse signage.", "labs.html"),
 ("Bird Species Predictor", "Characteristic-based ID", "A classic demo model: describe a bird, get the species. Great for AI education labs.", "education.html"),
]
def tool_cards(rows, chips=True):
    out = '<div class="grid-3 reveal">'
    for name, tag, desc, href, ch in [(r[0], r[1], r[2], r[3], r[4] if len(r) > 4 else []) for r in rows]:
        ext = ' target="_blank" rel="noopener noreferrer"' if href.startswith('http') else ''
        out += f"""<article class="card"><span class="glow-line"></span><h3>{name}</h3><p style="font-family:var(--font-head);font-size:13px;color:var(--cyan);margin:-6px 0 10px">{tag}</p><p>{desc}</p>
<div class="tag-row" style="margin-top:14px">{''.join(f'<span class="chip">{c}</span>' for c in ch)}</div>
<a class="btn btn-sm btn-ghost" style="margin-top:16px" href="{href}"{ext}>Visit →</a></article>"""
    return out + '</div>'
P['tools.html'] = dict(
 title="Free AI Tools Directory — Ai'Social Sponsored Tools | Ai Metaverse",
 desc="Sponsored AI tools that help you write, create videos, images, music and prompts with calls to action: MagicStudio, Wordtune, Acrolinx, Brandwatch, Craiyon, Zoom AI Companion and more.",
 body=hero("Free AI Tools Directory", None, "Free AI Tools Directory", "Take advantage of", "Ai'Social",
   "The sponsored AI tools below can help you write, create videos, images, music, and suggestive prompts with calls to action. Grow your reach and get more business with social media.")
 + sec("dir", shead("Sponsored directory", "Six tools our community", "actually uses", "Each link opens the vendor in a new tab; Craiyon stays in-house.") + tool_cards(TOOLS))
 + sec("more", shead("In-house &amp; partner labs", "Six more from", "Ai-Labs", "Built by us or by partners we trust.") + tool_cards([(a,b,c,d) for a,b,c,d in TOOLS2]))
)

# ============================================================ LABS
P['labs.html'] = dict(
 title="Access Ai-Labs — Craiyon, Generation Modes & Sandbox | Ai Metaverse",
 desc="Supercharge your artistic Kre8tivty: Craiyon free AI image generation, text/image/video/object generation modes, model sandbox with supercomputing behind it.",
 body=hero("Access Ai-Labs", None, "Access Ai-Labs", "Stop imagining,", "start creating",
   "Craiyon is the new kid on the tech block and the best AI art generator in our community's words — the brainchild of our CEO, lead researcher and AI hero, Boris Dayma. Since 2022 we've been ushering in the next era of AI image generation.")
 + sec("modes", shead("Generation modes", "Four ways to", "make something", "Pick a mode, prompt it, iterate. Your companion can prompt with you.") + """
<div class="grid-4 reveal">
 <article class="card"><h3>Text</h3><p>Copy, scripts, code and translation with models tuned for your brand voice.</p></article>
 <article class="card"><h3>Image</h3><p>“If you can dream it, Craiyon can draw it.” Nine royalty-free variants per prompt.</p></article>
 <article class="card"><h3>Video</h3><p>Short-form video, face swaps and social clips ready for YouTube, TikTok and Reels.</p></article>
 <article class="card"><h3>Object</h3><p>3D objects and scanned real-world assets you can drop straight into a world.</p></article>
</div>
<div class="callout good reveal" style="margin-top:24px"><b>Royalty-free by default.</b> Everything you kre8te here is yours to keep and sell — no watermark, no licence maze.</div>
""")
 + sec("sandbox", shead("The sandbox", "Build, train, validate, test,", "deploy", "A hosted sandbox with supercomputing behind it — the same pipeline enterprise uses.") + """
<div class="grid-3 reveal">
 <article class="card"><h3>Notebooks</h3><p>Starter agents, model cards and deployment templates from our certification track.</p><a class="btn btn-sm btn-ghost" style="margin-top:14px" href="education.html">Certification track</a></article>
 <article class="card"><h3>Model zoo</h3><p>20,000+ models for NLP, vision, speech and recommendation — filter by task and size.</p><a class="btn btn-sm btn-ghost" style="margin-top:14px" href="why-ai.html">See pillars</a></article>
 <article class="card"><h3>Prompt library</h3><p>Tested prompts for art, video, lyrics and retail copy, sorted by mode.</p><a class="btn btn-sm btn-ghost" style="margin-top:14px" href="metabox.html">Ask the Metabox</a></article>
</div>
""")
)

# ============================================================ EDUCATION
P['education.html'] = dict(
 title="Ai_Education — Learn AI Programming & Get Certified | Ai Metaverse",
 desc="Explore AI (neural networks, deep learning, computer vision, NLP, robotics) and the metaverse stack (VR, AR, blockchain, smart contracts, NFTs). Get certified.",
 body=hero("Ai_Education", None, "Ai_Education — Get certified", "Learn the stack,", "then prove it",
   "Two clouds of knowledge — the AI side and the metaverse side — plus a developer repo and a certification you can pin to your avatar profile.")
 + sec("ai", """<div class="grid-2">
 <div class="panel reveal"><h3>Explore the different AI</h3><div class="tag-row" style="margin-top:14px">
 <span class="tag">Artificial Intelligence</span><span class="tag">Neural Networks</span><span class="tag">Deep Learning</span><span class="tag">Computer Vision</span><span class="tag">Natural Language Processing</span><span class="tag">Robotics</span><span class="tag">Autonomous Systems</span></div>
 <p style="margin-top:16px">Hands-on labs for each topic live in <a href="labs.html" style="color:var(--cyan)">Ai-Labs</a>; the bird-species and plagiarism models double as teaching material.</p></div>
 <div class="panel reveal"><h3>Metaverse stack</h3><div class="tag-row" style="margin-top:14px">
 <span class="tag">Virtual Reality</span><span class="tag">Augmented Reality</span><span class="tag">Blockchain</span><span class="tag">Decentralization</span><span class="tag">Cryptocurrency</span><span class="tag">Smart Contracts</span><span class="tag">Non-Fungible Tokens (NFTs)</span></div>
 <p style="margin-top:16px">Economy and ownership modules include BitBucks mechanics and virtual retail case studies.</p></div>
</div>
<div class="grid-3 reveal" style="margin-top:24px">
 <article class="card"><span class="glow-line"></span><h3>Developer &amp; coding repo</h3><p>Notebooks, starter agents, model cards and deployment templates — everything used in the certification track.</p><a class="btn btn-sm btn-ghost" style="margin-top:14px" href="developers.html">Open developer hub</a></article>
 <article class="card"><span class="glow-line"></span><h3>Get certified</h3><p>Learn AI programming &amp; development with hands-on labs, then publish the credential to your avatar profile.</p><a class="btn btn-sm" style="margin-top:14px" href="signup.html">Enroll free</a></article>
 <article class="card"><span class="glow-line"></span><h3>Teach with your agent</h3><p>Forged agents can tutor: set the role to Educator and it teaches from your own persona.</p><a class="btn btn-sm btn-ghost" style="margin-top:14px" href="avatar-create.html">Forge an educator</a></article>
</div>
""")
)

# ---------- embedded AI Gifts & Gadgets storefront (store/aig-store.html) ----------
_store = io.open(os.path.join(ROOT, 'store', 'aig-store.html'), encoding='utf-8').read()
STORE_CSS = _store.split('<style>', 1)[1].split('</style>', 1)[0]
STORE_BODY = _store.split('<body>', 1)[1].rsplit('<script>', 1)[0]
STORE_JS = _store.rsplit('<script>', 1)[1].rsplit('</script>', 1)[0]
STORE_SECTION = (
  '<section class="sec-tight" id="gifts"><div class="wrap" style="max-width:1080px">'
  '<div class="sec-head center reveal"><span class="eyebrow"><span class="dot"></span> Featured storefront</span>'
  '<h2 class="h-lg">AI Gifts &amp; <span class="grad-text">Gadgets</span></h2>'
  '<p class="lead">Summer 2027 collection — AI-powered wearables from our Kre8tive Konceptz storefront, embedded live below.</p></div>'
  '<style>\n' + STORE_CSS + '\n.aig-store-wrapper{min-height:0;border-radius:24px;border:1px solid rgba(102,126,234,.25)}\n</style>\n'
  + STORE_BODY +
  '</div></section>\n'
)
STORE_EXTRA = '<script>\n' + STORE_JS + '\n</script>\n'

# ---------- embedded Metaverse Communities page (store/communities.html) ----------
_comm = io.open(os.path.join(ROOT, 'store', 'communities.html'), encoding='utf-8').read()
COMM_CSS = _comm.split('<style>', 1)[1].split('</style>', 1)[0]
COMM_BODY = _comm.split('<body>', 1)[1].rsplit('<script>', 1)[0]
COMM_JS = _comm.rsplit('<script>', 1)[1].rsplit('</script>', 1)[0]

def scope_css(css, sc='.mvc-embed'):
    import re as _re
    css = _re.sub(r'/\*.*?\*/', '', css, flags=_re.S)   # comments would poison prefixed selectors
    # Stash @keyframes blocks verbatim: their inner selectors (from/to/0%) are NOT CSS selectors
    # and must never be prefixed, or the browser drops the whole animation.
    _kf = []
    def _stash_kf(m):
        _kf.append(m.group(0))
        return '\x00KF%d\x00{}' % (len(_kf) - 1)   # self-contained dummy rule so it can't glue onto the next selector
    css = _re.sub(r'@keyframes\s+[\w-]+\s*\{(?:[^{}]*\{[^{}]*\})*[^{}]*\}', _stash_kf, css)
    def prefix(sel_group):
        out = []
        for sel in sel_group.split(','):
            sel = sel.strip()
            if not sel: continue
            if sel in (':root', 'body', 'html'): out.append(sc)
            elif sel == '*': out.append(sc + ' *')
            elif sel.startswith(sc) or sel.startswith('@'): out.append(sel)
            else: out.append(sc + ' ' + sel)
        return ', '.join(out)
    def transform(block):
        def repl(m):
            sel, body = m.group(1), m.group(2)
            if sel.strip().startswith('@') or '\x00KF' in sel: return m.group(0)
            return prefix(sel) + ' {' + body + '}'
        return _re.sub(r'([^{}]+)\{([^{}]*)\}', repl, block)
    def media_repl(m):
        return m.group(1) + '{' + transform(m.group(2)) + '}'
    css = _re.sub(r'(@media[^{]+\{)((?:[^{}]*\{[^{}]*\})*[^{}]*)\}', media_repl, css)
    css = transform(css)
    for i, blk in enumerate(_kf):
        css = css.replace('\x00KF%d\x00{}' % i, blk)
    return css

COMM_BODY = COMM_BODY.replace('href="#" class="card-btn"', 'href="worlds.html" class="card-btn"')
COMM_JS = COMM_JS.replace("querySelectorAll('.tag')", "querySelectorAll('.mvc-embed .tag')")
COMMUNITIES_SECTION = (
  '<section class="sec" id="communities"><div class="wrap" style="max-width:1240px">'
  '<style>\n' + scope_css(COMM_CSS) + '\n</style>\n'
  '<div class="mvc-embed">' + COMM_BODY + '</div>'
  '<div class="callout good reveal" style="margin-top:30px"><b>Bring your agent to the party.</b> Forge a companion in four steps and it will greet these communities in your voice. '
  '<a href="avatar-create.html" style="color:var(--cyan);text-decoration:underline">Clone yourself virtually →</a></div>'
  '</div></section>\n'
)
COMM_EXTRA = '<script>\n' + COMM_JS + '\n</script>\n'

# ---------- embedded Ai.RECORDS studio (store/airecords.html) ----------
_air = io.open(os.path.join(ROOT, 'store', 'airecords.html'), encoding='utf-8').read()
AIR_CSS = _air.split('<style>', 1)[1].split('</style>', 1)[0]
AIR_BODY = _air.split('<body>', 1)[1].rsplit('<script>', 1)[0]
AIR_JS = _air.rsplit('<script>', 1)[1].rsplit('</script>', 1)[0]
import re as _re2
AIR_BODY = _re2.sub(r'<nav>.*?</nav>', '', AIR_BODY, flags=_re2.S)
AIR_BODY = _re2.sub(r'<!-- Footer -->.*?</footer>', '', AIR_BODY, flags=_re2.S)
AIR_BODY = AIR_BODY.replace('<img src="https://img1.wsimg.com', '<img onerror="this.remove()" loading="lazy" src="https://img1.wsimg.com')
AIR_JS = AIR_JS.replace("querySelectorAll('.control-btn')", "querySelectorAll('.air-embed .control-btn')")
AIR_LYRIC_JS = open(os.path.join(ROOT, 'store', 'air-lyrics.js'), encoding='utf-8').read()
RECORDS_SECTION = (
  '<section class="sec-tight" id="records-studio"><div class="wrap" style="max-width:1240px">'
  '<style>\n' + scope_css(AIR_CSS, '.air-embed') + '\n.air-embed .gallery-item{background:linear-gradient(135deg,#241650,#0a0620)}\n.air-embed .container{padding:20px 0}\n</style>\n'
  '<div class="air-embed">' + AIR_BODY + '</div>'
  '</div></section>\n'
)
RECORDS_EXTRA = '<script>\n' + AIR_JS + '\n' + AIR_LYRIC_JS + '\n</script>\n'

# ---------- embedded ExploreMars virtual real-estate (store/exploremars.html) ----------
_mars = io.open(os.path.join(ROOT, 'store', 'exploremars.html'), encoding='utf-8').read()
MARS_CSS = _mars.split('<style>', 1)[1].split('</style>', 1)[0]
MARS_BODY = _mars.split('<body>', 1)[1].rsplit('<script>', 1)[0]
MARS_JS = _mars.rsplit('<script>', 1)[1].rsplit('</script>', 1)[0]
MARS_JS = MARS_JS.replace('.innerText', '.textContent')  # jsdom-safe + identical in browsers
import re as _re3
MARS_BODY = _re3.sub(r'<nav>.*?</nav>', '', MARS_BODY, flags=_re3.S)
MARS_BODY = _re3.sub(r'<!-- Footer -->.*?</footer>', '', MARS_BODY, flags=_re3.S)
MARS_SECTION = (
  '<section class="sec-tight" id="mars-estate"><div class="wrap" style="max-width:1240px">'
  '<style>\n' + scope_css(MARS_CSS, '.mx-embed') + '\n.mx-embed .hero{padding:40px 0 30px}\n</style>\n'
  '<div class="mx-embed">' + MARS_BODY + '</div>'
  '</div></section>\n'
)
MARS_EXTRA = '<script>\n' + MARS_JS + '\n</script>\n'

# ---------- embedded BitBucks learn-&-earn (store/bitbucks.html) ----------
_bb = io.open(os.path.join(ROOT, 'store', 'bitbucks.html'), encoding='utf-8').read()
BB_CSS = _bb.split('<style>', 1)[1].split('</style>', 1)[0]
BB_BODY = _bb.split('<body>', 1)[1].rsplit('<script>', 1)[0]
BB_JS = _bb.rsplit('<script>', 1)[1].rsplit('</script>', 1)[0]
BB_JS = BB_JS.replace('.innerText', '.textContent')  # jsdom-safe + identical in browsers
import re as _re4
BB_BODY = _re4.sub(r'<nav>.*?</nav>', '', BB_BODY, flags=_re4.S)
BB_BODY = _re4.sub(r'<!-- Footer -->.*?</footer>', '', BB_BODY, flags=_re4.S)
BITBUCKS_SECTION = (
  '<section class="sec-tight" id="bitbucks-earn"><div class="wrap" style="max-width:1240px">'
  '<style>\n' + scope_css(BB_CSS, '.bb-embed') + '\n.bb-embed .hero{padding:50px 0 40px}\n</style>\n'
  '<div class="bb-embed">' + BB_BODY + '</div>'
  '</div></section>\n'
)
BITBUCKS_EXTRA = '<script>\n' + BB_JS + '\n</script>\n'

# ---------- embedded Agentik AI CRM (store/agentik-crm.html) ----------
_crm = io.open(os.path.join(ROOT, 'store', 'agentik-crm.html'), encoding='utf-8').read()
CRM_CSS = _crm.split('<style>', 1)[1].split('</style>', 1)[0]
CRM_BODY = _crm.split('<body>', 1)[1].rsplit('<script>', 1)[0]
CRM_JS = _crm.rsplit('<script>', 1)[1].rsplit('</script>', 1)[0]
CRM_JS = CRM_JS.replace('.innerText', '.textContent')  # jsdom-safe + identical in browsers
# make view switching explicit (no implicit window.event)
CRM_JS = CRM_JS.replace('function switchView(viewId) {', 'function switchView(viewId, el) {')
CRM_JS = CRM_JS.replace('event.currentTarget.classList.add(\'active\');', 'if (el) el.classList.add(\'active\');')
for _v in ['dashboard','pipeline','contacts','calendar','automation']:
    CRM_BODY = CRM_BODY.replace('onclick="switchView(' + chr(39) + _v + chr(39) + ')"',
                                  'onclick="switchView(' + chr(39) + _v + chr(39) + ', this)"')
CRM_INTEGRATIONS = io.open(os.path.join(ROOT, 'store', 'crm-integrations.js'), encoding='utf-8').read()
CRM_OVERRIDES = (
  '.crm-embed{position:relative;height:min(880px,92vh);border-radius:20px;border:1px solid #2d3342;overflow:hidden}'
  '.crm-embed .ai-chat-widget{position:absolute;bottom:20px;right:20px;width:min(370px,72%);z-index:60}'
  '.crm-embed .toast{position:absolute;bottom:22px;left:50%;z-index:80}'
  '.crm-embed .modal{position:absolute;z-index:90}'
  '.crm-embed .kanban-board{height:calc(100% - 120px)}'
  '@media (max-width:860px){.crm-embed{height:auto}.crm-embed .sidebar{width:100%}.crm-embed{display:block}}'
)
CRM_SECTION = (
  '<section class="sec-tight" id="crm-app"><div class="wrap" style="max-width:1280px">'
  '<div class="sec-head center reveal"><span class="eyebrow"><span class="dot"></span> Free AI CRM</span>'
  '<h2 class="h-lg">Agentik AI CRM — <span class="grad-text">visual pipeline</span>, dialer &amp; automations</h2>'
  '<p class="lead">Unlimited users, 50k records, 250 AI credits/mo on the free plan. Integrations view wires real Google Sheets, Twilio and OpenAI/Ollama calls.</p></div>'
  '<style>\n' + scope_css(CRM_CSS, '.crm-embed') + '\n' + CRM_OVERRIDES + '\n</style>\n'
  '<div class="crm-embed">' + CRM_BODY + '</div>'
  '</div></section>\n'
)
CRM_EXTRA = '<script>\n' + CRM_JS + '\n' + CRM_INTEGRATIONS + '\n</script>\n'
CRM_HEAD = '<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" crossorigin="anonymous" referrerpolicy="no-referrer" />\n'

# ---------- embedded Virtual Store Builder (store/virtualstore.html) ----------
_vs = io.open(os.path.join(ROOT, 'store', 'virtualstore.html'), encoding='utf-8').read()
VS_CSS = _vs.split('<style>', 1)[1].split('</style>', 1)[0]
VS_BODY = _vs.split('<body>', 1)[1].rsplit('<script>', 1)[0]
VS_JS = _vs.rsplit('<script>', 1)[1].rsplit('</script>', 1)[0]
VS_BODY = re.sub(r'<nav>.*?</nav>', '', VS_BODY, flags=re.S)
VS_BODY = re.sub(r'<!-- Footer -->.*?</footer>', '', VS_BODY, flags=re.S)
VS_JS = VS_JS.replace('.innerText', '.textContent')
# keep the smooth-scroll handler inside the embed and hash-safe after dirform
VS_JS = VS_JS.replace('document.querySelectorAll(' + chr(39) + 'a[href^=' + chr(34) + '#' + chr(34) + ']' + chr(39) + ')',
                    'document.querySelectorAll(' + chr(39) + '.vs-embed a[href*=' + chr(34) + '#' + chr(34) + ']' + chr(39) + ')')
VS_JS = VS_JS.replace("const target = document.querySelector(this.getAttribute('href'));",
                      "const target = document.getElementById(this.getAttribute('href').split('#')[1]);")
VS_OVERRIDES = ('.vs-embed .toast{position:absolute;bottom:22px;left:50%;z-index:80}'
                '.vs-embed .hero{padding:70px 5% 60px}')
VSTORE_SECTION = (
  '<section class="sec-tight" id="vstore-builder"><div class="wrap" style="max-width:1240px">'
  '<div class="sec-head center reveal"><span class="eyebrow"><span class="dot"></span> Virtual Shopping Kre8tor</span>'
  '<h2 class="h-lg">Setup your <span class="grad-text">virtual retail store</span></h2>'
  '<p class="lead">Immersive 3D storefronts: templates, Shopify/Magento sync, try-ons, curation tools and dashboards — the builder brief below, contact form included.</p></div>'
  '<style>\n' + scope_css(VS_CSS, '.vs-embed') + '\n' + VS_OVERRIDES + '\n</style>\n'
  '<div class="vs-embed">' + VS_BODY + '</div>'
  '</div></section>\n'
)
VSTORE_EXTRA = '<script>\n' + VS_JS + '\n</script>\n'
VSTORE_HEAD = '<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" crossorigin="anonymous" referrerpolicy="no-referrer" />\n'

# ---------- embedded Commz AI outbound platform (store/commz.html) ----------
_cz = io.open(os.path.join(ROOT, 'store', 'commz.html'), encoding='utf-8').read()
CZ_CSS = _cz.split('<style>', 1)[1].split('</style>', 1)[0]
CZ_BODY = _cz.split('<body>', 1)[1].rsplit('<script>', 1)[0]
CZ_JS = _cz.rsplit('<script>', 1)[1].rsplit('</script>', 1)[0]
CZ_BODY = re.sub(r'<nav>.*?</nav>', '', CZ_BODY, flags=re.S)
CZ_BODY = re.sub(r'<!-- Footer -->.*?</footer>', '', CZ_BODY, flags=re.S)
CZ_JS = CZ_JS.replace('.innerText', '.textContent')
# clipboard-safe copy button (works in insecure contexts + jsdom)
CZ_JS = CZ_JS.replace("""        function copyCode() {
            const code = document.getElementById('codeSnippet').textContent;
            navigator.clipboard.writeText(code).then(() => {
                showToast("Code copied to clipboard!");
            });
        }""",
"""        function copyCode() {
            const code = document.getElementById('codeSnippet').textContent;
            function done(){ showToast("Code copied to clipboard!"); }
            function fallback(){
                try {
                    const ta = document.createElement('textarea');
                    ta.value = code; ta.style.position = 'fixed'; ta.style.opacity = '0';
                    document.body.appendChild(ta); ta.select();
                    document.execCommand('copy'); ta.remove(); done();
                } catch (e) { showToast("Copy blocked — select the code manually."); }
            }
            if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(code).then(done, fallback);
            else fallback();
        }""")
CZ_OVERRIDES = ('.cz-embed .toast{position:absolute;bottom:22px;left:50%;z-index:80}'
                '.cz-embed .hero{padding:70px 0 60px}'
                '.cz-embed pre{max-height:460px}')
COMMZ_SECTION = (
  '<section class="sec-tight" id="commz-outbound"><div class="wrap" style="max-width:1240px">'
  '<div class="sec-head center reveal"><span class="eyebrow"><span class="dot"></span> Hire AI Telemarketers</span>'
  '<h2 class="h-lg">Commz — AI outbound calling, <span class="grad-text">perfected</span></h2>'
  '<p class="lead">High-volume, low-latency AI phone agents that qualify leads, handle objections and sync to your CRM. Request a demo or scaffold the MVP below.</p></div>'
  '<style>\n' + scope_css(CZ_CSS, '.cz-embed') + '\n' + CZ_OVERRIDES + '\n</style>\n'
  '<div class="cz-embed">' + CZ_BODY + '</div>'
  '</div></section>\n'
)
COMMZ_EXTRA = '<script>\n' + CZ_JS + '\n</script>\n'
COMMZ_HEAD = ('<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" crossorigin="anonymous" referrerpolicy="no-referrer" />\n'
              '<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">\n')

# ---------- embedded Constellation25 AI App Builder (store/app-builder.html) ----------
_ab = io.open(os.path.join(ROOT, 'store', 'app-builder.html'), encoding='utf-8').read()
AB_CSS = _ab.split('<style>', 1)[1].split('</style>', 1)[0]
AB_BODY = _ab.split('<body>', 1)[1].rsplit('<script>', 1)[0]
AB_JS = _ab.rsplit('<script>', 1)[1].rsplit('</script>', 1)[0]
AB_JS = AB_JS.replace('.innerText', '.textContent')
AB_OVERRIDES = (
  '.ab-embed{position:relative;height:min(820px,92vh);border-radius:20px;border:1px solid rgba(255,255,255,.1);overflow:hidden}'
  '.ab-embed .loading-overlay{position:absolute;z-index:60}'
  '.ab-embed .toast{position:absolute;bottom:22px;z-index:70}'
  '.ab-embed main{overflow-y:auto}'
)
APPBUILDER_SECTION = (
  '<section class="sec-tight" id="app-builder"><div class="wrap" style="max-width:1080px">'
  '<div class="sec-head center reveal"><span class="eyebrow"><span class="dot"></span> AI AppBuilder</span>'
  '<h2 class="h-lg">Describe it. <span class="grad-text">We build it.</span></h2>'
  '<p class="lead">Vibe-code your next iOS, Android or Web app: prompt it, drop artifacts, pick platforms, and watch the agent pipeline scaffold, generate and compile.</p></div>'
  '<style>\n' + scope_css(AB_CSS, '.ab-embed') + '\n' + AB_OVERRIDES + '\n</style>\n'
  '<div class="ab-embed">' + AB_BODY + '</div>'
  '</div></section>\n'
)
APPBUILDER_EXTRA = '<script>\n' + AB_JS + '\n</script>\n'
APPBUILDER_HEAD = '<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" crossorigin="anonymous" referrerpolicy="no-referrer" />\n'

# ---------- embedded Constellation25 AI Studio / web builder (store/webstudio.html) ----------
_ws = io.open(os.path.join(ROOT, 'store', 'webstudio.html'), encoding='utf-8').read()
WS_CSS = _ws.split('<style>', 1)[1].split('</style>', 1)[0]
WS_BODY = re.split(r'<body[^>]*>', _ws, 1)[1].rsplit('<script>', 1)[0]
WS_JS = _ws.rsplit('<script>', 1)[1].rsplit('</script>', 1)[0]
WS_BODY = re.sub(r'<nav\b.*?</nav>', '', WS_BODY, flags=re.S)
WS_BODY = re.sub(r'<footer\b.*?</footer>', '', WS_BODY, flags=re.S)
WS_TW = io.open(os.path.join(ROOT, 'store', 'tailwindcdn.js'), encoding='utf-8').read()
WS_TW_CFG = ("<script>window.tailwind=window.tailwind||{};</script>"
             "<script>tailwind.config={corePlugins:{preflight:false},theme:{extend:{"
             "fontFamily:{sans:['Inter','sans-serif'],display:['Space Grotesk','sans-serif']},"
             "colors:{dark:'#020617',panel:'#0f172a',cyan:'#22d3ee',blue:'#3b82f6',gold:'#fbbf24'}}}};</script>")
WS_OVERRIDES = (
  '.ws-embed{position:relative}'
  '.ws-embed main{padding-top:40px}'
)
WEBSTUDIO_SECTION = (
  '<section class="sec-tight" id="web-studio"><div class="wrap" style="max-width:1280px">'
  '<div class="sec-head center reveal"><span class="eyebrow"><span class="dot"></span> Create Websites with AI</span>'
  '<h2 class="h-lg">Prompt-to-page, <span class="grad-text">source-grounded</span></h2>'
  '<p class="lead">Describe your vision, upload source documents, and watch Qwen WebDev generate clean code with a live side-by-side preview. The Tailwind runtime is inlined — this studio works fully offline.</p></div>'
  '<style>\n' + scope_css(WS_CSS, '.ws-embed') + '\n' + WS_OVERRIDES + '\n</style>\n'
  '<div class="ws-embed bg-grid flex flex-col">' + WS_BODY + '</div>'
  '</div></section>\n'
)
WEBSTUDIO_EXTRA = '<script>\n' + WS_JS + '\n</script>\n'
WEBSTUDIO_HEAD = ('<script>\n' + WS_TW + '\n</script>\n' + WS_TW_CFG +
  '<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" crossorigin="anonymous" referrerpolicy="no-referrer" />\n')

# ---------- embedded C25 FaceForge (store/faceforge.html) ----------
_ff = io.open(os.path.join(ROOT, 'store', 'faceforge.html'), encoding='utf-8').read()
FF_CSS = _ff.split('<style>', 1)[1].split('</style>', 1)[0]
FF_BODY = re.split(r'<body[^>]*>', _ff, 1)[1].rsplit('<script>', 1)[0]
FF_JS = _ff.rsplit('<script>', 1)[1].rsplit('</script>', 1)[0]
FF_BODY = re.sub(r'<header\b.*?</header>', '', FF_BODY, flags=re.S)
FF_OVERRIDES = '.ff-embed{position:relative}.ff-embed main{padding:30px 4% 60px}'
FACEFORGE_SECTION = (
  '<section class="sec-tight" id="faceforge"><div class="wrap" style="max-width:1080px">'
  '<div class="sec-head center reveal"><span class="eyebrow"><span class="dot"></span> Re-Face AI</span>'
  '<h2 class="h-lg">C25 FaceForge — <span class="grad-text">swap faces, reframe reality</span></h2>'
  '<p class="lead">Our white-label answer to Reface, HeyGen and Viggle: InsightFace + ONNX swap engine with a drag-and-drop studio. Runs against faceforge/app.py on your device or LAN.</p></div>'
  '<style>\n' + scope_css(FF_CSS, '.ff-embed') + '\n' + FF_OVERRIDES + '\n</style>\n'
  '<div class="ff-embed">' + FF_BODY + '</div>'
  '</div></section>\n'
)
FACEFORGE_EXTRA = '<script>\n' + FF_JS + '\n</script>\n'
FACEFORGE_HEAD = ('<script>\n' + WS_TW + '\n</script>\n' + WS_TW_CFG)

# ---------- embedded Ai4Reelz cinematic video orchestration (store/ai4reelz.html) ----------
_ar = io.open(os.path.join(ROOT, 'store', 'ai4reelz.html'), encoding='utf-8').read()
AR_CSS = _ar.split('<style>', 1)[1].split('</style>', 1)[0]
AR_BODY = re.split(r'<body[^>]*>', _ar, 1)[1].rsplit('<script>', 1)[0]
AR_JS = _ar.rsplit('<script>', 1)[1].rsplit('</script>', 1)[0]
AR_JS = AR_JS.replace('.innerText', '.textContent')
AR_BODY = re.sub(r'<nav\b.*?</nav>', '', AR_BODY, flags=re.S)
AR_BODY = re.sub(r'<footer\b.*?</footer>', '', AR_BODY, flags=re.S)
AR_TW_CFG = ("<script>window.tailwind=window.tailwind||{};</script>"
             "<script>tailwind.config={corePlugins:{preflight:false},theme:{extend:{"
             "fontFamily:{sans:['Inter','sans-serif'],display:['Space Grotesk','sans-serif']},"
             "colors:{c25:{dark:'#020617',panel:'#0f172a',cyan:'#22d3ee',blue:'#3b82f6',purple:'#8b5cf6',gold:'#fbbf24'}}}}};</script>")
AR_OVERRIDES = '.ar-embed{position:relative}.ar-embed main{padding-top:40px}'
AI4REELZ_SECTION = (
  '<section class="sec-tight" id="ai4reelz"><div class="wrap" style="max-width:1280px">'
  '<div class="sec-head center reveal"><span class="eyebrow"><span class="dot"></span> Ai4Reelz</span>'
  '<h2 class="h-lg">Cinematic AI video, <span class="grad-text">zero &ldquo;AI slop&rdquo;</span></h2>'
  '<p class="lead">Qwen + Ollama orchestrate the C25 agents — VENUS scripts, JUPITER synthesizes avatars &amp; voices, MARS edits &amp; upscales, SATURN enforces platform compliance. Initialize the workflow below.</p></div>'
  '<style>\n' + scope_css(AR_CSS, '.ar-embed') + '\n' + AR_OVERRIDES + '\n</style>\n'
  '<div class="ar-embed bg-grid flex flex-col">' + AR_BODY + '</div>'
  '</div></section>\n'
)
AI4REELZ_EXTRA = '<script>\n' + AR_JS + '\n</script>\n'
AI4REELZ_HEAD = ('<script>\n' + WS_TW + '\n</script>\n' + AR_TW_CFG +
  '<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" crossorigin="anonymous" referrerpolicy="no-referrer" />\n')

# ---------- embedded Metaverse Creator Toolkit (store/metaverse-toolkit.html) ----------
_mt = io.open(os.path.join(ROOT, 'store', 'metaverse-toolkit.html'), encoding='utf-8').read()
MT_CSS = _mt.split('<style>', 1)[1].split('</style>', 1)[0]
MT_BODY = re.split(r'<body[^>]*>', _mt, 1)[1].rsplit('<script>', 1)[0]
MT_JS = _mt.rsplit('<script>', 1)[1].rsplit('</script>', 1)[0]
MT_JS = MT_JS.replace('.innerText', '.textContent')
MT_BODY = re.sub(r'<nav\b.*?</nav>', '', MT_BODY, flags=re.S)
MT_BODY = re.sub(r'<footer\b.*?</footer>', '', MT_BODY, flags=re.S)
MT_TW_CFG = ("<script>window.tailwind=window.tailwind||{};</script>"
             "<script>tailwind.config={corePlugins:{preflight:false},theme:{extend:{"
             "fontFamily:{sans:['Inter','sans-serif'],display:['Space Grotesk','sans-serif']},"
             "colors:{c25:{dark:'#020617',panel:'#0f172a',cyan:'#22d3ee',purple:'#8b5cf6',gold:'#fbbf24'}}}}};</script>")
MT_OVERRIDES = '.mt-embed{position:relative}.mt-embed main{padding-top:40px}'
METATOOLKIT_SECTION = (
  '<section class="sec-tight" id="metaverse-toolkit"><div class="wrap" style="max-width:1280px">'
  '<div class="sec-head center reveal"><span class="eyebrow"><span class="dot"></span> Metaverse Creator Toolkit</span>'
  '<h2 class="h-lg">Build your own <span class="grad-text">metaverse</span></h2>'
  '<p class="lead">Spatial.io, Meta Horizon, Viverse or custom WebGL: generate a blueprint, then follow the four-phase workflow — setup, assets, logic, publish — with the C25 agent routing terminal.</p></div>'
  '<style>\n' + scope_css(MT_CSS, '.mt-embed') + '\n' + MT_OVERRIDES + '\n</style>\n'
  '<div class="mt-embed bg-grid flex flex-col">' + MT_BODY + '</div>'
  '</div></section>\n'
)
METATOOLKIT_EXTRA = '<script>\n' + MT_JS + '\n</script>\n'
METATOOLKIT_HEAD = ('<script>\n' + WS_TW + '\n</script>\n' + MT_TW_CFG +
  '<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" crossorigin="anonymous" referrerpolicy="no-referrer" />\n')

# ---------- embedded VR Hardware Hub (store/vr-hub.html) ----------
_vr = io.open(os.path.join(ROOT, 'store', 'vr-hub.html'), encoding='utf-8').read()
VR_CSS = _vr.split('<style>', 1)[1].split('</style>', 1)[0]
VR_BODY = re.split(r'<body[^>]*>', _vr, 1)[1].rsplit('<script>', 1)[0]
VR_JS = _vr.rsplit('<script>', 1)[1].rsplit('</script>', 1)[0]
VR_JS = VR_JS.replace("querySelectorAll('.tab-content')", "querySelectorAll('.vr-embed .tab-content')")
VR_JS = VR_JS.replace("querySelectorAll('.tab-btn')", "querySelectorAll('.vr-embed .tab-btn')")
VR_BODY = re.sub(r'<nav\b.*?</nav>', '', VR_BODY, flags=re.S)
VR_BODY = re.sub(r'<footer\b.*?</footer>', '', VR_BODY, flags=re.S)
VR_TW_CFG = ("<script>window.tailwind=window.tailwind||{};</script>"
             "<script>tailwind.config={corePlugins:{preflight:false},theme:{extend:{"
             "fontFamily:{sans:['Inter','sans-serif'],display:['Space Grotesk','sans-serif']},"
             "colors:{c25:{dark:'#020617',panel:'#0f172a',cyan:'#22d3ee',purple:'#8b5cf6',emerald:'#10b981'}}}}};</script>")
VR_OVERRIDES = '.vr-embed{position:relative}.vr-embed main{padding-top:40px}'
VRHUB_SECTION = (
  '<section class="sec-tight" id="vr-hub"><div class="wrap" style="max-width:1240px">'
  '<div class="sec-head center reveal"><span class="eyebrow"><span class="dot"></span> VR Access &amp; Hardware Hub</span>'
  '<h2 class="h-lg">From Cardboard to <span class="grad-text">mixed reality</span></h2>'
  '<p class="lead">Pick your tier — mobile viewer, tethered PC/console HMD, or premium standalone — for tailored setup steps, launchers and headset picks. SteamVR guide one click away.</p></div>'
  '<style>\n' + scope_css(VR_CSS, '.vr-embed') + '\n' + VR_OVERRIDES + '\n</style>\n'
  '<div class="vr-embed bg-grid flex flex-col">' + VR_BODY + '</div>'
  '</div></section>\n'
)
VRHUB_EXTRA = '<script>\n' + VR_JS + '\n</script>\n'
VRHUB_HEAD = ('<script>\n' + WS_TW + '\n</script>\n' + VR_TW_CFG +
  '<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" crossorigin="anonymous" referrerpolicy="no-referrer" />\n')

# ---------- embedded Metaverse World Directory (store/metaverse-directory.html) ----------
_wd = io.open(os.path.join(ROOT, 'store', 'metaverse-directory.html'), encoding='utf-8').read()
WD_CSS = _wd.split('<style>', 1)[1].split('</style>', 1)[0]
WD_BODY = re.split(r'<body[^>]*>', _wd, 1)[1].rsplit('<script>', 1)[0]
WD_JS = _wd.rsplit('<script>', 1)[1].rsplit('</script>', 1)[0]
WD_JS = WD_JS.replace("querySelectorAll('.filter-btn')", "querySelectorAll('.wd-embed .filter-btn')")
WD_JS = WD_JS.replace("querySelector('.filter-btn.active')", "querySelector('.wd-embed .filter-btn.active')")
WD_BODY = re.sub(r'<nav\b.*?</nav>', '', WD_BODY, flags=re.S)
WD_BODY = re.sub(r'<footer\b.*?</footer>', '', WD_BODY, flags=re.S)
# the search box lived in the stripped nav — relocate it above the filters
WD_SEARCH = ('<div class="max-w-7xl mx-auto mb-8 text-center">'
             '<input type="text" id="searchInput" placeholder="Search 100+ platforms…" '
             'class="bg-slate-900 border border-slate-700 rounded-full px-5 py-3 text-sm text-white '
             'focus:outline-none focus:border-c25-cyan w-full max-w-md" /></div>')
WD_BODY = WD_BODY.replace('<section class="max-w-7xl mx-auto mb-12">',
                          WD_SEARCH + '<section class="max-w-7xl mx-auto mb-12">', 1)
WD_TW_CFG = ("<script>window.tailwind=window.tailwind||{};</script>"
             "<script>tailwind.config={corePlugins:{preflight:false},theme:{extend:{"
             "fontFamily:{sans:['Inter','sans-serif'],display:['Space Grotesk','sans-serif']},"
             "colors:{c25:{dark:'#020617',panel:'#0f172a',cyan:'#22d3ee',purple:'#8b5cf6',emerald:'#10b981',gold:'#fbbf24'}}}}};</script>")
WD_OVERRIDES = '.wd-embed{position:relative}.wd-embed main{padding-top:40px}'
METADIR_SECTION = (
  '<section class="sec-tight" id="world-directory"><div class="wrap" style="max-width:1320px">'
  '<div class="sec-head center reveal"><span class="eyebrow"><span class="dot"></span> World Directory</span>'
  '<h2 class="h-lg">Explore 100s of metaverse <span class="grad-text">environments</span></h2>'
  '<p class="lead">34 tracked platforms across browser, gaming, VR-social, blockchain, enterprise and Japanese worlds — filter, search, compare and visit. Updated for 2026.</p></div>'
  '<style>\n' + scope_css(WD_CSS, '.wd-embed') + '\n' + WD_OVERRIDES + '\n</style>\n'
  '<div class="wd-embed bg-grid flex flex-col">' + WD_BODY + '</div>'
  '</div></section>\n'
)
METADIR_EXTRA = '<script>\n' + WD_JS + '\n</script>\n'
METADIR_HEAD = ('<script>\n' + WS_TW + '\n</script>\n' + WD_TW_CFG +
  '<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" crossorigin="anonymous" referrerpolicy="no-referrer" />\n')

# ---------- embedded AI Education & Prompt Hub (store/ai-education-hub.html) ----------
_ed = io.open(os.path.join(ROOT, 'store', 'ai-education-hub.html'), encoding='utf-8').read()
ED_CSS = _ed.split('<style>', 1)[1].split('</style>', 1)[0]
ED_BODY = re.split(r'<body[^>]*>', _ed, 1)[1].rsplit('<script>', 1)[0]
ED_JS = _ed.rsplit('<script>', 1)[1].rsplit('</script>', 1)[0]
ED_JS = ED_JS.replace('.innerText', '.textContent')
# fix upstream bug: searching while the 'All' tag is active returned nothing
ED_JS = ED_JS.replace("const matchesCat = filter === 'all' || p.cat === filter;",
                    "const matchesCat = String(filter).toLowerCase() === 'all' || String(p.cat).toLowerCase() === String(filter).toLowerCase();")
# scope every query to the embed so the host page's tabs/filters are untouched
for _sel in ['.view-section', '.tab-btn', '.quiz-filter', '.prompt-tag']:
    ED_JS = ED_JS.replace("querySelectorAll('" + _sel + "')", "querySelectorAll('.edu-embed " + _sel + "')")
ED_JS = ED_JS.replace("querySelector('.prompt-tag.bg-c25-cyan\\/20')", "querySelector('.edu-embed .prompt-tag.bg-c25-cyan\\/20')")
# explicit element arg instead of implicit window.event
ED_JS = ED_JS.replace('function filterPrompts(cat) {', 'function filterPrompts(cat, el) {')
ED_JS = ED_JS.replace('event.target.classList.remove(', 'el.classList.remove(')
ED_JS = ED_JS.replace('event.target.classList.add(', 'el.classList.add(')
ED_BODY = re.sub(r'onclick="filterPrompts\(' + chr(39) + '([A-Za-z]+)' + chr(39) + '\)"',
                    lambda m: 'onclick="filterPrompts(' + chr(39) + m.group(1) + chr(39) + ', this)"', ED_BODY)
ED_BODY = re.sub(r'<nav\b.*?</nav>', '', ED_BODY, flags=re.S)
ED_BODY = re.sub(r'<footer\b.*?</footer>', '', ED_BODY, flags=re.S)
# the tab bar lived in the stripped nav — relocate it above the first view
ED_TABS = ('<div class="max-w-6xl mx-auto mb-10 flex flex-wrap justify-center gap-6">'
           '<button onclick="switchTab(\'quiz\')" id="tab-quiz" class="tab-btn tab-active text-sm font-medium text-slate-300 hover:text-white transition-colors pb-1">Quiz Cards</button>'
           '<button onclick="switchTab(\'prompts\')" id="tab-prompts" class="tab-btn text-sm font-medium text-slate-400 hover:text-white transition-colors pb-1">Prompt Library (1000+)</button>'
           '<button onclick="switchTab(\'certs\')" id="tab-certs" class="tab-btn text-sm font-medium text-slate-400 hover:text-white transition-colors pb-1">Certifications</button>'
           '<button onclick="switchTab(\'opensource\')" id="tab-opensource" class="tab-btn text-sm font-medium text-slate-400 hover:text-white transition-colors pb-1">Open Source</button>'
           '</div>')
ED_BODY = ED_BODY.replace('<main class="flex-1 pt-24 pb-20 px-6">',
                          '<main class="flex-1 pt-24 pb-20 px-6">' + ED_TABS, 1)
# clipboard polyfill for insecure contexts
ED_JS = ("if (!navigator.clipboard) { navigator.clipboard = { writeText: function (t) { return new Promise(function (res, rej) { try { var ta = document.createElement('textarea'); ta.value = t; ta.style.position = 'fixed'; ta.style.opacity = '0'; document.body.appendChild(ta); ta.select(); document.execCommand('copy'); ta.remove(); res(); } catch (e) { rej(e); } }); } }; }\n"
         + ED_JS)
ED_TW_CFG = ("<script>window.tailwind=window.tailwind||{};</script>"
             "<script>tailwind.config={corePlugins:{preflight:false},theme:{extend:{"
             "fontFamily:{sans:['Inter','sans-serif'],display:['Space Grotesk','sans-serif']},"
             "colors:{c25:{dark:'#020617',panel:'#0f172a',cyan:'#22d3ee',purple:'#8b5cf6',gold:'#fbbf24'}}}}};</script>")
ED_OVERRIDES = '.edu-embed{position:relative}.edu-embed main{padding-top:26px}'
EDUHUB_SECTION = (
  '<section class="sec-tight" id="ai-education-hub"><div class="wrap" style="max-width:1240px">'
  '<div class="sec-head center reveal"><span class="eyebrow"><span class="dot"></span> Ai_Education — Get certified</span>'
  '<h2 class="h-lg">Learn AI programming &amp; <span class="grad-text">development</span></h2>'
  '<p class="lead">Flip-card quizzes (Termux, prompting, certifications), a copy-paste prompt library, certification paths from beginner to Stanford/MIT, and the open-source curriculum table.</p></div>'
  '<style>\n' + scope_css(ED_CSS, '.edu-embed') + '\n' + ED_OVERRIDES + '\n</style>\n'
  '<div class="edu-embed bg-grid flex flex-col">' + ED_BODY + '</div>'
  '</div></section>\n'
)
EDUHUB_EXTRA = '<script>\n' + ED_JS + '\n</script>\n'
EDUHUB_HEAD = ('<script>\n' + WS_TW + '\n</script>\n' + ED_TW_CFG +
  '<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" crossorigin="anonymous" referrerpolicy="no-referrer" />\n')

# ---------- embedded aiEDU portal (store/ai-education.html) ----------
_e2 = io.open(os.path.join(ROOT, 'store', 'ai-education.html'), encoding='utf-8').read()
ED2_CSS = _e2.split('<style>', 1)[1].split('</style>', 1)[0]
ED2_BODY = re.split(r'<body[^>]*>', _e2, 1)[1].rsplit('</body>', 1)[0]
# strip the top utility bar, sticky nav and footer (shell provides chrome)
ED2_BODY = re.sub(r'<div class="bg-edu-panel[^"]*">.*?</div>\s*</div>', '', ED2_BODY, count=1, flags=re.S)
ED2_BODY = re.sub(r'<nav\b.*?</nav>', '', ED2_BODY, flags=re.S)
ED2_BODY = re.sub(r'<footer\b.*?</footer>', '', ED2_BODY, flags=re.S)
# no page-level script in this module; the newsletter form uses an inline onsubmit
ED2_TW_CFG = ("<script>window.tailwind=window.tailwind||{};</script>"
              "<script>tailwind.config={corePlugins:{preflight:false},theme:{extend:{"
              "fontFamily:{sans:['Inter','sans-serif'],display:['Space Grotesk','sans-serif']},"
              "colors:{edu:{dark:'#020617',panel:'#0f172a',cyan:'#22d3ee',purple:'#8b5cf6',emerald:'#10b981'}}}}};</script>")
ED2_OVERRIDES = '.ed-embed{position:relative}.ed-embed main{padding-top:10px}'
AIEDU_SECTION = (
  '<section class="sec-tight" id="ai-education"><div class="wrap" style="max-width:1240px">'
  '<div class="sec-head center reveal"><span class="eyebrow"><span class="dot"></span> aiEDU \u2014 Get Educated with AI</span>'
  '<h2 class="h-lg">AI literacy for <span class="grad-text">every student</span></h2>'
  '<p class="lead">Role-based learning paths (students, educators, professionals), the 3-month strategic framework to fluency, the aiEDU 501(c)(3) mission, partners and the educator newsletter.</p></div>'
  '<style>\n' + scope_css(ED2_CSS, '.ed-embed') + '\n' + ED2_OVERRIDES + '\n</style>\n'
  '<div class="ed-embed bg-grid flex flex-col">' + ED2_BODY + '</div>'
  '</div></section>\n'
)
AIEDU_EXTRA = ''
AIEDU_HEAD = ('<script>\n' + WS_TW + '\n</script>\n' + ED2_TW_CFG +
  '<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" crossorigin="anonymous" referrerpolicy="no-referrer" />\n')

# ============================================================ WORLDS
WORLDS = ['Tivoli Cloud','Twin Planet Metaverse','Vpark','VRland','Hiberworld','Mona','Somnium Space','The Nemesis','VRChat','Yabal','Alphabatem','Atlas Space','Spatial','Geenee AR','Immersed','Imsimity','Magecosmos','Marine Cup','Mazing XR','MeetInVR','Anything World','Therack','Deverse World','Dubbz','Amber Metaverse','Alter.game','Aftermath Island','Mini Royale','Animo','In Town Metaverse','Hedra Bot Face','Couch.live','Avatar Cam','Mzaalo','Fleepas','Frolic','GB Arena','iChalleng1','LootOut','Metaverser','Paintball Arena','House of Math','3DBear','EducaVerse','ImEdu','Metazoome','Opto.city','Syglass','Twin Science Games']
HUES = [('#1b1040','#0a0620'),('#3a0d4d','#12041c'),('#0b2f3a','#04141a'),('#2c1a5e','#0d0722'),('#3a2200','#160c02'),('#062a2a','#02100f')]
wtiles = '<div class="wtiles reveal">' + ''.join(
  f'<a class="wtile" style="--w1:{HUES[i%6][0]};--w2:{HUES[i%6][1]}" href="metabox.html" title="Route through Planet.Ai"><span class="d"></span><b>{w}</b></a>'
  for i, w in enumerate(WORLDS)) + '</div>'
P['ai-education-hub.html'] = dict(
 head=EDUHUB_HEAD,
 extra=EDUHUB_EXTRA,
 title="AI Education & Prompt Hub — Learn AI Programming & Get Certified | Ai Metaverse",
 desc="Learn AI programming & development: flip-card quizzes, 1000+ prompt library with copy buttons, certification paths (beginner to advanced) and open-source curriculums + boilerplates.",
 body=EDUHUB_SECTION
)

P['ai-education.html'] = dict(
 head=AIEDU_HEAD,
 extra=AIEDU_EXTRA,
 title="Get Educated with AI \u2014 aiEDU Portal | Ai Metaverse",
 desc="aiEDU portal: AI literacy and readiness with role-based learning paths for students, educators and professionals, the 3-month strategic framework, mission, partners and the educator newsletter.",
 body=AIEDU_SECTION
)

P['metaverse-directory.html'] = dict(
 head=METADIR_HEAD,
 extra=METADIR_EXTRA,
 title="Metaverse World Directory — 100+ Virtual Worlds | Ai Metaverse",
 desc="Explore 100s of metaverse environments: 34 tracked platforms with filters, live search, comparison table and direct links — browser, gaming, VR social, blockchain, enterprise, Japanese.",
 body=METADIR_SECTION
)

P['vr-hub.html'] = dict(
 head=VRHUB_HEAD,
 extra=VRHUB_EXTRA,
 title="VR Access & Hardware Hub — Cardboard to HMD | Ai Metaverse",
 desc="Access VR virtual reality platforms: interactive hardware spectrum (mobile, tethered, standalone), on-demand SteamVR setup guide, headset store and VR support.",
 body=VRHUB_SECTION
)

P['metaverse-toolkit.html'] = dict(
 head=METATOOLKIT_HEAD,
 extra=METATOOLKIT_EXTRA,
 title="Metaverse Creator Toolkit — Build Your Own Metaverse | Ai Metaverse",
 desc="Build your own metaverse: AI blueprint generator for Spatial.io, Meta Horizon Worlds, Viverse or custom WebGL/Three.js, plus the four-phase creator workflow and how-to videos.",
 body=METATOOLKIT_SECTION
)

P['ai4reelz.html'] = dict(
 head=AI4REELZ_HEAD,
 extra=AI4REELZ_EXTRA,
 title="Ai4Reelz — Cinematic AI Video Orchestration | Ai Metaverse",
 desc="Create YouTube/social videos with AI: Ai4Reelz routes your niche, format and likeness choices through VENUS, JUPITER, MARS, SATURN and PLUTO agents with cinematic prompting rules and platform compliance.",
 body=AI4REELZ_SECTION
)

P['faceforge.html'] = dict(
 head=FACEFORGE_HEAD,
 extra=FACEFORGE_EXTRA,
 title="C25 FaceForge — AI Face Swap & Video Reface | Ai Metaverse",
 desc="Create videos and face swaps with Re-Face AI: C25 FaceForge studio — upload a source face and target image, swap with the local InsightFace + ONNX engine, download the result.",
 body=FACEFORGE_SECTION
)

P['webstudio.html'] = dict(
 head=WEBSTUDIO_HEAD,
 extra=WEBSTUDIO_EXTRA,
 title="AI Studio — Create Websites with AI Precision | Ai Metaverse",
 desc="Create websites with AI: prompt-to-page builder with live preview, source-grounded notebooks, study/content generation and pricing — Qwen WebDev studio.",
 body=WEBSTUDIO_SECTION
)

P['app-builder.html'] = dict(
 head=APPBUILDER_HEAD,
 extra=APPBUILDER_EXTRA,
 title="AI App Builder — Describe It, We Build It | Ai Metaverse",
 desc="Create mobile apps with the AI AppBuilder: prompt-driven iOS/Android/Web generation with artifact upload, platform chips and a live agent build pipeline.",
 body=APPBUILDER_SECTION
)

P['commz.html'] = dict(
 head=COMMZ_HEAD,
 extra=COMMZ_EXTRA,
 title="Commz — Hire AI Telemarketers | AI Outbound Calling Platform | Ai Metaverse",
 desc="Hire AI telemarketers: Commz AI outbound calling platform — demo signup, Twilio/Deepgram/Qwen/ElevenLabs architecture, C25 agent delegation, pricing and a copyable FastAPI MVP scaffold.",
 body=COMMZ_SECTION
)

P['vstore.html'] = dict(
 head=VSTORE_HEAD,
 extra=VSTORE_EXTRA,
 title="Virtual Store Builder — Immersive 3D Retail Environments | Ai Metaverse",
 desc="Setup a virtual retail store: immersive 3D environments, pre-built templates, Shopify/Magento integration, virtual try-ons, curation tools and conversion dashboards.",
 body=VSTORE_SECTION
)

P['crm.html'] = dict(
 head=CRM_HEAD,
 extra=CRM_EXTRA,
 title="Agentik AI CRM — Free Visual Customer Relationship Management | Ai Metaverse",
 desc="Create a free AI CRM: visual sales pipeline with drag & drop leads, contacts table, online calendar, AI automation hub, auto-dialer, lead scraper and an AI assistant — with real Google Sheets / Twilio / OpenAI-Ollama integration paths.",
 body=CRM_SECTION
)

P['bitbucks.html'] = dict(
 extra=BITBUCKS_EXTRA,
 title="BitBucks — Share & Learn to Earn Bitcoin | Ai Metaverse",
 desc="Earn BitBucks: learn-&-earn Bitcoin modules with rewards, share & refer bonuses, mobile-number transfers and German-regulated custody.",
 body=BITBUCKS_SECTION
)

P['mars.html'] = dict(
 extra=MARS_EXTRA,
 title="ExploreMars — Virtual Real Estate & MARSFIAT | Ai Metaverse",
 desc="Search virtual real-estate with AI: drop PIX pins on the Mars map, claim parcels, adopt Astropet NFTs, and explore the MARSAVERSE.",
 body=MARS_SECTION
)

P['records.html'] = dict(
 extra=RECORDS_EXTRA,
 title="Ai.RECORDS — Create Your Own Song Lyrics | Ai Metaverse",
 desc="Ai.RECORDS studio: AI lyric generator, mixer dashboard, open source record label vision, featured talents and subscriptions — the page your Create Your Own Song Lyrics button opens.",
 body=RECORDS_SECTION
)

P['communities.html'] = dict(
 extra=COMM_EXTRA,
 title="Find Friends — Metaverse Communities | Ai Metaverse",
 desc="Find friends in metaverse communities: virtual concerts, in-store shopping, social hangouts, blockchain games, digital art and historical AR worlds.",
 body=COMMUNITIES_SECTION
)

P['worlds.html'] = dict(
 title="Virtual Worlds — 100s of Metaverse Environments | Ai Metaverse",
 desc="Tivoli Cloud, Somnium Space, VRChat, Mona, Spatial, educational worlds, arenas and classrooms. Tap any world to route through Planet.Ai.",
 body=hero("Virtual Worlds", None, "Explore the Ai_Metaverse", "100s of environments,", "one Meta-Port",
   "Social platforms, gaming worlds, enterprise spaces, classrooms and arenas. Tap any tile and the Metabox routes you through Planet.Ai — attach your avatar voice before you enter.")
 + sec("grid", shead("The directory", "Tap a world to", "access Planet.Ai", "Green dot = community online right now.") + wtiles +
  '<p class="worlds-note" style="margin-top:18px">…and dozens more added by creators every month. <a href="metabox.html" style="color:var(--cyan)">Ask the Metabox</a> for a guided route.</p>')
 + sec("cardboard", """<div class="callout reveal"><b>🥽 Google Cardboard:</b> visit new places, play immersive games, fly through space and more. Get it, fold it and look inside — a VR experience starting with a simple viewer anyone can build or buy. <a href="https://arvr.google.com/cardboard/get-cardboard/" target="_blank" rel="noopener noreferrer" style="color:var(--cyan)">Get Cardboard →</a></div>""")
)

# ============================================================ SHOP
P['shop.html'] = dict(
 extra=STORE_EXTRA,
 title="Virtual Shopping Kre8tor — Gadgets, Stores & BitBucks | Ai Metaverse",
 desc="Shop the latest must-have AI gadgets and accessories, set up a virtual retail store, millions of virtual fashion and home décor items, biometric checkout and BitBucks rewards.",
 body=hero("Virtual Shopping Kre8tor", None, "Meta-Port commerce", "Shop in-store,", "virtually",
   "Millions of virtual fashion, home décor and clothing items are available in the virtual world AiMetaverse — and everything you need to go from selfie to fully rigged, world-ready digital twin.")
 + STORE_SECTION
 + sec("gear", shead("Must-have gear", "AI gadgets &amp;", "accessories", "From capture rigs to prompt packs.") + """
<div class="grid-3 reveal">
 <article class="card"><h3>Meta Avatar Setup</h3><p>Selfie → rigged 3D avatar with voice and birth-chart personality traits.</p></article>
 <article class="card"><h3>Environment Kits</h3><p>Pre-built rooms, venues and planets — drop in and host in minutes.</p></article>
 <article class="card"><h3>HMD &amp; Sensors</h3><p>Wearable consumer head-mounted displays with AI-powered sensors.</p></article>
 <article class="card"><h3>3D Scanning Rig</h3><p>Reconstruct real-world objects into virtual versions you can sell.</p></article>
 <article class="card"><h3>Free Cloud Storage</h3><p>Members get free storage cloud services for assets, renders and worlds.</p></article>
 <article class="card"><h3>Creator Accessories</h3><p>Controllers, capture gear and prompt packs for the Kre8tor workflow.</p></article>
</div>""")
 + sec("store", shead("Open for business", "Set up a virtual", "retail store", "Four steps from empty lot to open sign.") + """
<div class="grid-4 reveal">
 <article class="card"><h3>1 · Scan</h3><p>3D-scan your real storefront or start from a kit.</p></article>
 <article class="card"><h3>2 · Stock</h3><p>Import catalogue; AI writes descriptions and prices in-world.</p></article>
 <article class="card"><h3>3 · Staff</h3><p>Attach a forged agent as your retail assistant — it never sleeps.</p></article>
 <article class="card"><h3>4 · Checkout</h3>Biometric payments with <a href="https://mybuyo-biometric-saas.vercel.app" target="_blank" rel="noopener noreferrer" style="color:var(--cyan)">MyBUY'o</a>; customers earn BitBucks round-ups.</article>
</div>
<div class="callout reveal" style="margin-top:24px"><b>BitBucks:</b> AI-powered purchase &amp; round-up rewards across the whole virtual economy.</div>""")
)

# ============================================================ METABOX
P['metabox.html'] = dict(
 title="Conversate with the Metabox — Live AI Chat | Ai Metaverse",
 desc="The Metabox is your always-on guide to the Ai Metaverse: avatars, royalty-free art, virtual worlds, enterprise agents and education. Type or talk.",
 body=hero("Metabox", None, "Live AI assistant", "Conversate with", "the Metabox",
   "Your always-on guide to the Ai Metaverse. Ask about avatar creation, environments, enterprise agents, or any of our 20,000+ AI models. The humanoid companion in the corner shares this brain — and this voice.")
 + sec("chat", """<div class="chatbox reveal" id="mbox">
  <div class="cbar"><i></i> metabox // session <span style="margin-left:auto;color:var(--lime)">online</span></div>
  <div class="clog" id="mlog" aria-live="polite">
    <div class="m bot"><span class="who">Metabox</span>Welcome to the Ai Metaverse 👋 I can help you clone your avatar, generate royalty-free art, find a virtual world, or deploy a custom agent model. What would you like to create today?</div>
  </div>
  <form id="mform" autocomplete="off"><label for="minput" style="position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0)">Message the Metabox</label>
  <input id="minput" maxlength="240" placeholder="Ask the Metabox anything…" /><button class="btn btn-sm" type="submit">Send</button></form>
</div>
<div class="hm-sugs reveal" id="pg-sugs" style="margin-top:14px"></div>
<div class="reveal" style="margin-top:14px"><div class="hm-ads" id="pg-ads"></div></div>
<div class="tag-row reveal" style="margin-top:16px">
 <button class="tag mb-q" data-q="How do I clone my avatar?">clone my avatar</button>
 <button class="tag mb-q" data-q="Generate royalty-free AI art">free AI art</button>
 <button class="tag mb-q" data-q="Show me virtual worlds to explore">explore worlds</button>
 <button class="tag mb-q" data-q="What AI tools are free?">free tools</button>
 <button class="tag mb-q" data-q="Tell me about AI for enterprise">enterprise</button>
</div>""", cls="sec-tight")
 , extra="""<script defer>
document.addEventListener('DOMContentLoaded', function(){
  var $=function(s){return document.querySelector(s)};
  var log=$('#mlog'), form=$('#mform'), inp=$('#minput');
  function push(cls,txt,who){var d=document.createElement('div');d.className='m '+cls;d.innerHTML=(who?'<span class="who">'+who+'</span>':'')+txt;log.appendChild(d);log.scrollTop=log.scrollHeight;return d;}
  function brain(q){
    if(window.AIMV_HUMANOID) return window.AIMV_HUMANOID.brain(q).replace(/</g,'&lt;');
    return 'The companion brain is loading — try again in a second.';
  }
  function ask(q){ push('me', q.replace(/</g,'&lt;'));
    setTimeout(function(){ var r=brain(q); push('bot', r, 'Metabox');
      if(window.AIMV_HUMANOID && window.AIMV_HUMANOID.dockOpen()) window.AIMV_HUMANOID.speak(r);
    }, 380+Math.random()*340); }
  form.addEventListener('submit', function(e){ e.preventDefault(); var v=inp.value.trim(); if(!v)return; inp.value=''; ask(v); });
  document.querySelectorAll('.mb-q').forEach(function(b){ b.addEventListener('click', function(){ ask(b.dataset.q); }); });
  (function waitHm(){ if(!window.AIMV_HUMANOID) return setTimeout(waitHm,120);
    window.AIMV_HUMANOID.renderAds(document.getElementById('pg-ads'));
    window.AIMV_HUMANOID.renderSugs(document.getElementById('pg-sugs')); })();
});
</script>
""")

# ============================================================ NEWS
POSTS = [
 ("2026-02-07", "Humanoid companion ships with three faces and five voices", "VERSED'ai now wears a spatial light-ribbon head, a photographed human face or a brushed-metal robot — and speaks as ARIA, ATLAS, NOVA, ORACLE or PIXEL. Click-to-talk arrives with live captions.", ["product","humanoid"]),
 ("2026-01-19", "Clone-yourself pipeline goes fully client-side", "Selfie, voice snippet and birthday now stay in your browser: the forge builds a standalone agent page you can download and keep. Zero uploads.", ["privacy","agents"]),
 ("2025-11-30", "Ready Player Me bodies link to forged agents", "Export a GLB from the RPM creator and it is captured straight into your agent's model card — renderable with visage, Unity or Unreal.", ["rpm","3d"]),
 ("2025-09-12", "BitBucks round-ups land in virtual retail", "Every in-world purchase now rounds up into rewards; store owners can pass them to customers or keep them as margin.", ["economy"]),
 ("2025-06-03", "Certification track adds six labs", "Computer vision, NLP, robotics and autonomous systems labs join the Ai_Education track, each with a graded notebook.", ["education"]),
]
_ph = ['<div class="grid-2 reveal">']
for d, t, b, tags in POSTS:
    chips = ''.join('<span class="chip">%s</span>' % c for c in tags)
    _ph.append('<article class="post"><time>%s</time><h3>%s</h3><p>%s</p><div class="tagline">%s</div></article>' % (d, t, b, chips))
_ph.append('</div>')
posts_html = ''.join(_ph)
P['news.html'] = dict(
 title="Ai Metaverse News & Blog | Ai Metaverse",
 desc="Product notes from the Ai Metaverse: humanoid faces and voices, client-side cloning, Ready Player Me integration, BitBucks rewards and new education labs.",
 body=hero("News & Blog", None, "Ai Metaverse News & Blog", "What shipped,", "lately",
   "Short, honest release notes from the team in Greensboro. The companion bubble will read any of these aloud if you ask.")
 + sec("posts", posts_html)
)

# ============================================================ CONTACT
P['contact.html'] = dict(
 title="Contact Us — Greensboro, NC | Ai Metaverse",
 desc="1007 Yanceyville Street, Greensboro, North Carolina 27405 · 336-805-0229 · weekdays 09:00–17:00. Drop us a line or visit in person.",
 body=hero("Contact", None, "Contact us", "Better yet,", "see us in person",
   "We love our customers, so feel free to visit during normal business hours — computer programming software, metaverse environments and AI agent design.")
 + sec("c", """<div class="contact-grid">
 <aside class="panel reveal" style="display:grid;gap:22px">
   <div class="info-row"><span class="ic">⌂</span><div><b style="display:block;font-family:var(--font-head);font-size:11px;letter-spacing:.18em;text-transform:uppercase;color:var(--dim);margin-bottom:5px">Ai Metaverse</b><p style="color:var(--txt);font-size:14.6px">1007 Yanceyville Street<br>Greensboro, North Carolina 27405<br>United States</p></div></div>
   <div class="info-row"><span class="ic">✆</span><div><b style="display:block;font-family:var(--font-head);font-size:11px;letter-spacing:.18em;text-transform:uppercase;color:var(--dim);margin-bottom:5px">Phone</b><a href="tel:+13368050229" style="color:var(--txt)">336-805-0229</a></div></div>
   <div class="info-row"><span class="ic">◷</span><div><b style="display:block;font-family:var(--font-head);font-size:11px;letter-spacing:.18em;text-transform:uppercase;color:var(--dim);margin-bottom:5px">Hours</b><p style="color:var(--txt);font-size:14.6px">Monday – Friday · 09:00 am – 05:00 pm</p><span class="status" id="open-status" style="margin-top:10px"><span class="d"></span><span id="status-text">Checking…</span></span></div></div>
   <div class="info-row"><span class="ic">✉</span><div><b style="display:block;font-family:var(--font-head);font-size:11px;letter-spacing:.18em;text-transform:uppercase;color:var(--dim);margin-bottom:5px">Email</b><a href="mailto:hello@aimetaverse.cloud" style="color:var(--txt)">hello@aimetaverse.cloud</a></div></div>
 </aside>
 <form class="panel reveal" id="contact-form" style="display:grid;gap:16px" novalidate>
   <h3 class="h-md">Drop us a line!</h3>
   <div class="two"><div class="field"><label for="c-name">Name</label><input id="c-name" type="text" placeholder="Your name" autocomplete="name"></div>
   <div class="field"><label for="c-email">Email <span class="req">*</span></label><input id="c-email" type="email" placeholder="you@example.com" autocomplete="email" required></div></div>
   <div class="field"><label for="c-msg">Message</label><textarea id="c-msg" placeholder="Tell us what you want to build in the metaverse…"></textarea></div>
   <div class="form-msg" id="form-msg" role="status"></div>
   <div class="form-foot"><p class="recap">This site is protected by reCAPTCHA and the Google Privacy Policy and Terms of Service apply.</p>
   <div class="btn-row" style="gap:10px"><button class="btn" type="submit">Send</button><button class="btn btn-ghost" type="reset" id="form-cancel">Cancel</button></div></div>
 </form>
</div>""")
 , extra="""<script defer>
document.addEventListener('DOMContentLoaded', function(){
  var st=document.getElementById('open-status'), txt=document.getElementById('status-text');
  var now=new Date(), day=now.getDay(), mins=now.getHours()*60+now.getMinutes();
  var open = day>=1&&day<=5&&mins>=540&&mins<1020;
  if(open){ txt.textContent='Open now — closes at 05:00 pm'; }
  else { st.classList.add('closed'); txt.textContent = (day>=1&&day<=5) ? 'Closed now — opens 09:00 am' : 'Closed — opens Monday 09:00 am'; }
  var f=document.getElementById('contact-form'), msg=document.getElementById('form-msg');
  f.addEventListener('submit', function(e){ e.preventDefault();
    var em=document.getElementById('c-email');
    if(!em.value || !/^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/.test(em.value)){ msg.className='form-msg show err'; msg.textContent='Email is required — please enter a valid address so we can reply.'; em.focus(); return; }
    msg.className='form-msg show'; msg.textContent='✓ Message sent. Our team in Greensboro replies within one business day (09:00–17:00).'; f.reset(); });
  document.getElementById('form-cancel').addEventListener('click', function(){ msg.className='form-msg'; });
});
</script>""")

# ============================================================ SIGNUP / SIGNIN
P['signup.html'] = dict(
 title="Create Your Free Account — Start Your Free Trial Today | Ai Metaverse",
 desc="Free account: AI tools directory, Craiyon generation, free cloud storage, 100s of metaverse environments. Upgrade for the most advanced models.",
 body=hero("Sign up", None, "Start your free trial today", "Create your", "free account",
   "Clone yourself virtually — selfie, voice snippet and birthday. Then step into the Ai Metaverse with free tools and free cloud storage.")
 + sec("s", """<div class="grid-2">
 <div class="panel reveal"><h3>What's inside free</h3><ul class="prose">
 <li>Free AI tools directory &amp; Craiyon image generation</li><li>Free storage cloud services</li>
 <li>Access to 100s of metaverse environments</li><li>One forged AI agent of yourself</li>
 <li>Humanoid companion with five voice personas</li></ul>
 <p style="margin-top:14px;color:var(--dim);font-size:13px">Upgraded users unlock our most advanced AI models and tools.</p></div>
 <form class="panel reveal" id="su-form" style="display:grid;gap:15px" novalidate>
   <div class="field"><label for="s-name">Name</label><input id="s-name" type="text" placeholder="Your name" autocomplete="name"></div>
   <div class="field"><label for="s-email">Email <span class="req">*</span></label><input id="s-email" type="email" placeholder="you@example.com" autocomplete="email" required></div>
   <div class="field"><label for="s-pass">Password</label><input id="s-pass" type="password" placeholder="At least 8 characters" minlength="8"></div>
   <div class="form-msg" id="su-msg" role="status"></div>
   <button class="btn" type="submit">Create my free account</button>
   <p style="font-size:11.4px;color:var(--dim);text-align:center">Demo form — nothing is transmitted. Already a member? <a href="signin.html" style="color:var(--cyan)">Sign in</a></p>
 </form></div>""")
 , extra="""<script defer>
document.addEventListener('DOMContentLoaded', function(){
  var f=document.getElementById('su-form'), m=document.getElementById('su-msg');
  f.addEventListener('submit', function(e){ e.preventDefault();
    var em=document.getElementById('s-email'), pw=document.getElementById('s-pass');
    if(!em.value || !/^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/.test(em.value)){ m.className='form-msg show err'; m.textContent='Please enter a valid email address.'; return; }
    if(pw.value.length<8){ m.className='form-msg show err'; m.textContent='Password needs at least 8 characters.'; return; }
    m.className='form-msg show'; m.textContent='✓ Account created (demo). Check your inbox to upload your selfie & voice snippet.';
    if(window.AIMV_HUMANOID) window.AIMV_HUMANOID.speak('Welcome aboard! Your free account is ready. Shall we clone you now?');
    f.reset(); });
});
</script>""")
P['signin.html'] = dict(
 title="Sign In — Ai Metaverse",
 desc="Sign in to your Ai Metaverse account to reach your avatar, your forged agents and your cloud storage.",
 body=hero("Sign in", None, "Welcome back", "Sign in to your", "Ai Metaverse",
   "Your avatar, your forged agents and your cloud storage are waiting. (Demo form — nothing is transmitted.)")
 + sec("s", """<form class="panel reveal" id="si-form" style="max-width:520px;margin-inline:auto;display:grid;gap:15px" novalidate>
   <div class="field"><label for="i-email">Email</label><input id="i-email" type="email" placeholder="you@example.com" autocomplete="email" required></div>
   <div class="field"><label for="i-pass">Password</label><input id="i-pass" type="password" placeholder="Your password" autocomplete="current-password"></div>
   <div class="form-msg" id="si-msg" role="status"></div>
   <button class="btn" type="submit">Sign in</button>
   <p style="font-size:12.6px;color:var(--dim);text-align:center">No account yet? <a href="signup.html" style="color:var(--cyan)">Create one free</a> · <a href="contact.html" style="color:var(--muted)">Forgot password</a></p>
 </form>""")
 , extra="""<script defer>
document.addEventListener('DOMContentLoaded', function(){
  var f=document.getElementById('si-form'), m=document.getElementById('si-msg');
  f.addEventListener('submit', function(e){ e.preventDefault();
    var em=document.getElementById('i-email');
    if(!em.value || !/^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/.test(em.value)){ m.className='form-msg show err'; m.textContent='Enter the email you signed up with.'; return; }
    m.className='form-msg show'; m.textContent='✓ Signed in (demo). Opening your avatar dashboard…';
    setTimeout(function(){ location.href='avatar.html'; }, 900); });
});
</script>""")

# ============================================================ PRIVACY / TERMS
P['privacy.html'] = dict(
 title="Privacy Policy — Client-Side by Design | Ai Metaverse",
 desc="What the Ai Metaverse stores, where it stores it (your browser), what never leaves your device (selfie, voice, birthday), cookies, and how to wipe everything.",
 body=hero("Privacy Policy", None, "Legal", "Privacy,", "client-side by design",
   "Short version: the interesting data never leaves your device. Long version below.")
 + sec("p", """<div class="prose reveal" style="max-width:80ch">
<p><b>1 · What we process in your browser.</b> The clone-yourself flow stores a downscaled selfie (≤560 px, JPEG data URL), derived voice metrics (pitch, loudness, pace, character — never the audio itself), your birthday and the personality traits derived from it, your forged agents, companion preferences (face, persona, voice on/off), likes you mention and calendar notes you ask it to remember. All of it lives in <code>localStorage</code> under keys prefixed <code>aimv_</code>.</p>
<p><b>2 · What never leaves your device.</b> The voice recording blob exists only in memory as a temporary object URL for playback; closing the tab destroys it. No biometric template is computed, transmitted or sold. No server ever receives your selfie.</p>
<p><b>3 · Network calls.</b> Google Fonts for typography; the optional Ready Player Me creator iframe (only when you launch it) which then talks to readyplayer.me directly; outbound vendor links you click. The Python/Eel backend, if you run it, stays on localhost.</p>
<p><b>4 · Cookies &amp; consent.</b> The cookie banner stores only your choice (<code>aimv_cookies</code>). We use cookies to analyse traffic and optimise experience; by accepting, your data will be aggregated with all other user data.</p>
<p><b>5 · reCAPTCHA.</b> Contact and signup forms are protected by reCAPTCHA; the Google Privacy Policy and Terms of Service apply to that component.</p>
<p><b>6 · Your controls.</b> “Delete everything” on the clone page wipes every <code>aimv_</code> key instantly. Browser settings can clear site storage at any time. Downloaded agent pages are yours and contain only what you chose to embed.</p>
<p><b>7 · Children.</b> The service is not directed at children under 13; the clone flow requires a birthday that produces an adult age for full features.</p>
<p><b>8 · Changes.</b> Material changes will be posted on the <a href="news.html">News &amp; Blog</a> page with a new date at the top of this policy.</p>
<p style="color:var(--dim)">Last updated: 7 February 2026 · Questions: <a href="contact.html">contact us</a>.</p>
</div>""")
)
P['terms.html'] = dict(
 title="Terms and Conditions | Ai Metaverse",
 desc="The terms for using the Ai Metaverse site, the clone-yourself pipeline, forged agents, the companion, and vendor tools linked from the directory.",
 body=hero("Terms and Conditions", None, "Legal", "The terms,", "in plain words",
   "By using this site you agree to the following. It is shorter than most because most of what happens here happens on your own machine.")
 + sec("t", """<div class="prose reveal" style="max-width:80ch">
<p><b>1 · Service.</b> Ai Metaverse provides a web experience: informational pages, a conversational companion, an in-browser avatar/agent creation pipeline, and links to third-party tools. Availability is on an “as is” basis.</p>
<p><b>2 · Your content.</b> Selfies, voice snippets and agent specs you create remain yours. You grant us no licence because we never receive them. Downloaded agent pages are your artefacts and your responsibility.</p>
<p><b>3 · Acceptable use.</b> Don't forge agents that impersonate real people without consent, don't use generated voices to deceive, don't scrape the directory for spam, don't attempt to break other users' worlds.</p>
<p><b>4 · Third parties.</b> Ready Player Me, MagicStudio, Wordtune, Acrolinx, Brandwatch, Zoom and Google Cardboard are governed by their own terms. We may swap directory partners with notice on the blog.</p>
<p><b>5 · Astrology disclaimer.</b> Personality vectors derived from birthdays are entertainment, not psychometrics or advice (medical, legal, financial).</p>
<p><b>6 · Liability.</b> To the maximum extent permitted by law, we are not liable for losses arising from use of the service, including lost profits or virtual assets.</p>
<p><b>7 · Termination.</b> We may suspend accounts that breach these terms; you may stop using the service and wipe local storage at any time.</p>
<p><b>8 · Governing law.</b> North Carolina, United States — matching our home at 1007 Yanceyville Street, Greensboro.</p>
<p style="color:var(--dim)">Effective: 7 February 2026.</p>
</div>""")
)

# ============================================================ DEVELOPERS
RPM = [
 ("rpm-unity-sdk-core", "C#", "Core functionality for using Ready Player Me avatars in Unity, including avatar loading and creation"),
 ("visage", "TypeScript", "Easily display Ready Player Me avatars and 3D models on the web (web component we recommend)"),
 ("rpm-unreal-sdk", "C++", "Ready Player Me Unreal SDK"),
 ("glTFRuntime", "C++", "Unreal Engine plugin for loading glTF files at runtime"),
 ("animation-library", "—", "Ready Player Me animation library"),
 ("Example-iframe", "HTML", "iframe integration example for readyplayer.me (what our creator modal mirrors)"),
 ("rpm-react-avatar-creator", "TypeScript", "React wrapper for the Ready Player Me Avatar Creator"),
 ("content-validation-schemas", "JSON", "Schemas that validate 3D content for RPM integrations"),
 ("rpm-proxy-server-example", "JavaScript", "Simple proxy server to protect your API keys"),
]
rpm_rows = ''.join(f'<tr><td><code>{n}</code></td><td>{l}</td><td>{d}</td></tr>' for n, l, d in RPM)
P['developers.html'] = dict(
 title="Developers — Agent Spec, Eel Bridge & Ready Player Me SDKs | Ai Metaverse",
 desc="Explore our AI developer & coding repo notes: the agent model card schema, the Python/Eel bridge, Web Speech wiring, and the Ready Player Me SDK map (Unity, Unreal, visage, iframe).",
 body=hero("Developers", None, "Developer &amp; coding repo", "Build on the", "humanoid stack",
   "Everything the companion does is three moving parts — a face renderer, a Web Speech pipeline and a persona brain — plus an optional Python/Eel backend. Here is the map.")
 + sec("arch", shead("Architecture", "GUI + STT + TTS +", "animation engine", "The same split works in the browser or on desktop.") + """
<div class="tbl-wrap reveal"><table class="tbl">
<tr><th>Layer</th><th>Browser (default)</th><th>Python backend (optional)</th></tr>
<tr><td>GUI / face</td><td>Inline SVG + CSS vars (<code>--mouth</code>)</td><td>Eel window hosting the same page</td></tr>
<tr><td>STT</td><td><code>SpeechRecognition</code> w/ interim captions</td><td><code>SpeechRecognition</code> + mic via <code>listen_once()</code></td></tr>
<tr><td>Brain</td><td>Persona KB (<code>AIMV_HUMANOID.brain</code>)</td><td><code>user_said()</code> → local / OpenAI / Ollama</td></tr>
<tr><td>TTS</td><td><code>speechSynthesis</code> + 5 personas</td><td><code>pyttsx3</code> worker queue; browser lip-syncs via <code>avatar_say()</code></td></tr>
<tr><td>Body</td><td>Ready Player Me iframe + GLB URL</td><td>Same URL into Unity / Unreal SDKs</td></tr>
</table></div>
<code class="blk reveal" style="margin-top:20px"><span class="c"># run the backend (desktop voice + optional LLM)</span>
pip install -r py/requirements.txt
python py/main.py                <span class="c"># Chrome app window on :8080</span>
AIMV_LLM=ollama python py/main.py   <span class="c"># local Llama brain</span></code>""")
 + sec("spec", shead("Agent model card", "One JSON spec,", "every surface", "Downloaded with every forged agent; embed it in your own runtime.") + """
<code class="blk reveal">{
  <span class="s">"schema"</span>: "aimetaverse.agent/v1",
  <span class="s">"human"</span>:   { birthday, selfie: {width,height,source,faces}, imageStoredLocally },
  <span class="s">"persona"</span>: { zodiac, element, ruler, chineseZodiac, lifePath,
                traits: {Courage,Wit,Empathy,Ambition,Curiosity,Calm}, greeting },
  <span class="s">"voice"</span>:   { character, fundamentalHz, loudnessRms, pace, storedOnDevice },
  <span class="s">"appearance"</span>: { provider: "Ready Player Me", avatarUrl, avatarId },
  <span class="s">"behaviour"</span>: { role, roleBrief, voiceStyle, temperature },
  <span class="s">"privacy"</span>: { processing: "client-side only", uploads: "none" }
}</code>""")
 + sec("rpm", shead("Ready Player Me", "The SDK map,", "straight from their org", "Where each repo fits in our pipeline.") + """
<div class="tbl-wrap reveal"><table class="tbl"><tr><th>Repository</th><th>Lang</th><th>What it's for here</th></tr>""" + rpm_rows + """</table></div>
<code class="blk reveal" style="margin-top:20px"><span class="c">// render a forged agent's body in any web page</span>
&lt;script type="module" src="https://unpkg.com/@readyplayerme/visage/dist/visage.js"&gt;&lt;/script&gt;
&lt;visage-avatar src="https://models.readyplayer.me/&lt;id&gt;.glb" style="width:100%;height:480px"&gt;&lt;/visage-avatar&gt;

<span class="c">// capture the export from the creator iframe (exactly what our modal listens for)</span>
window.addEventListener(<span class="s">"message"</span>, ev =&gt; {
  const d = typeof ev.data === <span class="s">"string"</span> ? JSON.parse(ev.data) : ev.data;
  if (d?.source === <span class="s">"readyplayerme"</span> &amp;&amp; d.eventName === <span class="s">"v1.avatar.exported"</span>) save(d.data.url);
});</code>""")
 + sec("repo", shead("Certification", "Learn it,", "then ship it", "The education track doubles as the repo tour.") + """
<div class="grid-3 reveal">
 <article class="card"><h3>Notebooks</h3><p>Starter agents, model cards, deployment templates.</p><a class="btn btn-sm btn-ghost" style="margin-top:14px" href="education.html">Ai_Education</a></article>
 <article class="card"><h3>Local brain</h3><p>Swap the persona KB for Ollama/OpenAI with one env var.</p><a class="btn btn-sm btn-ghost" style="margin-top:14px" href="enterprise.html">Enterprise track</a></article>
 <article class="card"><h3>Contribute</h3><p>Found a bug in the companion? The spec schema is versioned — send a patch.</p><a class="btn btn-sm btn-ghost" style="margin-top:14px" href="contact.html">Contact</a></article>
</div>""")
)

# ============================================================ AVATAR DASHBOARD + AGENT LOADER
P['avatar.html'] = dict(scripts=('avatar',),
 title="My Avatar & Agent — Dashboard | Ai Metaverse",
 desc="Your stored clone: selfie, voice profile, birthday personality vector, Ready Player Me body and forged agents. Chat with your agent or wipe everything.",
 body=hero("My Avatar & Agent", None, "Dashboard", "Everything your clone", "is made of",
   "Read straight from this browser's storage. Nothing here exists on a server. If a section is empty, the forge step hasn't run yet.")
 + sec("dash", """<div class="grid-2" id="dash">
  <div class="panel reveal" id="dash-identity"><h3>Identity</h3><p style="color:var(--dim)">Loading…</p></div>
  <div class="panel reveal" id="dash-voice"><h3>Voice profile</h3><p style="color:var(--dim)">Loading…</p></div>
  <div class="panel reveal" id="dash-persona" style="grid-column:1/-1"><h3>Personality vector</h3><p style="color:var(--dim)">Loading…</p></div>
  <div class="panel reveal" id="dash-agent" style="grid-column:1/-1"><h3>Forged agents</h3><p style="color:var(--dim)">Loading…</p></div>
</div>
<div class="chatbox reveal" id="abox" style="margin-top:26px">
  <div class="cbar"><i></i> <span id="abar">agent // offline</span></div>
  <div class="clog" id="alog" aria-live="polite"></div>
  <form id="aform" autocomplete="off"><label for="ainput" style="position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0)">Message your agent</label>
  <input id="ainput" maxlength="240" placeholder="Talk to your agent…" /><button class="btn btn-sm" type="submit">Send</button></form>
</div>
<div class="btn-row reveal" style="margin-top:22px">
  <a class="btn" href="avatar-create.html">Edit my clone</a>
  <button class="btn btn-ghost" id="wipe-all" type="button">Delete everything</button>
</div>""")
 , extra="""<script defer>
document.addEventListener('DOMContentLoaded', function(){
  var $ = function(s){ return document.querySelector(s); };
  (function waitProfile(){ if(!window.AIMV_PROFILE){ return setTimeout(waitProfile, 80); }
  var P = window.AIMV_PROFILE ? window.AIMV_PROFILE.get() : null;
  function row(k,v){ return '<div><span class="k">'+k+'</span><span class="v">'+v+'</span></div>'; }
  if(!P || (!P.image && !P.persona && !P.agent)){
    $('#dash-identity').innerHTML = '<h3>Identity</h3><p style="color:var(--muted)">No clone yet. <a href="avatar-create.html" style="color:var(--cyan)">Forge one in four steps →</a></p>';
    $('#dash-voice').innerHTML = '<h3>Voice profile</h3><p style="color:var(--dim)">—</p>';
    $('#dash-persona').innerHTML = '<h3>Personality vector</h3><p style="color:var(--dim)">—</p>';
    $('#dash-agent').innerHTML = '<h3>Forged agents</h3><p style="color:var(--dim)">—</p>';
    $('#alog').innerHTML = '<div class="m bot">No agent forged yet — I am the house Metabox filling in. Forge your clone and this chat becomes <em>you</em>.</div>';
  } else {
    var im = P.imageMeta || {};
    $('#dash-identity').innerHTML = '<h3>Identity</h3>' + (P.image ? '<img src="'+P.image+'" alt="stored selfie" style="width:150px;height:150px;object-fit:cover;border-radius:18px;border:1px solid var(--stroke-2);margin-bottom:14px">' : '') +
      '<div class="kv">' + row('Name', P.name||'—') + row('Image', im.w? im.w+'×'+im.h+' · '+im.label : '—') + row('RPM body', P.rpm? (P.rpm.id||'linked') : 'not linked') + row('Saved', P.updatedAt? new Date(P.updatedAt).toLocaleString() : '—') + '</div>';
    var v = P.voiceMeta || {};
    $('#dash-voice').innerHTML = '<h3>Voice profile</h3><div class="kv">' + row('Character', v.character||'—') + row('Pitch', v.freq? Math.round(v.freq)+' Hz':'—') + row('Loudness', v.loudness? v.loudness.toFixed(3):'—') + row('Pace', v.pace||'—') + row('Clip', v.duration? v.duration.toFixed(1)+'s (not stored)':'—') + '</div>';
    var pe = P.persona || {};
    var traits = pe.traits || {};
    $('#dash-persona').innerHTML = '<h3>Personality vector</h3><p style="color:var(--muted);font-size:13.6px;margin-bottom:14px">'+(pe.sign? pe.glyph+' '+pe.sign+' · '+pe.element+' · life path '+pe.lifePath+' ('+pe.lifePathTitle+') · Year of the '+pe.animal : '—')+'</p><div class="traits">' +
      Object.keys(traits).map(function(k){ return '<div class="trait"><div class="tl"><span>'+k+'</span><b>'+traits[k]+'</b></div><div class="bar"><span class="fill" style="width:'+traits[k]+'%"></span></div></div>'; }).join('') + '</div>';
    var ags = P.agents || [];
    $('#dash-agent').innerHTML = '<h3>Forged agents</h3>' + (ags.length ? ags.map(function(a){ return '<div class="agent-card" style="margin-bottom:12px"><div class="av">'+(P.image?'<img src="'+P.image+'" alt="">':'<span style="font-size:30px">'+(pe.glyph||'🤖')+'</span>')+'</div><div><h4>'+a.name+'</h4><div class="id">'+a.id+' · '+a.role+'</div><p style="font-size:13px;color:var(--muted);margin-top:6px">'+new Date(a.createdAt).toLocaleString()+'</p></div></div>'; }).join('') : '<p style="color:var(--dim)">None yet.</p>');
    var greet = (pe.greeting || 'Hello — I am your agent.') + ' Ask me about my personality, my voice, or my job.';
    $('#alog').innerHTML = '<div class="m bot"><span class="who">'+(P.agent?P.agent.name:'agent')+'</span>'+greet+'</div>';
    $('#abar').textContent = 'agent // ' + (P.agent ? P.agent.id : 'persona-only');
  }
  var log=$('#alog'), form=$('#aform'), inp=$('#ainput');
  function push(cls,t,who){ var d=document.createElement('div'); d.className='m '+cls; d.innerHTML=(who?'<span class="who">'+who+'</span>':'')+t; log.appendChild(d); log.scrollTop=log.scrollHeight; }
  form.addEventListener('submit', function(e){ e.preventDefault();
    var q=inp.value.trim(); if(!q) return; inp.value=''; push('me', q.replace(/</g,'&lt;'));
    setTimeout(function(){
      var r = window.AIMV_HUMANOID ? window.AIMV_HUMANOID.brain(q) : '…';
      push('bot', r.replace(/</g,'&lt;'), (P&&P.agent)?P.agent.name:'agent');
      if(window.AIMV_HUMANOID) window.AIMV_HUMANOID.speak(r);
    }, 360+Math.random()*300);
  });
  })();
  $('#wipe-all').addEventListener('click', function(){
    if(!confirm('Delete selfie, voice analysis, birthday, agents and companion preferences from this browser?')) return;
    ['aimv_profile_v1','aimv_hm_face','aimv_hm_persona','aimv_hm_voice','aimv_likes','aimv_events'].forEach(function(k){ localStorage.removeItem(k); });
    location.href='avatar-create.html';
  });
});
</script>""")

P['agents/agent.html'] = dict(scripts=('avatar',),
 title="My AI Agent — Live Persona | Ai Metaverse",
 desc="The in-browser home of your forged agent: persona card, traits, voice profile and a live persona chat. Download the standalone version from the forge step.",
 body=hero("My AI Agent", None, "Live persona", "Your agent,", "in the flesh",
   "This page reads your stored profile and runs the persona locally. For a shareable copy, use “Download standalone agent page” on the forge step — that file embeds everything and works offline.")
 + sec("a", """<div class="panel reveal" id="agent-hero"><h3>Loading agent…</h3></div>
<div class="chatbox reveal" id="cbox" style="margin-top:24px">
 <div class="cbar"><i></i> <span id="cbar">persona // local</span></div>
 <div class="clog" id="clog" aria-live="polite"></div>
 <form id="cform" autocomplete="off"><label for="cinput" style="position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0)">Message your agent</label>
 <input id="cinput" maxlength="240" placeholder="Ask your agent…" /><button class="btn btn-sm" type="submit">Send</button></form>
</div>""")
 , extra="""<script defer>
document.addEventListener('DOMContentLoaded', function(){
  var $ = function(s){ return document.querySelector(s); };
  (function waitProfile(){ if(!window.AIMV_PROFILE){ return setTimeout(waitProfile, 80); }
  var P = window.AIMV_PROFILE ? window.AIMV_PROFILE.get() : null;
  var pe = (P&&P.persona)||{}, ag=(P&&P.agent)||null, v=(P&&P.voiceMeta)||{};
  if(!ag){ $('#agent-hero').innerHTML='<h3>No agent forged yet</h3><p style="color:var(--muted)">Run the four-step forge first. <a href="avatar-create/index.html" style="color:var(--cyan)">Open avatar-create →</a></p>'; }
  else {
    $('#agent-hero').innerHTML = '<div class="agent-card"><div class="av">'+(P.image?'<img src="'+P.image+'" alt="">':'<span style="font-size:34px">'+(pe.glyph||'🤖')+'</span>')+'</div>'+
      '<div><h4>'+ag.name+'</h4><div class="id">'+ag.id+' · '+ag.role+' · '+ag.voiceStyle+' · temp '+ag.temperature+'</div>'+
      '<p style="font-size:13.6px;color:var(--muted);margin-top:8px">“'+(pe.greeting||'')+'”</p>'+
      '<div class="tag-row" style="margin-top:12px">'+[pe.sign?pe.sign+' · '+pe.element:'', pe.lifePath?'life path '+pe.lifePath:'', pe.animal?'Year of the '+pe.animal:'', v.character||''].filter(Boolean).map(function(t){return '<span class="chip">'+t+'</span>';}).join('')+'</div>'+
      '<div class="btn-row" style="margin-top:14px"><button class="btn btn-sm" id="greet" type="button">🔊 Hear my greeting</button><a class="btn btn-sm btn-ghost" href="avatar/index.html">Dashboard</a></div></div></div>';
    $('#greet').addEventListener('click', function(){ if(window.AIMV_HUMANOID) window.AIMV_HUMANOID.speak(pe.greeting||('I am '+ag.name+'.')); });
    $('#cbar').textContent = 'persona // ' + ag.id;
  }
  var log=$('#clog'), form=$('#cform'), inp=$('#cinput');
  log.innerHTML = '<div class="m bot">'+((pe.greeting||'Hello — ask me anything.') )+'</div>';
  function push(cls,t,who){ var d=document.createElement('div'); d.className='m '+cls; d.innerHTML=(who?'<span class="who">'+who+'</span>':'')+t; log.appendChild(d); log.scrollTop=log.scrollHeight; }
  form.addEventListener('submit', function(e){ e.preventDefault(); var q=inp.value.trim(); if(!q)return; inp.value=''; push('me', q.replace(/</g,'&lt;'));
    setTimeout(function(){ var r = window.AIMV_HUMANOID? window.AIMV_HUMANOID.brain(q):'…'; push('bot', r.replace(/</g,'&lt;'), ag?ag.name:'agent'); if(window.AIMV_HUMANOID) window.AIMV_HUMANOID.speak(r); }, 360+Math.random()*300); });
  })();
});
</script>""")

# ---------- embedded Avatar Prompt Selector / Prompter (store/prompter.html) ----------
_pr = io.open(os.path.join(ROOT, 'store', 'prompter.html'), encoding='utf-8').read()
PR_CSS = _pr.split('<style>', 1)[1].split('</style>', 1)[0]
_pr_body_all = re.split(r'<body[^>]*>', _pr, 1)[1].rsplit('</body>', 1)[0]
PR_JS = _pr_body_all.rsplit('<script>', 1)[1].rsplit('</script>', 1)[0]
PR_BODY = _pr_body_all.rsplit('<script>', 1)[0]
# "View Repo" button -> real link to the source repository
PR_BODY = re.sub(
    r'<button[^>]*>\s*<i class="fa-brands fa-github[^>]*></i>\s*View Repo\s*</button>',
    '<a href="https://github.com/x1xhlol/system-prompts" target="_blank" rel="noopener noreferrer" '
    'class="bg-zinc-800 hover:bg-zinc-700 text-white px-4 py-1.5 rounded-full text-sm font-medium '
    'transition-colors border border-brand-border inline-flex items-center">'
    '<i class="fa-brands fa-github mr-2"></i>View Repo</a>',
    PR_BODY, count=1)
# Fork -> persist to a local "workspace" library (also fixes the "(In real timer/timr)" toast typos)
PR_JS = PR_JS.replace(
    "showToast('Forked to your local workspace! (In real timer)');",
    "saveFork(document.getElementById('modalTitle').textContent, document.getElementById('modalContent').textContent);")
PR_JS = PR_JS.replace(
    "showToast('Forked to your local workspace! (In real timr)');",
    "var _fp = prompts.find(function(p){return p.id===id;}); if(_fp) saveFork(_fp.title, _fp.content);")
PR_JS = PR_JS.replace(
    "function showToast(message) {",
    "function saveFork(title, text) { try { var key='aimv_prompt_forks'; var arr=JSON.parse(localStorage.getItem(key)||'[]'); if(!arr.some(function(f){return f.title===title;})) arr.push({title:title,text:text,at:Date.now()}); localStorage.setItem(key, JSON.stringify(arr)); showToast('Forked '+title+' to your workspace ('+arr.length+' saved)'); } catch(e){ showToast('Forked to your workspace!'); } }\n\n        function showToast(message) {",
    1)
PR_TW_CFG = ("<script>window.tailwind=window.tailwind||{};</script>"
             "<script>tailwind.config={corePlugins:{preflight:false},theme:{extend:{"
             "fontFamily:{sans:['Inter','sans-serif'],mono:['JetBrains Mono','monospace']},"
             "colors:{brand:{dark:'#09090b',panel:'#18181b',border:'#27272a',accent:'#8b5cf6',accentHover:'#7c3aed',success:'#10b981'}}}}};</script>")
PR_OVERRIDES = ('.pr-embed{position:relative;display:flex;flex-direction:column;height:min(880px,90vh);'
                'border:1px solid #27272a;border-radius:18px;overflow:hidden;background:#09090b;color:#e4e4e7}'
                '.pr-embed header,.pr-embed aside,.pr-embed main{min-width:0}'
                '@media (max-width:900px){.pr-embed{height:min(720px,84vh)}.pr-embed aside{display:none}}')
PROMPTER_SECTION = (
  '<section class="sec-tight" id="prompter"><div class="wrap" style="max-width:1240px">'
  '<div class="sec-head center reveal"><span class="eyebrow"><span class="dot"></span> Prompter \u2014 Guided Prompt Library</span>'
  '<h2 class="h-lg">Select avatar prompts with <span class="grad-text">Prompter</span></h2>'
  '<p class="lead">An IDE-like library of battle-tested system prompts from the open-source community. Filter by AI avatar (Cursor, Devin, Replit, Windsurf, Claude, Manus, Trae, Qwen), get a deterministic suggestion for each, preview the full prompt in a modal, then copy or fork it to your workspace.</p></div>'
  '<style>\n' + scope_css(PR_CSS, '.pr-embed') + '\n' + PR_OVERRIDES + '\n</style>\n'
  '<div class="pr-embed flex flex-col overflow-hidden">' + PR_BODY + '</div>'
  '<div class="callout good reveal" style="margin-top:30px"><b>Put a prompt to work.</b> Fork a system prompt, then forge a companion that runs on it \u2014 '
  '<a href="avatar-create.html" style="color:var(--cyan);text-decoration:underline">clone yourself virtually \u2192</a></div>'
  '</div></section>\n'
)
PROMPTER_EXTRA = '<script>\n' + PR_JS + '\n</script>\n'
PROMPTER_HEAD = ('<script>\n' + WS_TW + '\n</script>\n' + PR_TW_CFG +
  '<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">\n'
  '<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" crossorigin="anonymous" referrerpolicy="no-referrer" />\n')

P['prompter.html'] = dict(
 head=PROMPTER_HEAD,
 extra=PROMPTER_EXTRA,
 title="Avatar Prompt Selector \u2014 Guided System-Prompt Library | Ai Metaverse",
 desc="Browse, filter and fork battle-tested AI system prompts (Cursor, Devin, Replit, Windsurf, Claude, Manus, Trae, Qwen) with a deterministic per-avatar suggestion engine and an IDE-like modal viewer.",
 body=PROMPTER_SECTION
)

# ---------- embedded Virtual Twin Studio (store/vtwin.html) ----------
_vt = io.open(os.path.join(ROOT, 'store', 'vtwin.html'), encoding='utf-8').read()
VT_CSS = _vt.split('<style>', 1)[1].split('</style>', 1)[0]
_vt_body_all = re.split(r'<body[^>]*>', _vt, 1)[1].rsplit('</body>', 1)[0]
VT_JS = _vt_body_all.rsplit('<script>', 1)[1].rsplit('</script>', 1)[0]
VT_BODY = _vt_body_all.rsplit('<script>', 1)[0]
# strip module chrome (shell provides header/footer)
VT_BODY = re.sub(r'<!--\s*Header\s*-->\s*<header[\s\S]*?</header>', '', VT_BODY, count=1)
VT_BODY = re.sub(r'<!--\s*Footer\s*-->\s*<footer[\s\S]*?</footer>', '', VT_BODY, count=1)
# fix upstream broken markup: stray "6" after preview <img>, "</div" missing ">", toast closed with "</"
VT_BODY = VT_BODY.replace('rounded-xl hidden" />\n               6\n', 'rounded-xl hidden" />\n')
VT_BODY = VT_BODY.replace('</button>\n                </div\n            </div>', '</button>\n                </div>\n            </div>')
VT_BODY = VT_BODY.replace('Action successful</span>\n    </', 'Action successful</span>\n    </div>')
# ids + type for the twin chat controls (input/mic had no hooks)
VT_BODY = VT_BODY.replace('<input type="text" placeholder="Speak or type to your twin..."',
                          '<input type="text" id="twinInput" placeholder="Speak or type to your twin..."', 1)
VT_BODY = VT_BODY.replace('<button class="absolute right-3 top-1/2 -translate-y-1/2 w-10 h-10 bg-c25-cyan',
                          '<button type="button" id="twinMic" class="absolute right-3 top-1/2 -translate-y-1/2 w-10 h-10 bg-c25-cyan', 1)
VT_BODY = VT_BODY.replace('<div class="flex-1 bg-slate-900/50 rounded-xl border border-white/5 p-4 overflow-y-auto mb-4">',
                          '<div id="twinChat" class="flex-1 bg-slate-900/50 rounded-xl border border-white/5 p-4 overflow-y-auto mb-4">', 1)
# keep the module grid backdrop inside the embed (body tag is stripped)
VT_BODY = VT_BODY.replace('<main class="flex-1 max-w-7xl mx-auto px-6 py-8 w-full grid lg:grid-cols-12 gap-8">',
                          '<main class="flex-1 max-w-7xl mx-auto px-6 py-8 w-full grid lg:grid-cols-12 gap-8 bg-grid">', 1)
# JS hygiene: innerText -> textContent; track visualizer intervals so Reset can clear them
VT_JS = VT_JS.replace('.innerText', '.textContent')
VT_JS = VT_JS.replace('setInterval(() => {', 'vtVizTimers.push(setInterval(() => {')
VT_JS = VT_JS.replace('}, 100 + Math.random() * 200);', '}, 100 + Math.random() * 200));')
VT_JS = VT_JS.replace('function resetStudio() {',
                      'function resetStudio() {\n            vtVizTimers.forEach(function(t){ clearInterval(t); }); vtVizTimers.length = 0;')
VT_CHAT_JS = """
        var vtVizTimers = [];
        (function wireTwinChat(){
          var log = document.getElementById('twinChat');
          var inp = document.getElementById('twinInput');
          var mic = document.getElementById('twinMic');
          if (!log || !inp) return;
          function esc(s){ return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }
          function push(who, html){
            var row = document.createElement('div');
            row.className = 'flex gap-3 mb-4' + (who === 'me' ? ' flex-row-reverse' : '');
            var av = document.createElement('div');
            av.className = 'w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ' + (who === 'me' ? 'bg-c25-purple/20' : 'bg-c25-cyan/20');
            av.innerHTML = '<i class="fa-solid ' + (who === 'me' ? 'fa-user text-c25-purple' : 'fa-robot text-c25-cyan') + ' text-xs"></i>';
            var bub = document.createElement('div');
            bub.className = 'rounded-2xl p-4 max-w-[85%] ' + (who === 'me' ? 'bg-c25-purple/15 rounded-tr-none' : 'bg-slate-800/50 rounded-tl-none');
            bub.innerHTML = '<p class="text-sm text-slate-200 leading-relaxed">' + html + '</p>';
            row.appendChild(av); row.appendChild(bub);
            log.appendChild(row); log.scrollTop = log.scrollHeight;
          }
          function send(){
            var q = (inp.value || '').trim(); if (!q) return; inp.value = '';
            push('me', esc(q));
            setTimeout(function(){
              var r = (window.AIMV_HUMANOID && window.AIMV_HUMANOID.brain) ? window.AIMV_HUMANOID.brain(q) : '';
              if (!r) r = 'Still synchronizing with your persona — “' + esc(q.slice(0, 60)) + '” noted. Ask me about your twin, your agent, or the Ai Metaverse.';
              push('bot', r);
              if (window.AIMV_HUMANOID && window.AIMV_HUMANOID.speak) { try { window.AIMV_HUMANOID.speak(r); } catch (e) {} }
            }, 380);
          }
          inp.addEventListener('keydown', function(e){ if (e.key === 'Enter') send(); });
          if (mic) mic.addEventListener('click', function(){
            if (window.AIMV_HUMANOID && window.AIMV_HUMANOID.listen) { try { window.AIMV_HUMANOID.listen(); return; } catch (e) {} }
            send();
          });
        })();
"""
VT_JS_FULL = ('(function(){\n' + VT_JS + VT_CHAT_JS +
  '\n        window.handleImageUpload = handleImageUpload;'
  ' window.handleVoiceUpload = handleVoiceUpload;'
  ' window.startRendering = startRendering;'
  ' window.resetStudio = resetStudio;\n})();')
VT_TW_CFG = ("<script>window.tailwind=window.tailwind||{};</script>"
             "<script>tailwind.config={corePlugins:{preflight:false},theme:{extend:{"
             "fontFamily:{sans:['Inter','sans-serif'],display:['Space Grotesk','sans-serif']},"
             "colors:{c25:{dark:'#020617',panel:'#0f172a',cyan:'#22d3ee',purple:'#8b5cf6',gold:'#fbbf24'}},"
             "animation:{scan:'scan 2s linear infinite','pulse-glow':'pulse-glow 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',float:'float 6s ease-in-out infinite'},"
             "keyframes:{scan:{'0%':{top:'0%'},'100%':{top:'100%'}},"
             "'pulse-glow':{'0%, 100%':{boxShadow:'0 0 20px rgba(34, 211, 238, 0.2)'},'50%':{boxShadow:'0 0 40px rgba(34, 211, 238, 0.6)'}},"
             "float:{'0%, 100%':{transform:'translateY(0)'},'50%':{transform:'translateY(-10px)'}}}"
             "}}};</script>")
VT_OVERRIDES = ('.vt-embed{position:relative;border:1px solid rgba(255,255,255,.1);border-radius:18px;overflow:hidden;background:#020617;color:#e2e8f0}'
  '.vt-embed main{min-height:640px;padding-top:26px;padding-bottom:26px}'
  '.vt-embed #toast{left:16px;right:auto;bottom:16px;z-index:160}'
  '.vt-embed #twinChat{min-height:180px}'
  '@keyframes scan{0%{top:0%}100%{top:100%}}'
  '@keyframes pulse-glow{0%,100%{box-shadow:0 0 20px rgba(34,211,238,.2)}50%{box-shadow:0 0 40px rgba(34,211,238,.6)}}'
  '@keyframes float{0%,100%{transform:translateY(0)}50%{transform:translateY(-10px)}}')
VTWIN_SECTION = (
  '<section class="sec-tight" id="twin-studio"><div class="wrap" style="max-width:1240px">'
  '<div class="sec-head center reveal"><span class="eyebrow"><span class="dot"></span> Virtual Twin Studio</span>'
  '<h2 class="h-lg">Create myself as an <span class="grad-text">AI agent</span></h2>'
  '<p class="lead">Sync a spatial image, queue a voice snippet for biometric cloning and define your persona matrix \u2014 then watch the render stage map your mesh, analyze your voice and compile your traits into a live, talking virtual twin. 100% client-side: your image and voice never leave the browser.</p></div>'
  '<style>\n' + scope_css(VT_CSS, '.vt-embed') + '\n' + VT_OVERRIDES + '\n</style>\n'
  '<div class="vt-embed">' + VT_BODY + '</div>'
  '<div class="callout good reveal" style="margin-top:30px"><b>Want the real pipeline?</b> The studio above simulates the render \u2014 '
  '<a href="avatar-create.html" style="color:var(--cyan);text-decoration:underline">Clone Yourself Virtually</a> runs the actual four-step forge: selfie \u2192 voice-pitch analysis \u2192 birth-chart traits \u2192 a downloadable agent of your own.</div>'
  '</div></section>\n'
)
VTWIN_EXTRA = '<script>\n' + VT_JS_FULL + '\n</script>\n'
VTWIN_HEAD = ('<script>\n' + WS_TW + '\n</script>\n' + VT_TW_CFG +
  '<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Space+Grotesk:wght@500;700&display=swap" rel="stylesheet">\n'
  '<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" crossorigin="anonymous" referrerpolicy="no-referrer" />\n')

P['twin-studio.html'] = dict(
 head=VTWIN_HEAD,
 extra=VTWIN_EXTRA,
 title="Virtual Twin Studio \u2014 Create Myself as an AI Agent | Ai Metaverse",
 desc="Upload a spatial image, attach a voice snippet and set your persona matrix, then render your virtual twin: scan-line synthesis, voice visualizer and a talking agent chat \u2014 100% client-side and private.",
 body=VTWIN_SECTION
)

# ---------- embedded Voice & Lip-Sync Studio (store/voicelip.html) ----------
_vl = io.open(os.path.join(ROOT, 'store', 'voicelip.html'), encoding='utf-8').read()
VL_CSS = _vl.split('<style>', 1)[1].split('</style>', 1)[0]
_vl_body_all = re.split(r'<body[^>]*>', _vl, 1)[1].rsplit('</body>', 1)[0]
VL_JS = _vl_body_all.rsplit('<script>', 1)[1].rsplit('</script>', 1)[0]
VL_BODY = _vl_body_all.rsplit('<script>', 1)[0]
# strip module chrome (shell provides header/footer)
VL_BODY = re.sub(r'<!--\s*Header\s*-->\s*<header[\s\S]*?</header>', '', VL_BODY, count=1)
VL_BODY = re.sub(r'<!--\s*Footer\s*-->\s*<footer[\s\S]*?</footer>', '', VL_BODY, count=1)
# keep the module grid backdrop inside the embed (body tag is stripped)
VL_BODY = VL_BODY.replace('<main class="flex-1 max-w-7xl mx-auto px-6 py-8 w-full grid lg:grid-cols-12 gap-8">',
                          '<main class="flex-1 max-w-7xl mx-auto px-6 py-8 w-full grid lg:grid-cols-12 gap-8 bg-grid">', 1)
# counter promises 500 chars — make the textarea keep that promise
VL_BODY = VL_BODY.replace('<textarea id="scriptInput" rows="4" class="',
                          '<textarea id="scriptInput" rows="4" maxlength="500" class="', 1)
# dead "Export MP4" button -> real (simulated) export
VL_BODY = VL_BODY.replace('<button class="text-xs bg-c25-purple hover:bg-purple-500 text-white px-3 py-1.5 rounded-lg transition-colors flex items-center gap-1">',
                          '<button type="button" id="exportBtn" onclick="exportMP4()" class="text-xs bg-c25-purple hover:bg-purple-500 text-white px-3 py-1.5 rounded-lg transition-colors flex items-center gap-1">', 1)
# JS hygiene: innerText -> textContent
VL_JS = VL_JS.replace('.innerText', '.textContent')
# wire the declared-but-unused isRendering flag as a re-entrancy guard
VL_JS = VL_JS.replace('function startRendering() {\n            const script =',
                      'function startRendering() {\n            if (isRendering) return;\n            const script =', 1)
VL_JS = VL_JS.replace('// UI State Changes', 'isRendering = true;\n            // UI State Changes', 1)
VL_JS = VL_JS.replace('showToast("Lip-sync video successfully generated!");',
                      'isRendering = false;\n                showToast("Lip-sync video successfully generated!");', 1)
# track every render timeout + talking interval so Reset can actually stop them
VL_JS = VL_JS.replace('steps.forEach(step => {\n                setTimeout(',
                      'steps.forEach(step => {\n                vlTimers.push(setTimeout(', 1)
VL_JS = VL_JS.replace('}, step.delay);\n            });', '}, step.delay));\n            });', 1)
VL_JS = VL_JS.replace('// Finish Rendering\n            setTimeout(() => {',
                      '// Finish Rendering\n            vlTimers.push(setTimeout(() => {', 1)
VL_JS = VL_JS.replace('}, 8000);', '}, 8000));', 1)
VL_JS = VL_JS.replace('setInterval(() => {', 'vlTimers.push(setInterval(() => {', 1)
VL_JS = VL_JS.replace('}, 150);', '}, 150));', 1)
VL_JS = VL_JS.replace('function resetStudio() {',
                      'function resetStudio() {\n            vlTimers.forEach(function(t){ clearTimeout(t); clearInterval(t); }); vlTimers.length = 0;\n            isRendering = false;', 1)
VL_EXPORT_JS = """
        function exportMP4() {
            if (!avatarDataUrl) { showToast('Nothing to export yet — generate a render first.'); return; }
            var m = /^data:(\\w+)\\/(\\w+);/.exec(avatarDataUrl);
            var ext = (m && m[2]) ? m[2].replace('jpeg', 'jpg') : 'png';
            var a = document.createElement('a');
            a.href = avatarDataUrl;
            a.download = 'c25-lipsync-render.' + ext;
            document.body.appendChild(a); a.click(); document.body.removeChild(a);
            showToast('Render frame exported locally — your media never left the browser.');
        }
"""
VL_JS_FULL = ('(function(){\n        var vlTimers = [];\n' + VL_JS + VL_EXPORT_JS +
  '\n        window.setAvatarType = setAvatarType;'
  ' window.handleAvatarUpload = handleAvatarUpload;'
  ' window.handleVoiceUpload = handleVoiceUpload;'
  ' window.startRendering = startRendering;'
  ' window.resetStudio = resetStudio;'
  ' window.exportMP4 = exportMP4;'
  ' window.showToast = showToast;\n})();')
VL_TW_CFG = ("<script>window.tailwind=window.tailwind||{};</script>"
             "<script>tailwind.config={corePlugins:{preflight:false},theme:{extend:{"
             "fontFamily:{sans:['Inter','sans-serif'],display:['Space Grotesk','sans-serif']},"
             "colors:{c25:{dark:'#020617',panel:'#0f172a',cyan:'#22d3ee',purple:'#8b5cf6',gold:'#fbbf24'}},"
             "animation:{scan:'scan 2s linear infinite','pulse-glow':'pulse-glow 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',wave:'wave 1.2s ease-in-out infinite'},"
             "keyframes:{scan:{'0%':{top:'0%'},'100%':{top:'100%'}},"
             "'pulse-glow':{'0%, 100%':{boxShadow:'0 0 20px rgba(139, 92, 246, 0.2)'},'50%':{boxShadow:'0 0 40px rgba(139, 92, 246, 0.6)'}},"
             "wave:{'0%, 100%':{height:'20%'},'50%':{height:'100%'}}}"
             "}}};</script>")
VL_OVERRIDES = ('.vl-embed{position:relative;border:1px solid rgba(255,255,255,.1);border-radius:18px;overflow:hidden;background:#020617;color:#e2e8f0}'
  '.vl-embed main{min-height:600px;padding-top:26px;padding-bottom:26px}'
  '.vl-embed #toast{left:16px;right:auto;bottom:16px;z-index:160}'
  '@keyframes scan{0%{top:0%}100%{top:100%}}'
  '@keyframes pulse-glow{0%,100%{box-shadow:0 0 20px rgba(139,92,246,.2)}50%{box-shadow:0 0 40px rgba(139,92,246,.6)}}'
  '@keyframes wave{0%,100%{height:20%}50%{height:100%}}')
VOICE_SECTION = (
  '<section class="sec-tight" id="voice-lipsync"><div class="wrap" style="max-width:1240px">'
  '<div class="sec-head center reveal"><span class="eyebrow"><span class="dot"></span> Voice &amp; Lip-Sync Studio</span>'
  '<h2 class="h-lg">Upload your voice, <span class="grad-text">attach it to your avatar</span></h2>'
  '<p class="lead">Pick a still photo or a video template, queue a clean voice snippet for biometric cloning (ElevenLabs / HeyGen-style) and write up to 500 characters of multi-lingual script \u2014 then watch the render stage extract pitch and cadence, map 68 facial landmarks and align phonemes frame-by-frame into a talking preview with a live audio visualizer. 100% client-side: your audio and images never reach a server.</p></div>'
  '<style>\n' + scope_css(VL_CSS, '.vl-embed') + '\n' + VL_OVERRIDES + '\n</style>\n'
  '<div class="vl-embed">' + VL_BODY + '</div>'
  '<div class="callout good reveal" style="margin-top:30px"><b>Build the whole twin.</b> Pair this voice engine with the '
  '<a href="twin-studio.html" style="color:var(--cyan);text-decoration:underline">Virtual Twin Studio</a> (persona matrix + talking agent chat), or run the real four-step forge in '
  '<a href="avatar-create.html" style="color:var(--cyan);text-decoration:underline">Clone Yourself Virtually</a>.</div>'
  '</div></section>\n'
)
VOICE_EXTRA = '<script>\n' + VL_JS_FULL + '\n</script>\n'
VOICE_HEAD = ('<script>\n' + WS_TW + '\n</script>\n' + VL_TW_CFG +
  '<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Space+Grotesk:wght@500;700&display=swap" rel="stylesheet">\n'
  '<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" crossorigin="anonymous" referrerpolicy="no-referrer" />\n')

P['voice-lipsync.html'] = dict(
 head=VOICE_HEAD,
 extra=VOICE_EXTRA,
 title="Voice & Lip-Sync Studio \u2014 Upload Your Voice to Attach to Avatar | Ai Metaverse",
 desc="Attach your voice to your avatar: still-photo or video source, biometric voice-cloning sample, 500-char multi-lingual script, cinematic scan-line render and a talking lip-sync preview with audio visualizer \u2014 100% client-side and private.",
 body=VOICE_SECTION
)

# ============================================================ write files
for name, d in P.items():
    html = head(d['title'], d['desc']) + dirform(d['body'], name) + foot(dirform(d.get('extra', ''), name), d.get('scripts', ()))
    if d.get('head'):
        html = html.replace('</head>', d['head'] + '</head>', 1)
    emit(name, html)
print('generated', len(P), 'pages x2 (flat + folder index)')
