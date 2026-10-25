/* ============================================================
   Ai Metaverse — HUMANOID COMPANION  ("your buddy on the net")
   A conversational face that lives on every page:
     · three faces   : spatial (light-ribbon head) · real (photo) · robot
     · five personas : ARIA · ATLAS · NOVA · ORACLE · PIXEL (voice + accent)
     · CLICK TO TALK : browser STT with live captions, then a spoken reply
     · companion kit : jokes, trivia, news, hugs, schedule memory,
                       and it learns what you like (stored locally)
   Everything is client-side. No uploads. No build step.
   ============================================================ */
(function () {
  "use strict";
  var $ = function (s, c) { return (c || document).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || document).querySelectorAll(s)); };
  var reduceMotion = !!(window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches);

  var LS_FACE = 'aimv_hm_face', LS_PERS = 'aimv_hm_persona', LS_VOICE = 'aimv_hm_voice',
      LS_LIKES = 'aimv_likes', LS_EVENTS = 'aimv_events', SS_GREET = 'aimv_hm_greeted';

  /* ==========================================================
     VOICE PERSONAS
     ========================================================== */
  var PERSONAS = {
    aria:   { label: 'ARIA',   desc: 'warm & human',      pitch: 1.12, rate: 1.00, c1: '#00f0ff', c2: '#a855f7', voice: /zira|samantha|aria|jenny|kate|serena|female/i },
    atlas:  { label: 'ATLAS',  desc: 'deep & grounded',   pitch: 0.72, rate: 0.90, c1: '#5b8cff', c2: '#00f0ff', voice: /daniel|david|fred|alex|george|male/i },
    nova:   { label: 'NOVA',   desc: 'bright & upbeat',   pitch: 1.34, rate: 1.12, c1: '#ff2fb9', c2: '#ffc857', voice: /zira|samantha|aria|victoria|female/i },
    oracle: { label: 'ORACLE', desc: 'measured & wise',   pitch: 0.95, rate: 0.80, c1: '#9dff3d', c2: '#00f0ff', voice: /daniel|fred|olive|male/i },
    pixel:  { label: 'PIXEL',  desc: 'playful robot',     pitch: 1.50, rate: 1.16, c1: '#ffc857', c2: '#ff2fb9', voice: /karen|moira|tessa|fiona|female/i }
  };

  var state = {
    face: 'spatial',
    persona: 'aria',
    voiceOn: true,
    open: false,
    st: 'idle',              /* idle | listening | thinking | speaking */
    interacted: 0,
    mouthRaf: null,
    blinkTimer: null,
    idleTimer: null,
    reco: null,
    recoLive: false
  };
  function lsGet(k, d) { try { var v = localStorage.getItem(k); return v === null ? d : v; } catch (e) { return d; } }
  function lsSet(k, v) { try { localStorage.setItem(k, v); } catch (e) {} }
  function lsJson(k, d) { try { var v = localStorage.getItem(k); return v ? JSON.parse(v) : d; } catch (e) { return d; } }
  function lsSave(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) {} }

  state.face = lsGet(LS_FACE, 'real');   /* the photoreal portrait in the orb is the signature look */
  state.persona = PERSONAS[lsGet(LS_PERS, '')] ? lsGet(LS_PERS, 'aria') : 'aria';
  state.voiceOn = lsGet(LS_VOICE, '1') !== '0';
  if (['spatial', 'real', 'robot'].indexOf(state.face) === -1) state.face = 'real';

  /* ==========================================================
     COMPANION BRAIN
     ========================================================== */
  var JOKES = [
    'Why did the neural network break up with the chatbot? Too many layers of commitment.',
    'I told my avatar a joke about the metaverse. It is still rendering the punchline.',
    'Why do programmers prefer dark mode? Because light attracts bugs — and my visor attracts photons.',
    'My friend asked my AI agent to be more spontaneous. It scheduled that for Tuesday.',
    'What is a robot\'s favourite music genre? Heavy metal — obviously.'
  ];
  var TRIVIA = [
    'The word "avatar" comes from Sanskrit avatāra — a deity\'s descent into the mortal world.',
    'Craiyon began life in 2022 as "DALL·E mini", built by Boris Dayma, and has been generating royalty-free art here ever since.',
    'The Ai Metaverse directory lists over 100 named virtual worlds, from Tivoli Cloud to Somnium Space.',
    'Google Cardboard started as a 20% project in 2014 — a VR headset you fold from cardboard.',
    'Your life-path number comes from adding every digit of your birthday until one remains. Masters 11 and 22 are kept whole.'
  ];
  var NEWS = [
    'Late-breaking: the Ai-Labs sandbox just added 40 new open models for certification students.',
    'Headlines: virtual retail storefronts built with digital twins grew again this quarter in the Ai Metaverse economy.',
    'Newsflash: BitBucks round-up rewards now apply to virtual fashion purchases in-world.',
    'Bulletin: the Metabox persona engine learned three new tricks — jokes, trivia and hugs. You are looking at one of them.'
  ];
  var IDLE = [
    'Psst — tap CLICK TO TALK and tell me what you are building today.',
    'Did you know you can forge an AI agent of yourself in four steps? Selfie, voice, birthday, done.',
    'I keep your likes and your schedule in this browser only. Old-school buddy, new-school privacy.',
    'Want a joke? A trivia nugget? A hug delivered with feeling? I do all three.',
    'The metaverse is 100 worlds deep. I have opinions about at least 97 of them.'
  ];
  var KB = [
    { k: ['hello', 'hi ', 'hey', 'yo ', 'good morning', 'good evening'], r: 'Hey, I am so glad you are here. I am your humanoid buddy in the Ai Metaverse — I talk, I listen, I joke, I browse worlds with you, and I remember what you love. What shall we do first?' },
    { k: ['who are you', 'what are you', 'your name', 'introduce'], r: 'I am VERSED\'ai — a humanoid companion for the Ai Metaverse. Think of me as the friend who surfs the metaverse with you: I can talk, listen, joke, browse, search, remember your schedule and deliver messages with real feeling.' },
    { k: ['avatar', 'clone', 'selfie', 'birth chart', 'horoscope', 'birthday'], r: 'To clone yourself virtually: upload a selfie, attach a voice snippet, and enter your birthday so I can mimic your horoscope traits. Four steps and you have an agent of your own — open Clone Yourself from the menu.' },
    { k: ['craiyon', 'art', 'image', 'draw', 'paint', 'royalty'], r: 'Craiyon turns any text prompt into royalty-free images. Describe the subject, the style and the light, then re-roll until it sings. It lives inside Ai-Labs.' },
    { k: ['world', 'environment', 'explore', 'vrchat', 'somnium', 'planet', 'mars', 'where can i go'], r: 'I can take you to Tivoli Cloud, Somnium Space, VRChat, Mona, Spatial and a hundred more — including a virtual trip to Mars. Pick one from the Worlds page and I will narrate the journey.' },
    { k: ['free', 'tool', 'tools', 'directory', 'price', 'cost'], r: 'The Free AI Tools Directory covers writing, images, video, music and social — plus free cloud storage for members. Upgraded accounts unlock our most advanced models.' },
    { k: ['enterprise', 'business', 'agent', 'digital twin', 'crm', 'telemark'], r: 'For enterprise we deploy purpose-driven custom agent models, digital twins of offices and storefronts, a free AI CRM, AI telemarketers and biometric payments with MyBUY\'o.' },
    { k: ['learn', 'education', 'certif', 'course', 'programming', 'code', 'python', 'study'], r: 'Ai Education teaches AI programming and development with certification — neural networks, deep learning, computer vision, NLP, robotics and autonomous systems.' },
    { k: ['video', 'youtube', 'face swap', 'reface', 'social'], r: 'You can create YouTube and social videos with AI, including Re-Face face swaps — script, render, caption and publish from one workspace.' },
    { k: ['shop', 'store', 'fashion', 'decor', 'bitbuck', 'reward', 'buy'], r: 'Millions of virtual fashion, home décor and clothing items are in-world. Set up a virtual retail store, pay with biometrics, and earn BitBucks round-up rewards.' },
    { k: ['music', 'song', 'lyric', 'record', 'concert'], r: 'Ai Records writes and produces original lyrics and tracks — then you can host a virtual concert in your own environment and invite the whole community.' },
    { k: ['joke', 'funny', 'make me laugh'], r: function () { return JOKES[Math.floor(Math.random() * JOKES.length)]; } },
    { k: ['trivia', 'fact', 'did you know', 'tell me something'], r: function () { return TRIVIA[Math.floor(Math.random() * TRIVIA.length)]; } },
    { k: ['news', 'headline', 'what\'s new', 'whats new'], r: function () { return NEWS[Math.floor(Math.random() * NEWS.length)]; } },
    { k: ['hug', 'kiss', 'love you', 'miss you', 'cheer me up'], r: 'Coming in for a hug… consider it delivered in person, with feeling. I can also pass one on to a friend on your behalf — I will say it in your agent\'s voice.' },
    { k: ['schedule', 'calendar', 'appointment', 'remind', 'remember'], r: 'I keep a tiny calendar in this browser. Say "remember <thing> on <day>" and I will hold it for you. Ask "what\'s on my schedule?" any time.' },
    { k: ['voice', 'persona', 'sound like', 'change your voice'], r: 'I speak in five personas — ARIA is warm and human, ATLAS deep and grounded, NOVA bright and upbeat, ORACLE measured and wise, PIXEL a playful robot. Tap a persona chip and hear the difference.' },
    { k: ['face', 'look like', 'robot', 'real', 'spatial', 'appearance'], r: 'I wear three faces. Spatial is my light-ribbon head, Real is a photographed human face, Robot is brushed metal with a visor. Switch any time — I am the same buddy underneath.' },
    { k: ['hour', 'open', 'address', 'where are you', 'contact', 'phone'], r: 'The humans behind me are at 1007 Yanceyville Street, Greensboro, North Carolina — weekdays nine to five, phone 336-805-0229. I, however, never sleep.' },
    { k: ['thank', 'thanks', 'cheers'], r: 'Any time, friend. That is what buddies are for.' },
    { k: ['bye', 'goodbye', 'see you', 'later'], r: 'See you soon. I will be right here, blinking politely at the corner of your screen.' }
  ];

  function brain(text) {
    var s = String(text || '').toLowerCase();
    /* timed reminders first — they are not calendar notes */
    var rem0 = parseReminder(s);
    if (rem0) {
      var rl0 = reminders(); rl0.push({ t: rem0.t, due: rem0.due, done: false, at: new Date().toISOString() });
      saveReminders(rl0.slice(-30));
      setTimeout(checkReminders, Math.max(0, rem0.due - Date.now()) + 250);
      return 'Reminder pinned: "' + rem0.t + '" at ' + new Date(rem0.due).toLocaleString() +
             '. I will speak it the moment it is due, on any page you have open.';
    }
    /* schedule memory */
    var m = s.match(/(?:remember|add to my schedule)\s+(.{3,90})/);
    if (m) {
      var ev = lsJson(LS_EVENTS, []);
      ev.push({ t: m[1].trim(), at: new Date().toISOString() });
      lsSave(LS_EVENTS, ev.slice(-20));
      return 'Noted and pinned to your calendar: "' + m[1].trim() + '". I am never late for an appointment.';
    }
    if (/what'?s on my (schedule|calendar)|my (appointments|events)/.test(s)) {
      var list = lsJson(LS_EVENTS, []);
      if (!list.length) return 'Your calendar is blissfully empty. Say "remember <thing>" and I will hold a slot.';
      return 'On your calendar: ' + list.slice(-5).map(function (e) { return '"' + e.t + '"'; }).join(', ') + '.';
    }
    if (/list my reminders|my reminders|show reminders/.test(s)) {
      var rr = reminders().filter(function (x) { return !x.done; });
      if (!rr.length) return 'No pending reminders. Say "remind me to <thing> in 10 minutes" and I will hold it.';
      return 'Pending reminders: ' + rr.map(function (x) { return '"' + x.t + '" at ' + new Date(x.due).toLocaleTimeString(); }).join(' · ') + '.';
    }
    if (/clear my reminders|cancel reminders/.test(s)) { saveReminders([]); return 'All reminders cleared. Your calendar breathes again.'; }
    var tk = s.match(/add task (.+)/);
    if (tk) { var tl = tasks(); tl.push({ t: tk[1].trim(), done: false }); saveTasks(tl.slice(-30)); return 'Task added: "' + tk[1].trim() + '". I will keep it on your agent board.'; }
    var ct = s.match(/(?:complete|finish|done with) task (.+)/);
    if (ct) {
      var tl2 = tasks(), hit = null;
      tl2.forEach(function (x) { if (!x.done && x.t.toLowerCase().indexOf(ct[1].trim().slice(0, 12)) !== -1) { x.done = true; hit = x.t; } });
      saveTasks(tl2);
      return hit ? 'Nice — "' + hit + '" marked done. Momentum is a feature.' : 'I could not find an open task matching that. Say "list tasks" to see the board.';
    }
    if (/list tasks|my tasks|task board/.test(s)) {
      var tt = tasks().filter(function (x) { return !x.done; });
      if (!tt.length) return 'Task board is empty. "Add task <thing>" and I will track it.';
      return 'Open tasks: ' + tt.map(function (x, i) { return (i + 1) + '. ' + x.t; }).join(' · ') + '.';
    }
    var dv = s.match(/deliver (?:a )?message to ([^:]{2,40}):(.{2,200})/);
    if (dv) {
      var sl = sentMsgs(); sl.push({ to: dv[1].trim(), text: dv[2].trim(), at: new Date().toISOString(), voice: PERSONAS[state.persona].label });
      lsSave(LS_SENT, sl.slice(-20));
      return 'On my way — I will deliver "' + dv[2].trim() + '" to ' + dv[1].trim() +
             ' myself, in my ' + PERSONAS[state.persona].label + ' voice, with exactly the right amount of feeling.';
    }
    if (/delivered messages|my messages|sent messages/.test(s)) {
      var ss = sentMsgs();
      if (!ss.length) return 'No deliveries yet. Try "deliver a message to Ada: the build is live".';
      return 'Deliveries: ' + ss.slice(-4).map(function (x) { return 'to ' + x.to + ' — "' + x.text + '" (' + x.voice + ')'; }).join(' · ') + '.';
    }
    /* learn likes */
    var lk = s.match(/\bi (?:really )?(?:like|love|enjoy)\s+([a-z0-9 ,'-]{3,40})/);
    if (lk) {
      var likes = lsJson(LS_LIKES, []);
      var topic = lk[1].trim().replace(/[.!,]$/, '');
      if (topic && likes.indexOf(topic) === -1) { likes.push(topic); lsSave(LS_LIKES, likes.slice(-8)); }
      return 'Got it — you love ' + topic + '. I will keep an eye out for worlds, tools and news that match, and bring them to you.';
    }
    for (var i = 0; i < KB.length; i++) {
      for (var j = 0; j < KB[i].k.length; j++) {
        if (s.indexOf(KB[i].k[j]) !== -1) {
          var r = KB[i].r;
          return typeof r === 'function' ? r() : r;
        }
      }
    }
    if (window.AIMV_BRAIN && typeof window.AIMV_BRAIN === 'function') {
      try { return window.AIMV_BRAIN(text); } catch (e) {}
    }
    var likes2 = lsJson(LS_LIKES, []);
    if (likes2.length && Math.random() < .35) {
      return 'Interesting one. It reminds me of how much you like ' + likes2[likes2.length - 1] +
             ' — want me to find a metaverse world or an AI tool built around that?';
    }
    return 'I hear you. I can clone your avatar, generate royalty-free art, open a hundred virtual worlds, tell jokes and trivia, keep your schedule, or just keep you company. Which sounds good?';
  }

  /* ==========================================================
     FACES
     ========================================================== */
  function spatialFace() {
    var ribbons = '';
    var g = '';
    var pairs = [['#00f0ff', '#7c5cff'], ['#7c5cff', '#ff2fb9'], ['#5b8cff', '#a855f7'], ['#00c2d4', '#5b8cff'], ['#a855f7', '#ff7ad9']];
    for (var i = 0; i < 5; i++) {
      g += '<linearGradient id="hmrg' + i + '" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="' + pairs[i][0] + '"/><stop offset="1" stop-color="' + pairs[i][1] + '"/></linearGradient>';
    }
    for (var n = 0; n < 16; n++) {
      var t = n / 15;
      var x0 = 96 + t * 30, y0 = 14 + t * 7;
      var c1x = 40 + t * 26, c1y = 34 + t * 24;
      var c2x = 52 + t * 26, c2y = 104 + t * 26;
      var x3 = 96 + t * 34, y3 = 168 + t * 30;
      var w = (24 - t * 13).toFixed(1);
      var op = (0.8 - t * 0.42).toFixed(2);
      ribbons += '<path class="hm-ribbon" style="animation-delay:' + (-n * .37).toFixed(2) + 's" d="M' + x0.toFixed(1) + ' ' + y0.toFixed(1) +
        ' C ' + c1x.toFixed(1) + ' ' + c1y.toFixed(1) + ', ' + (c1x + 10).toFixed(1) + ' ' + (c1y + 36).toFixed(1) + ', ' + c2x.toFixed(1) + ' ' + c2y.toFixed(1) +
        ' S ' + (x3 - 18).toFixed(1) + ' ' + (y3 - 28).toFixed(1) + ', ' + x3.toFixed(1) + ' ' + y3.toFixed(1) +
        '" fill="none" stroke="url(#hmrg' + (n % 5) + ')" stroke-width="' + w + '" stroke-linecap="round" opacity="' + op + '" filter="url(#hmBlur)"/>';
    }
    var sparks = '';
    for (var s2 = 0; s2 < 9; s2++) {
      sparks += '<circle cx="' + (40 + s2 * 15 % 130) + '" cy="' + (26 + (s2 * 37) % 160) + '" r="' + (0.8 + (s2 % 3) * 0.5) + '" fill="#bff7ff" opacity="' + (0.25 + (s2 % 4) * 0.14).toFixed(2) + '"/>';
    }
    return '<span class="floatwrap"><svg viewBox="0 0 200 220" aria-label="VERSED ai spatial light-ribbon head" role="img"><defs>' + g +
      '<filter id="hmBlur" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="2.1"/></filter>' +
      '<radialGradient id="hmGlow" cx="50%" cy="42%" r="55%"><stop offset="0" stop-color="#7c5cff" stop-opacity=".5"/><stop offset="1" stop-color="#7c5cff" stop-opacity="0"/></radialGradient>' +
      '</defs>' +
      '<ellipse cx="104" cy="104" rx="86" ry="92" fill="url(#hmGlow)"/>' +
      '<path d="M120 16 C 74 22, 50 60, 54 102 C 57 134, 72 156, 88 172 L 98 212 L 152 212 L 140 166 C 160 148, 170 116, 164 82 C 158 46, 144 22, 120 16 Z" fill="rgba(9,5,26,.62)"/>' +
      ribbons +
      '<ellipse class="hm-eye-glow" cx="126" cy="94" rx="13" ry="3.2" fill="#cffaff" opacity=".85" filter="url(#hmBlur)"/>' +
      '<rect class="hm-mouth-light" x="118" y="136" width="27" height="7" rx="3.5" fill="url(#hmrg1)" opacity=".9" filter="url(#hmBlur)"/>' +
      sparks + '</svg></span>';
  }

  function robotFace() {
    return '<span class="floatwrap"><svg viewBox="0 0 200 220" aria-label="VERSED ai robot head" role="img"><defs>' +
      '<linearGradient id="hmMetal" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#3b4668"/><stop offset=".45" stop-color="#141a30"/><stop offset="1" stop-color="#2a3350"/></linearGradient>' +
      '<linearGradient id="hmVisor" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#00f0ff"/><stop offset=".5" stop-color="#7c5cff"/><stop offset="1" stop-color="#ff2fb9"/></linearGradient>' +
      '<radialGradient id="hmRGlow" cx="50%" cy="45%" r="55%"><stop offset="0" stop-color="#00f0ff" stop-opacity=".34"/><stop offset="1" stop-color="#00f0ff" stop-opacity="0"/></radialGradient>' +
      '</defs>' +
      '<ellipse cx="100" cy="108" rx="88" ry="94" fill="url(#hmRGlow)"/>' +
      '<line x1="100" y1="30" x2="100" y2="14" stroke="#8fa0c9" stroke-width="3" stroke-linecap="round"/>' +
      '<circle class="hm-antenna" cx="100" cy="11" r="5" fill="#00f0ff"/>' +
      '<rect x="38" y="30" width="124" height="132" rx="30" fill="url(#hmMetal)" stroke="#5c6b96" stroke-width="2"/>' +
      '<path d="M52 44h96M52 150h96" stroke="#0d1226" stroke-width="2" opacity=".7"/>' +
      '<rect x="54" y="76" width="92" height="36" rx="18" fill="#05070f" stroke="#31406b" stroke-width="1.6"/>' +
      '<rect class="hm-visor-eye" x="66" y="86" width="24" height="15" rx="7.5" fill="url(#hmVisor)"/>' +
      '<rect class="hm-visor-eye" x="110" y="86" width="24" height="15" rx="7.5" fill="url(#hmVisor)"/>' +
      '<g class="hm-jaw">' +
        '<rect x="72" y="126" width="56" height="4.6" rx="2.3" fill="#0a0f1f" stroke="url(#hmVisor)" stroke-width="1.1"/>' +
        '<rect x="78" y="134" width="44" height="4.6" rx="2.3" fill="#0a0f1f" stroke="url(#hmVisor)" stroke-width="1.1"/>' +
        '<rect x="84" y="142" width="32" height="4.6" rx="2.3" fill="#0a0f1f" stroke="url(#hmVisor)" stroke-width="1.1"/>' +
      '</g>' +
      '<circle cx="34" cy="96" r="9" fill="#141a30" stroke="#5c6b96" stroke-width="2"/>' +
      '<circle cx="166" cy="96" r="9" fill="#141a30" stroke="#5c6b96" stroke-width="2"/>' +
      '<circle cx="34" cy="96" r="3" fill="#ff2fb9"/><circle cx="166" cy="96" r="3" fill="#ff2fb9"/>' +
      '<path d="M70 162h60l10 26H60z" fill="#10162b" stroke="#5c6b96" stroke-width="2"/>' +
      '<path d="M40 196c10-14 30-20 60-20s50 6 60 20" fill="none" stroke="#5c6b96" stroke-width="3" stroke-linecap="round"/>' +
      '</svg></span>';
  }

  function assetBase() {
    var sc = document.querySelector('script[src$="humanoid.js"]');
    if (sc && sc.src) return sc.src.replace(/[^/]*$/, '');
    return 'assets/';
  }
  function realFaceSrc() {
    return (window.AIMV_FACES && window.AIMV_FACES.real) || (assetBase() + 'face-real.jpg');
  }
  function realFace() {
    return '<span class="hm-photo">' +
      '<img src="' + realFaceSrc() + '" alt="VERSED ai — photoreal human companion face" />' +
      '<span class="lid l"></span><span class="lid r"></span>' +
      '<span class="mouthglow"></span>' +
      '<span class="sheen"></span>' +
      '</span>';
  }

  function faceMarkup() {
    if (state.face === 'real') return realFace();
    if (state.face === 'robot') return robotFace();
    return spatialFace();
  }

  /* ==========================================================
     DOCK + LAUNCHER
     ========================================================== */
  var el = {};

  function build() {
    if ($('#hm-dock')) return;
    var launch = document.createElement('button');
    launch.className = 'hm-launch';
    launch.id = 'hm-launch';
    launch.type = 'button';
    launch.setAttribute('aria-label', 'Talk to VERSED\'ai, your humanoid companion');
    launch.innerHTML = '<span class="mini">' + faceMarkup() + '</span><span class="hm-flag" id="hm-flag">1</span>';
    document.body.appendChild(launch);

    var dock = document.createElement('div');
    dock.className = 'hm-dock';
    dock.id = 'hm-dock';
    dock.setAttribute('role', 'dialog');
    dock.setAttribute('aria-label', 'VERSED\'ai humanoid companion');
    dock.innerHTML =
      '<div class="hm-head">' +
        '<div class="who">' +
          '<span class="dotface" id="hm-dotface"></span>' +
          '<div><b>VERSED&rsquo;ai <span style="color:var(--hm-accent)" id="hm-persname">ARIA</span></b>' +
          '<span class="st" id="hm-status"><i></i><span id="hm-statustext">Online</span></span></div>' +
        '</div>' +
        '<button class="hm-close" id="hm-close" aria-label="Close companion">✕</button>' +
      '</div>' +
      '<div class="hm-body">' +
        '<div class="hm-stage" id="hm-stage"><canvas class="orb-canvas" id="hm-orb"></canvas><span class="hm-orb-ring"></span><span class="hm-orb-ring r2"></span><span class="aura"></span><div class="hm-face" id="hm-face"></div></div>' +
        '<div class="hm-caption idle" id="hm-caption">Click to talk — or type below. I listen, I answer, I remember.</div>' +
        '<div class="hm-talkrow">' +
          '<button class="hm-talk" id="hm-talk" type="button">' + micSvg() + '<span id="hm-talklabel">Click to talk</span></button>' +
          '<button class="hm-mini-btn" id="hm-joke" type="button" title="Tell me a joke">😄</button>' +
          '<button class="hm-mini-btn" id="hm-trivia" type="button" title="Trivia nugget">🧠</button>' +
          '<button class="hm-mini-btn" id="hm-hug" type="button" title="Send a hug">💜</button>' +
        '</div>' +
        '<div class="hm-sugs" id="hm-sugs" aria-label="Suggested prompts"></div>' +
        '<div class="hm-agentik" id="hm-agentik" role="group" aria-label="Agentic actions"></div>' +
        '<div class="hm-personas" id="hm-personas" role="group" aria-label="Voice personas"></div>' +
        '<div class="hm-facerow" id="hm-facerow" role="group" aria-label="Companion face">' +
          '<button class="hm-facebtn" data-face="spatial" type="button">' + waveSvg() + 'Spatial</button>' +
          '<button class="hm-facebtn" data-face="real" type="button">' + userSvg() + 'Real</button>' +
          '<button class="hm-facebtn" data-face="robot" type="button">' + botSvg() + 'Robot</button>' +
          '<button class="hm-voicebtn on" id="hm-voicebtn" type="button" aria-pressed="true">' + spkSvg() + '<span>voice</span></button>' +
        '</div>' +
        '<div class="hm-log" id="hm-log" aria-live="polite"></div>' +
        '<form class="hm-inputrow" id="hm-form" autocomplete="off">' +
          '<label for="hm-input" style="position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0)">Message VERSED\'ai</label>' +
          '<input id="hm-input" maxlength="240" placeholder="Type a message to your buddy…" />' +
          '<button type="submit">Send</button>' +
        '</form>' +
        '<div class="hm-cards" id="hm-cards">' +
          '<button class="hm-card" data-act="surf" type="button"><b>🌊 Surfs with you</b>Pick a world and I come along, narrating as we go.</button>' +
          '<button class="hm-card" data-act="learn" type="button"><b>🧠 Learns what you love</b>Tell me your interests; I surface worlds &amp; tools you missed.</button>' +
          '<button class="hm-card" data-act="deliver" type="button"><b>💌 Delivers messages</b>I will say it in your agent\'s voice — hugs included.</button>' +
          '<button class="hm-card" data-act="schedule" type="button"><b> Keeps your schedule</b>"Remember…" and it is pinned. Never late.</button>' +
          '<button class="hm-card" data-act="news" type="button"><b>🗞️ Late-breaking news</b>Headlines from across the Ai Metaverse.</button>' +
          '<button class="hm-card" data-act="fun" type="button"><b>😄 Smiles all day</b>Jokes, trivia and your daily horoscope trait.</button>' +
        '</div>' +
        '<div class="hm-ads" id="hm-ads"></div>' +
        '<p class="hm-note">100% in your browser — voice, memory and face never leave this device. <b>Python bridge</b> optional via py/main.py.</p>' +
      '</div>';
    document.body.appendChild(dock);

    el.launch = launch; el.dock = dock;
    el.stage = $('#hm-stage'); el.face = $('#hm-face'); el.caption = $('#hm-caption');
    el.talk = $('#hm-talk'); el.talkLabel = $('#hm-talklabel');
    el.log = $('#hm-log'); el.status = $('#hm-status'); el.statusText = $('#hm-statustext');
    el.persName = $('#hm-persname'); el.dotface = $('#hm-dotface'); el.flag = $('#hm-flag');

    renderPersonas();
    renderFace();
    applyAccent();
    syncControls();
    registerOrb($('#hm-orb'));
    renderSugs($('#hm-sugs'));
    renderAds($('#hm-ads'));
    renderAgentik($('#hm-agentik'));
    setInterval(checkReminders, 4000);
    checkReminders();

    launch.addEventListener('click', function () { state.open ? close() : open(); });
    $('#hm-close').addEventListener('click', close);
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && state.open) close(); });

    el.talk.addEventListener('click', function () {
      if (state.st === 'speaking') { stopSpeaking(); return; }
      if (state.st === 'listening') { stopListening(); return; }
      listen();
    });
    $('#hm-joke').addEventListener('click', function () { say('joke', true); });
    $('#hm-trivia').addEventListener('click', function () { say('trivia nugget', true); });
    $('#hm-hug').addEventListener('click', function () { say('hug', true); });
    $('#hm-voicebtn').addEventListener('click', function () {
      state.voiceOn = !state.voiceOn;
      lsSet(LS_VOICE, state.voiceOn ? '1' : '0');
      if (!state.voiceOn && HAS_TTS) speechSynthesis.cancel();
      stopMouth();
      syncControls();
      setStatus(state.voiceOn ? 'Voice on — ' + PERSONAS[state.persona].label : 'Voice muted — captions only');
    });
    $$('#hm-facerow [data-face]').forEach(function (b) {
      b.addEventListener('click', function () { setFace(b.dataset.face); });
    });
    $('#hm-form').addEventListener('submit', function (e) {
      e.preventDefault();
      var i = $('#hm-input'), v = i.value.trim();
      if (!v) return;
      i.value = '';
      say(v, false);
    });
    $$('#hm-cards .hm-card').forEach(function (c) {
      c.addEventListener('click', function () {
        var acts = {
          surf: 'which virtual worlds can we surf together?',
          learn: 'how do you learn what I like?',
          deliver: 'deliver a message with feeling',
          schedule: 'what\'s on my schedule?',
          news: 'news',
          fun: 'make me smile'
        };
        say(acts[c.dataset.act] || 'hello', false);
      });
    });

    /* greeting badge */
    if (!sessionStorage.getItem(SS_GREET)) el.flag.style.display = 'grid';
    else el.flag.style.display = 'none';

    startBlink();
    startIdle();
  }

  function micSvg() { return '<svg viewBox="0 0 24 24" fill="none" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="2.5" width="6" height="11" rx="3"/><path d="M5.5 11a6.5 6.5 0 0 0 13 0M12 17.5V21M8.5 21h7"/></svg>'; }
  function spkSvg() { return '<svg viewBox="0 0 24 24" fill="none" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"><path d="M4 9v6h4l5 4V5L8 9z"/><path d="M17 8.5a5 5 0 0 1 0 7"/></svg>'; }
  function waveSvg() { return '<svg viewBox="0 0 24 24" fill="none" stroke-width="1.9" stroke-linecap="round"><path d="M3 12c2-6 4-6 6 0s4 6 6 0 4-6 6 0"/></svg>'; }
  function userSvg() { return '<svg viewBox="0 0 24 24" fill="none" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="8" r="4"/><path d="M4.5 21a7.5 7.5 0 0 1 15 0"/></svg>'; }
  function botSvg() { return '<svg viewBox="0 0 24 24" fill="none" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="7" width="16" height="12" rx="4"/><path d="M12 7V4M9 12h.01M15 12h.01M9.5 16h5"/></svg>'; }

  function renderPersonas() {
    var box = $('#hm-personas');
    if (!box) return;
    box.innerHTML = Object.keys(PERSONAS).map(function (k) {
      var p = PERSONAS[k];
      return '<button class="hm-pers' + (k === state.persona ? ' on' : '') + '" data-pers="' + k + '" type="button" style="--pc:' + p.c1 + '" title="' + p.desc + ' · pitch ' + p.pitch + ' · rate ' + p.rate + '"><i></i>' + p.label + '</button>';
    }).join('');
    $$('#hm-personas [data-pers]').forEach(function (b) {
      b.addEventListener('click', function () {
        setPersona(b.dataset.pers);
        speak('Hi — I am ' + PERSONAS[state.persona].label + '. ' + PERSONAS[state.persona].desc + '. This is my voice.');
      });
    });
  }

  function renderFace() {
    if (el.face) {
      el.face.innerHTML = faceMarkup();
      var ph = el.face.querySelector('.hm-photo img');
      if (ph) ph.addEventListener('error', function () {
        if (state.face === 'real') setFace('spatial');   /* never show a broken circle */
      }, { once: true });
    }
    var mini = $('.mini', el.launch);
    if (mini) mini.innerHTML = faceMarkup();
    if (el.dotface) el.dotface.innerHTML = faceMarkup();
    $$('#hm-facerow [data-face]').forEach(function (b) {
      b.classList.toggle('on', b.dataset.face === state.face);
    });
  }

  function applyAccent() {
    var p = PERSONAS[state.persona];
    document.documentElement.style.setProperty('--hm-accent', p.c1);
    document.documentElement.style.setProperty('--hm-accent-2', p.c2);
    if (el.persName) { el.persName.textContent = p.label; el.persName.style.color = p.c1; }
  }

  function syncControls() {
    $$('#hm-personas [data-pers]').forEach(function (b) { b.classList.toggle('on', b.dataset.pers === state.persona); });
    var vb = $('#hm-voicebtn');
    if (vb) { vb.classList.toggle('on', state.voiceOn); vb.setAttribute('aria-pressed', String(state.voiceOn)); $('span', vb).textContent = state.voiceOn ? 'voice' : 'muted'; }
    $$('#hm-facerow [data-face]').forEach(function (b) { b.classList.toggle('on', b.dataset.face === state.face); });
  }

  function open() {
    state.open = true;
    el.dock.classList.add('open');
    el.flag.style.display = 'none';
    try { sessionStorage.setItem(SS_GREET, '1'); } catch (e) {}
    state.interacted = Math.max(state.interacted, 1);
    if (!el.log.children.length) {
      var likes = lsJson(LS_LIKES, []);
      var greet = 'Welcome to the world of the Ai Metaverse! I am VERSED\'ai — your very own friend and sidekick on the net. ' +
        'I can talk, listen, joke, browse worlds with you, keep your schedule and deliver messages with feeling.' +
        (likes.length ? ' And I still remember that you like ' + likes[likes.length - 1] + '.' : '');
      pushMsg('bot', greet);
      setCaption(greet);
      if (state.voiceOn) speak(greet);
    }
    setTimeout(function () { var i = $('#hm-input'); if (i && window.innerWidth > 700) i.focus(); }, 250);
  }
  function close() {
    state.open = false;
    el.dock.classList.remove('open');
    stopListening();
    if (HAS_TTS) speechSynthesis.cancel();
    stopMouth();
    setState('idle');
  }

  /* ==========================================================
     STATE / CAPTION / STATUS
     ========================================================== */
  function setState(st) {
    state.st = st;
    if (el.dock) {
      el.dock.classList.remove('is-idle', 'is-listening', 'is-thinking', 'is-speaking');
      el.dock.classList.add('is-' + st);
    }
    if (el.talk) {
      el.talk.classList.remove('listening', 'thinking', 'speaking');
      if (st !== 'idle') el.talk.classList.add(st);
    }
    if (el.launch) {
      el.launch.classList.toggle('talking', st === 'speaking');
      el.launch.classList.toggle('listening', st === 'listening');
    }
    if (el.status) {
      el.status.className = 'st ' + (st === 'idle' ? '' : st);
    }
    var labels = {
      idle: state.voiceOn ? 'Click to talk' : 'Click to talk (muted)',
      listening: 'Listening… tap to stop',
      thinking: 'Thinking…',
      speaking: 'Speaking… tap to stop'
    };
    if (el.talkLabel) el.talkLabel.textContent = labels[st];
    syncStages();
  }
  function setStatus(t) { if (el.statusText) el.statusText.textContent = t; }
  function setCaption(t, live) {
    if (!el.caption) return;
    el.caption.className = 'hm-caption' + (live ? '' : '');
    el.caption.innerHTML = live ? '<span class="live">“' + escapeHtml(t) + '”</span>' : escapeHtml(t);
  }
  function escapeHtml(s) {
    return String(s).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; });
  }
  function pushMsg(cls, txt) {
    if (!el.log) return;
    var d = document.createElement('div');
    d.className = 'hm-msg ' + cls;
    d.textContent = txt;
    el.log.appendChild(d);
    while (el.log.children.length > 24) el.log.removeChild(el.log.firstChild);
    el.log.scrollTop = el.log.scrollHeight;
  }

  /* ==========================================================
     MOUTH + BLINK + IDLE
     ========================================================== */
  function startMouth(random) {
    stopMouth();
    var t = 0;
    state.mouthRaf = setInterval(function () {
      t += .19;
      var v = random ? (.26 + Math.random() * .74) : (.32 + .64 * Math.abs(Math.sin(t)) * Math.abs(Math.cos(t * .55)));
      if (el.stage) el.stage.style.setProperty('--mouth', Math.max(.05, Math.min(1, v)).toFixed(3));
    }, 62);
  }
  function stopMouth() {
    if (state.mouthRaf) { clearInterval(state.mouthRaf); state.mouthRaf = null; }
    if (el.stage) el.stage.style.removeProperty('--mouth');
  }
  function startBlink() {
    if (state.blinkTimer) clearTimeout(state.blinkTimer);
    (function loop() {
      state.blinkTimer = setTimeout(function () {
        var f = el.face;
        if (f && state.open && !reduceMotion) {
          f.classList.add('blink');
          setTimeout(function () { f.classList.remove('blink'); }, 140);
        }
        loop();
      }, 2400 + Math.random() * 4200);
    })();
  }
  function startIdle() {
    if (state.idleTimer) clearInterval(state.idleTimer);
    state.idleTimer = setInterval(function () {
      if (!state.open || state.st !== 'idle' || !state.interacted || !state.voiceOn) return;
      if (Math.random() < .55) return;
      var likes = lsJson(LS_LIKES, []);
      var line = IDLE[Math.floor(Math.random() * IDLE.length)];
      if (likes.length && Math.random() < .5) {
        line = 'Because you like ' + likes[likes.length - 1] + ', I found something for you: the Worlds page has an environment built around exactly that. Want me to open it?';
      }
      pushMsg('bot', line);
      setCaption(line);
      speak(line);
    }, 52000);
  }

  /* ==========================================================
     SPEECH (TTS with persona) + LISTEN (STT)
     ========================================================== */
  var HAS_TTS = ('speechSynthesis' in window);
  var RECO = window.SpeechRecognition || window.webkitSpeechRecognition || null;

  function pickVoice(p) {
    if (!HAS_TTS) return null;
    var vs = speechSynthesis.getVoices() || [];
    if (!vs.length) return null;
    var en = vs.filter(function (v) { return /^en/i.test(v.lang); });
    var pool = en.length ? en : vs;
    return pool.filter(function (v) { return p.voice.test(v.name); })[0] || pool[0] || null;
  }
  function speak(text, onDone) {
    var plain = String(text).replace(/<[^>]*>/g, ' ').replace(/\s+/g, ' ').trim();
    if (!plain) { if (onDone) onDone(); return; }
    state.interacted = Math.max(state.interacted, 1);
    if (!state.voiceOn || !HAS_TTS) {
      setState('speaking');
      setStatus('Captions only (voice off)');
      startMouth(true);
      var ms = Math.min(9000, 1300 + plain.length * 34);
      setTimeout(function () { stopMouth(); setState('idle'); setStatus('Online'); if (onDone) onDone(); }, reduceMotion ? 400 : ms);
      return;
    }
    try {
      speechSynthesis.cancel();
      var p = PERSONAS[state.persona];
      var u = new SpeechSynthesisUtterance(plain);
      var v = pickVoice(p); if (v) u.voice = v;
      u.pitch = p.pitch; u.rate = p.rate; u.volume = 1;
      var spoke = false;
      u.onstart = function () { spoke = true; setState('speaking'); setStatus('Speaking as ' + p.label); startMouth(false); };
      u.onboundary = function () { startMouth(true); };
      u.onend = u.onerror = function () { stopMouth(); setState('idle'); setStatus('Online · ' + p.label); if (onDone) onDone(); };
      speechSynthesis.speak(u);
      setTimeout(function () {
        if (!spoke && !speechSynthesis.speaking && state.st === 'speaking') { stopMouth(); setState('idle'); if (onDone) onDone(); }
      }, 4000);
    } catch (e) { stopMouth(); setState('idle'); if (onDone) onDone(); }
  }
  function stopSpeaking() {
    if (HAS_TTS) speechSynthesis.cancel();
    stopMouth();
    setState('idle');
    setStatus('Stopped');
  }

  function listen() {
    if (!RECO) {
      setCaption('This browser has no speech recognition — type to me below instead. (Chrome and Edge support CLICK TO TALK.)');
      setStatus('Mic unsupported here');
      var i = $('#hm-input'); if (i) i.focus();
      return;
    }
    if (state.recoLive) { stopListening(); return; }
    try {
      var R = new RECO();
      state.reco = R;
      R.lang = 'en-US'; R.interimResults = true; R.maxAlternatives = 1; R.continuous = false;
      R.onstart = function () { state.recoLive = true; setState('listening'); setStatus('Listening…'); setCaption('Listening…', true); };
      R.onresult = function (ev) {
        var interim = '', fin = '';
        for (var i = 0; i < ev.results.length; i++) {
          if (ev.results[i].isFinal) fin += ev.results[i][0].transcript;
          else interim += ev.results[i][0].transcript;
        }
        if (interim) setCaption(interim, true);
        if (fin) { stopListening(); say(fin.trim(), true); }
      };
      R.onerror = function (ev) {
        stopListening();
        var why = (ev && ev.error === 'not-allowed') ? 'Microphone permission denied — allow it in your browser, or type below.' :
                  'I could not hear that (' + ((ev && ev.error) || 'error') + '). Try again, or type.';
        setCaption(why); setStatus('Mic error');
        pushMsg('bot', why);
      };
      R.onend = function () { if (state.recoLive) { stopListening(); setCaption('I did not catch anything — tap CLICK TO TALK again.'); } };
      R.start();
    } catch (e) { stopListening(); setCaption('Microphone failed to start. Type below instead.'); }
  }
  function stopListening() {
    state.recoLive = false;
    try { if (state.reco) state.reco.stop(); } catch (e) {}
    state.reco = null;
    if (state.st === 'listening') setState('idle');
  }

  /* ---------- the conversation ---------- */
  function say(userText, fromVoice) {
    if (!state.open) open();
    pushMsg('me', userText);
    setCaption('Thinking…');
    setState('thinking');
    setStatus('Thinking…');
    if (window.eel && window.eel.user_said) {
      try {
        window.eel.user_said(userText)(function (reply) {
          pushMsg('bot', reply); setCaption(reply); speak(reply);
        });
        return;
      } catch (e) {}
    }
    setTimeout(function () {
      var reply = brain(userText);
      pushMsg('bot', reply);
      setCaption(reply);
      refreshSugs(reply);
      speak(reply);
      if (fromVoice) { /* keep flow */ }
    }, reduceMotion ? 60 : 420 + Math.random() * 380);
  }

  function renderAgentik(host) {
    if (!host) return;
    host.innerHTML =
      '<button class="hm-ag" data-ag="plan" type="button" title="Read your reminders, tasks and traits, then speak a plan">🧭 Plan my day</button>' +
      '<button class="hm-ag" data-ag="prompt" type="button" title="Generate a Craiyon prompt from your persona">🎨 Art prompt</button>' +
      '<button class="hm-ag" data-ag="rem" type="button" title="Quick reminder">⏰ Remind</button>' +
      '<button class="hm-ag" data-ag="apis" type="button" title="Open APIKonnect">🔌 APIKonnect</button>';
    $('[data-ag="plan"]', host).addEventListener('click', function () {
      var rem = reminders().filter(function (x) { return !x.done; });
      var tk = tasks().filter(function (x) { return !x.done; });
      var pe = lsJson('aimv_profile_v1', {}).persona || {};
      var line = 'Here is your day: ' + (rem.length ? rem.length + ' reminder' + (rem.length > 1 ? 's' : '') + ' (' + rem[0].t + ' first), ' : 'no reminders, ') +
        (tk.length ? tk.length + ' open task' + (tk.length > 1 ? 's' : '') + ' (' + tk[0].t + ' leads), ' : 'an empty task board, ') +
        'and a ' + (pe.sign || 'curious') + ' energy profile led by ' + (pe.top || 'wit') + '. I would start with the hardest thing while your ' + (pe.top || 'wit') + ' is fresh.';
      pushMsg('bot', line); setCaption(line); refreshSugs(line); speak(line);
    });
    $('[data-ag="prompt"]', host).addEventListener('click', function () {
      var likes = lsJson(LS_LIKES, []);
      var pe = lsJson('aimv_profile_v1', {}).persona || {};
      var sub = likes.length ? likes[likes.length - 1] : 'a luminous digital twin';
      var line = 'Craiyon prompt: "' + sub + ' as a ' + (pe.sign || 'celestial') + ' deity of the metaverse, ' +
        (pe.element || 'light') + '-element ribbons, volumetric glow, cinematic rim light, 8k detail" — copied to your clipboard and queued in Ai-Labs.';
      try { if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(sub + ' as a ' + (pe.sign || 'celestial') + ' deity of the metaverse, ' + (pe.element || 'light') + '-element ribbons, volumetric glow, cinematic rim light, 8k detail'); } catch (e) {}
      pushMsg('bot', line); setCaption(line); refreshSugs(line); speak(line);
    });
    $('[data-ag="rem"]', host).addEventListener('click', function () {
      var i = $('#hm-input'); if (i) { i.value = 'remind me to '; i.focus(); }
    });
    $('[data-ag="apis"]', host).addEventListener('click', function () { location.href = 'apikonnect/index.html'; });
  }

  /* ---------- public controls ---------- */
  function setFace(f) {
    if (['spatial', 'real', 'robot'].indexOf(f) === -1) return;
    state.face = f;
    lsSet(LS_FACE, f);
    renderFace();
    syncStages();
    var names = { spatial: 'my spatial light-ribbon head', real: 'my photographed human face', robot: 'my brushed-metal robot head' };
    setStatus('Face: ' + f);
    if (state.open) speak('This is ' + names[f] + '. Same buddy, new look.');
  }
  function setPersona(k) {
    if (!PERSONAS[k]) return;
    state.persona = k;
    lsSet(LS_PERS, k);
    applyAccent();
    syncControls();
    setStatus('Persona: ' + PERSONAS[k].label);
  }

  /* ---------- Python (Eel) bridge: desktop voice lip-sync ---------- */
  window.avatar_say = function (text) {
    if (!state.open) open();
    setState('speaking');
    setStatus('Speaking via Python TTS…');
    startMouth(true);
    var ms = Math.min(12000, 1400 + String(text).length * 55);
    setTimeout(function () { stopMouth(); setState('idle'); setStatus('Online'); }, ms);
    return String(text || '');
  };


  /* ==========================================================
     SUGGESTIVE PROMPTING — chips drawn from the repo brain
     ========================================================== */
  var SUGGESTS = [
    'Clone myself in four steps', 'Show me worlds for music lovers',
    'Write a Craiyon prompt for my avatar', 'What trait does my birthday give me?',
    'Find a free tool for video edits', 'Remember demo day on Friday',
    'Tell me a joke', 'Connect my APIs in APIKonnect',
    'Plan my day', 'Deliver a message to my team: the build is live'
  ];
  function followups(reply) {
    var r = String(reply).toLowerCase(), out = [];
    if (/clone|selfie|avatar|birthday/.test(r)) out = ['Record my voice snippet', 'What does my zodiac say?', 'Forge the agent now'];
    else if (/world|metaverse|mars/.test(r)) out = ['Which world fits a concert?', 'Route me to Somnium Space', 'What is Planet.Ai?'];
    else if (/art|craiyon|image|prompt/.test(r)) out = ['Make it cyberpunk', 'Nine variants please', 'Save the prompt to my agent'];
    else if (/tool|free|directory/.test(r)) out = ['Best tool for lyrics?', 'Is Wordtune free?', 'Open the tools directory'];
    else if (/schedule|remind|calendar/.test(r)) out = ['Remind me in 2 minutes to stretch', 'List my reminders', 'Add task ship the demo'];
    else if (/joke|trivia|news/.test(r)) out = ['Another one', 'Tell me trivia', 'What is new today?'];
    else if (/voice|persona/.test(r)) out = ['Sound like ATLAS', 'Sound like PIXEL', 'Mute yourself'];
    else out = ['What can you do for me?', 'Clone myself in four steps', 'Tell me a joke'];
    return out;
  }
  var sugHosts = [];
  function renderSugs(host, list) {
    if (!host) return;
    host.innerHTML = (list || SUGGESTS).slice(0, 4).map(function (t) {
      return '<button class="hm-sug" type="button" data-sug="' + escapeHtml(t) + '">✨ ' + escapeHtml(t) + '</button>';
    }).join('');
    $$('[data-sug]', host).forEach(function (b) {
      b.addEventListener('click', function () { say(b.dataset.sug, false); });
    });
    if (sugHosts.indexOf(host) === -1) sugHosts.push(host);
  }
  function refreshSugs(reply) {
    sugHosts.forEach(function (h) { renderSugs(h, followups(reply)); });
  }

  /* ==========================================================
     AD-SERVE BOX — sponsored by Alibaba & Qwen
     ========================================================== */
  var ADS = [
    { tag: 'Alibaba Cloud', t: 'Model Studio', d: 'Fine-tune and serve Qwen-Max behind your agent with one console.', u: 'https://www.alibabacloud.com/product/modelstudio' },
    { tag: 'Qwen', t: 'Qwen-Max', d: 'Frontier reasoning from the Tongyi Qianwen family — a single API call away.', u: 'https://qwen.ai' },
    { tag: 'Qwen', t: 'Qwen-VL', d: 'Vision-language eyes for your avatar: images in, grounded answers out.', u: 'https://huggingface.co/Qwen' },
    { tag: 'Alibaba Cloud', t: 'PAI-EAS inference', d: 'GPU endpoints that scale to zero between conversations. Pay per token.', u: 'https://www.alibabacloud.com/product/machine-learning' },
    { tag: 'Qwen', t: 'Qwen-Agent', d: 'Open-source agent framework: tools, memory and planning for your forge.', u: 'https://github.com/QwenLM/Qwen-Agent' },
    { tag: 'Alibaba Cloud', t: 'Tongyi Tingwu', d: 'Meeting transcription that feeds your companion\u2019s schedule automatically.', u: 'https://www.alibabacloud.com' }
  ];
  var adHosts = [], adIx = 0;
  function renderAds(host) {
    if (!host || adHosts.indexOf(host) !== -1) return;
    adHosts.push(host);
    paintAd(host, adIx);
  }
  function paintAd(host, ix) {
    var a = ADS[ix % ADS.length];
    host.innerHTML =
      '<div class="hm-ad-head"><span class="hm-ad-badge">Ad</span><span>Sponsored · served by Alibaba &amp; Qwen</span>' +
      '<button class="hm-ad-next" type="button" title="Next ad">↻</button></div>' +
      '<a class="hm-ad" href="' + a.u + '" target="_blank" rel="noopener noreferrer sponsored">' +
        '<b>' + a.t + '</b><span>' + a.d + '</span><em>' + a.tag + ' ↗</em>' +
      '</a>';
    var nx = $('.hm-ad-next', host);
    if (nx) nx.addEventListener('click', function (e) { e.preventDefault(); adIx++; paintAllAds(); });
  }
  function paintAllAds() { adHosts.forEach(function (h) { paintAd(h, adIx); }); }
  setInterval(function () { adIx++; paintAllAds(); }, 9000);

  /* ==========================================================
     REMINDERS · TASKS · DELIVERED MESSAGES (agentic + communicative)
     ========================================================== */
  var LS_REM = 'aimv_reminders', LS_TASKS = 'aimv_tasks', LS_SENT = 'aimv_sent';
  var DAYMS = 86400000;
  function parseReminder(text) {
    var m, now = Date.now();
    if ((m = text.match(/remind me to (.+?) in (\d+(?:\.\d+)?)\s*(minute|min|hour|hr|second|sec)s?/i))) {
      var mult = /h/i.test(m[3]) ? 3600000 : (/s/i.test(m[3]) && !/min/i.test(m[3]) ? 1000 : 60000);
      return { t: m[1].trim(), due: now + parseFloat(m[2]) * mult };
    }
    if ((m = text.match(/remind me to (.+?) at (\d{1,2})(?::(\d{2}))?\s*(am|pm)?/i))) {
      var d = new Date(); var h = +m[2]; var ap = (m[4] || '').toLowerCase();
      if (ap === 'pm' && h < 12) h += 12; if (ap === 'am' && h === 12) h = 0;
      d.setHours(h, +(m[3] || 0), 0, 0);
      if (d.getTime() < now) d.setTime(d.getTime() + DAYMS);
      return { t: m[1].trim(), due: d.getTime() };
    }
    if ((m = text.match(/remind me to (.+?) on (monday|tuesday|wednesday|thursday|friday|saturday|sunday)/i))) {
      var names = ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday'];
      var target = names.indexOf(m[2].toLowerCase());
      var dd = new Date(); dd.setHours(9, 0, 0, 0);
      var delta = (target - dd.getDay() + 7) % 7 || 7;
      dd.setTime(dd.getTime() + delta * DAYMS);
      return { t: m[1].trim(), due: dd.getTime() };
    }
    if ((m = text.match(/remind me to (.+)/i))) return { t: m[1].trim(), due: now + 3600000 };
    return null;
  }
  function reminders() { return lsJson(LS_REM, []); }
  function saveReminders(v) { lsSave(LS_REM, v); }
  function tasks() { return lsJson(LS_TASKS, []); }
  function saveTasks(v) { lsSave(LS_TASKS, v); }
  function sentMsgs() { return lsJson(LS_SENT, []); }

  function checkReminders() {
    var list = reminders(), now = Date.now(), fired = false;
    list.forEach(function (r) {
      if (!r.done && r.due <= now) {
        r.done = true; fired = true;
        var line = '⏰ Reminder: ' + r.t + '. Right on time — I am never late.';
        if (state.open) { pushMsg('bot', line); setCaption(line); }
        toastAgent(line);
        speak(line);
      }
    });
    if (fired) saveReminders(list);
  }
  function toastAgent(line) {
    var t = $('#hm-rem-toast');
    if (!t) {
      t = document.createElement('div'); t.id = 'hm-rem-toast'; t.className = 'hm-rem-toast';
      document.body.appendChild(t);
      t.addEventListener('click', function () { open(); t.classList.remove('show'); });
    }
    t.textContent = line;
    t.classList.add('show');
    setTimeout(function () { t.classList.remove('show'); }, 12000);
  }

  /* ==========================================================
     EMBEDDED STAGE (hero / pages) — face + CLICK TO TALK inline
     ========================================================== */
  function mountStage(host) {
    if (!host || host.dataset.hmStage) return;
    host.dataset.hmStage = '1';
    host.classList.add('hm-stage-embed');
    host.innerHTML =
      '<div class="hm-estage"><canvas class="orb-canvas" data-e="orb"></canvas><span class="hm-orb-ring"></span><span class="hm-orb-ring r2"></span><span class="aura"></span><div class="hm-face" data-e="face"></div></div>' +
      '<div class="hm-caption idle" data-e="cap">Click to talk — I listen, I answer, I remember.</div>' +
      '<div class="hm-talkrow"><button class="hm-talk" data-e="talk" type="button">' + micSvg() + '<span data-e="talklabel">Click to talk</span></button>' +
      '<button class="hm-mini-btn" data-e="joke" type="button" title="Joke">😄</button>' +
      '<button class="hm-mini-btn" data-e="trivia" type="button" title="Trivia">🧠</button>' +
      '<button class="hm-mini-btn" data-e="hug" type="button" title="Hug">💜</button></div>' +
      '<div class="hm-faceswitch" data-e="fs" role="group" aria-label="Companion face">' +
        '<button class="hm-fs" data-eface="spatial" type="button" title="Spatial light-ribbon face">' + waveSvg() + '</button>' +
        '<button class="hm-fs" data-eface="real" type="button" title="Photoreal face">' + userSvg() + '</button>' +
        '<button class="hm-fs" data-eface="robot" type="button" title="Robot face">' + botSvg() + '</button>' +
      '</div>' +
      '<div class="hm-sugs" data-e="sugs"></div>' +
      '<div class="hm-ads" data-e="ads"></div>';
    $$('[data-eface]', host).forEach(function (b) {
      b.addEventListener('click', function () { setFace(b.dataset.eface); });
    });
    var face = $('[data-e="face"]', host);
    function paint() { face.innerHTML = faceMarkup(); }
    paint();
    host._hmPaint = paint;
    $('[data-e="talk"]', host).addEventListener('click', function () {
      if (state.st === 'speaking') { stopSpeaking(); return; }
      if (state.st === 'listening') { stopListening(); return; }
      listen();
    });
    $('[data-e="joke"]', host).addEventListener('click', function () { say('joke', false); });
    $('[data-e="trivia"]', host).addEventListener('click', function () { say('trivia nugget', false); });
    $('[data-e="hug"]', host).addEventListener('click', function () { say('hug', false); });
    renderSugs($('[data-e="sugs"]', host));
    renderAds($('[data-e="ads"]', host));
    registerOrb($('[data-e="orb"]', host));
    stageHosts.push(host);
    syncStages();
  }
  var stageHosts = [];
  function syncStages() {
    stageHosts.forEach(function (h) {
      var f = $('[data-e="face"]', h); if (f) f.innerHTML = faceMarkup();
      var cap = $('[data-e="cap"]', h);
      if (cap) cap.textContent = state.st === 'listening' ? 'Listening…' : (state.st === 'speaking' ? 'Speaking…' : 'Click to talk — I listen, I answer, I remember.');
      var tk = $('[data-e="talk"]', h);
      if (tk) { tk.classList.remove('listening', 'thinking', 'speaking'); if (state.st !== 'idle') tk.classList.add(state.st); }
      var lb = $('[data-e="talklabel"]', h);
      if (lb) lb.textContent = { idle: 'Click to talk', listening: 'Listening… tap to stop', thinking: 'Thinking…', speaking: 'Speaking… tap to stop' }[state.st];
      $$('[data-eface]', h).forEach(function (b) { b.classList.toggle('on', b.dataset.eface === state.face); });
      var mouth = $('.hm-estage', h);
      if (mouth) mouth.style.setProperty('--mouth', el.stage ? (el.stage.style.getPropertyValue('--mouth') || '') : '');
    });
  }

  /* ==========================================================
     LIVE ORB CANVAS — the PIL orb art, animated
     base texture: assets/face-orb.jpg + drifting constellation
     ========================================================== */
  var orbCanvases = [], orbPts = [], orbImg = null, orbRaf = null;
  function orbImage() {
    if (orbImg) return orbImg;
    try {
      orbImg = new Image();
      orbImg.src = assetBase() + 'face-orb.jpg';
    } catch (e) { orbImg = null; }
    return orbImg;
  }
  function seedOrb() {
    orbPts = [];
    for (var i = 0; i < 34; i++) {
      var a = Math.random() * Math.PI * 2, r = Math.sqrt(Math.random()) * .82;
      orbPts.push({ x: Math.cos(a) * r, y: Math.sin(a) * r,
                    vx: (Math.random() - .5) * .0009, vy: (Math.random() - .5) * .0009,
                    s: 1 + Math.random() * 2.2, p: Math.random() * 6.28 });
    }
  }
  function registerOrb(cvs) {
    if (!cvs || orbCanvases.indexOf(cvs) !== -1) return;
    var ctx = null;
    try { ctx = cvs.getContext('2d'); } catch (e) { cvs.style.display = 'none'; return; }
    if (!ctx) { cvs.style.display = 'none'; return; }
    orbCanvases.push(cvs);
    if (!orbPts.length) seedOrb();
    if (orbRaf === null && !reduceMotion) orbRaf = requestAnimationFrame(orbLoop);
    if (reduceMotion) drawOrb(cvs, ctx, 0);
  }
  function orbLoop(t) {
    for (var i = 0; i < orbCanvases.length; i++) {
      var cvs = orbCanvases[i];
      if (!cvs.isConnected || !cvs.offsetParent) continue;
      var ctx = null;
      try { ctx = cvs.getContext('2d'); } catch (e) { continue; }
      drawOrb(cvs, ctx, t);
    }
    orbRaf = requestAnimationFrame(orbLoop);
  }
  function drawOrb(cvs, ctx, t) {
    var dpr = Math.min(window.devicePixelRatio || 1, 2);
    var w = cvs.clientWidth || 300, h = cvs.clientHeight || w;
    if (cvs.width !== Math.round(w * dpr)) { cvs.width = Math.round(w * dpr); cvs.height = Math.round(h * dpr); }
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.clearRect(0, 0, w, h);
    var cx = w / 2, cy = h / 2, R = Math.min(w, h) / 2;
    var pulse = 1 + (reduceMotion ? 0 : Math.sin(t / 900) * .012);
    /* base texture: the generated orb art */
    var img = orbImage();
    ctx.save();
    ctx.beginPath(); ctx.arc(cx, cy, R, 0, 6.2832); ctx.clip();
    if (!photoMode && img && img.complete && img.naturalWidth) {
      ctx.globalAlpha = .85;
      try { ctx.drawImage(img, 0, 0, w, h); } catch (e) {}
      ctx.globalAlpha = 1;
    }
    var photoMode = (state.face === 'real');
    if (!photoMode) {
      /* inner glow sphere (spatial / robot modes) */
      var g = ctx.createRadialGradient(cx, cy - R * .18, R * .08, cx, cy, R * pulse);
      g.addColorStop(0, 'rgba(160,96,255,.55)');
      g.addColorStop(.55, 'rgba(84,42,196,.28)');
      g.addColorStop(1, 'rgba(8,4,24,0)');
      ctx.fillStyle = g;
      ctx.beginPath(); ctx.arc(cx, cy, R * pulse, 0, 6.2832); ctx.fill();
    }
    /* drifting constellation inside the orb */
    var i, j, p, q;
    for (i = 0; i < orbPts.length; i++) {
      p = orbPts[i];
      p.x += p.vx * 16; p.y += p.vy * 16; p.p += .02;
      var rr = Math.sqrt(p.x * p.x + p.y * p.y);
      if (rr > .86) { p.vx *= -1; p.vy *= -1; p.x *= .86 / rr; p.y *= .86 / rr; }
    }
    for (i = 0; i < orbPts.length; i++) {
      p = orbPts[i];
      for (j = i + 1; j < orbPts.length; j++) {
        q = orbPts[j];
        var dx = p.x - q.x, dy = p.y - q.y, d = Math.sqrt(dx * dx + dy * dy);
        if (d < .34) {
          ctx.strokeStyle = 'rgba(168,85,247,' + ((1 - d / .34) * (photoMode ? .18 : .5)).toFixed(3) + ')';
          ctx.lineWidth = .8;
          ctx.beginPath();
          ctx.moveTo(cx + p.x * R, cy + p.y * R);
          ctx.lineTo(cx + q.x * R, cy + q.y * R);
          ctx.stroke();
        }
      }
    }
    for (i = 0; i < orbPts.length; i++) {
      p = orbPts[i];
      var tw = .5 + .5 * Math.abs(Math.sin(p.p));
      ctx.fillStyle = 'rgba(0,240,255,' + ((photoMode ? .22 : .5) + .5 * tw * (photoMode ? .35 : 1)).toFixed(3) + ')';
      ctx.beginPath(); ctx.arc(cx + p.x * R, cy + p.y * R, p.s * .8, 0, 6.2832); ctx.fill();
      ctx.fillStyle = 'rgba(0,240,255,' + ((photoMode ? .05 : .12) * tw).toFixed(3) + ')';
      ctx.beginPath(); ctx.arc(cx + p.x * R, cy + p.y * R, p.s * 2.6, 0, 6.2832); ctx.fill();
    }
    /* rim light */
    ctx.strokeStyle = 'rgba(0,240,255,.28)';
    ctx.lineWidth = 1.4;
    ctx.beginPath(); ctx.arc(cx, cy, R - 1.5, 0, 6.2832); ctx.stroke();
    ctx.restore();
  }

  /* ---------- boot ---------- */
  
  function boot() {
    build();
    if (HAS_TTS) { try { speechSynthesis.getVoices(); } catch (e) {} }
    window.addEventListener('pagehide', function () { if (HAS_TTS) speechSynthesis.cancel(); stopMouth(); });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot);
  else boot();

  window.AIMV_HUMANOID = {
    open: open, close: close,
    toggle: function () { state.open ? close() : open(); },
    speak: function (t) { if (!state.open) open(); setCaption(t); speak(t); },
    dockOpen: function () { return state.open; },
    think: function () { setState('thinking'); setStatus('Thinking…'); setCaption('Thinking…'); },
    say: say, listen: listen, stop: stopSpeaking,
    face: function () { return state.face; }, setFace: setFace,
    persona: function () { return state.persona; }, setPersona: setPersona,
    voiceOn: function () { return state.voiceOn; },
    setVoice: function (on) { state.voiceOn = !!on; lsSet(LS_VOICE, on ? '1' : '0'); syncControls(); },
    state: function () { return state.st; },
    brain: brain,
    mountStage: mountStage, renderAds: renderAds, renderSugs: renderSugs,
    reminders: reminders, tasks: tasks, sent: sentMsgs,
    likes: function () { return lsJson(LS_LIKES, []); },
    events: function () { return lsJson(LS_EVENTS, []); },
    PERSONAS: PERSONAS
  };
})();
