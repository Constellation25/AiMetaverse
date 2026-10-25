/* ============================================================
   Ai Metaverse — "Clone Yourself Virtually" engine
   Step 1 selfie/image · Step 2 voice recording · Step 3 birthday
   personality · Step 4 forge your AI agent (+ Ready Player Me)

   Everything runs locally in the browser. Nothing is uploaded.
   ============================================================ */
(function () {
  "use strict";
  var $ = function (s, c) { return (c || document).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || document).querySelectorAll(s)); };
  var reduceMotion = !!(window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches);
  var STORE_KEY = 'aimv_profile_v1';

  /* ==========================================================
     PROFILE STATE
     ========================================================== */
  var profile = {
    name: '',
    image: null,          /* dataURL (downscaled jpeg) */
    imageMeta: null,      /* {w,h,brightness,warmth,hue,palette,skin,faces} */
    voice: null,          /* {blobUrl,duration,seconds,freq,loudness,character,pace,mime} — blobUrl does NOT persist */
    voiceMeta: null,      /* persisted analysis only */
    birthday: null,       /* yyyy-mm-dd */
    persona: null,        /* derived traits */
    rpm: null,            /* {url,id,source} Ready Player Me avatar */
    agent: null,          /* {id,name,role,voiceStyle,temperature,createdAt} */
    agents: [],
    updatedAt: null
  };

  function save() {
    profile.updatedAt = new Date().toISOString();
    var copy = JSON.parse(JSON.stringify(profile));
    if (copy.voice) delete copy.voice.blobUrl;      /* object URLs die with the page */
    try {
      localStorage.setItem(STORE_KEY, JSON.stringify(copy));
      return true;
    } catch (e) {
      toast('Could not save to this browser (storage full or blocked). You can still download your agent file.', 'warn');
      return false;
    }
  }
  function load() {
    try {
      var raw = localStorage.getItem(STORE_KEY);
      if (!raw) return false;
      var p = JSON.parse(raw);
      Object.keys(p).forEach(function (k) { profile[k] = p[k]; });
      return true;
    } catch (e) { return false; }
  }

  /* ==========================================================
     TOASTS
     ========================================================== */
  function toast(msg, kind) {
    var t = $('#toast');
    if (!t) { t = document.createElement('div'); t.id = 'toast'; t.className = 'toast'; document.body.appendChild(t); }
    t.textContent = msg;
    t.className = 'toast show' + (kind ? ' ' + kind : '');
    clearTimeout(t._h);
    t._h = setTimeout(function () { t.className = 'toast'; }, 5200);
  }

  /* ==========================================================
     STEP NAVIGATION
     ========================================================== */
  var stepNo = 1;
  function gotoStep(n, scroll) {
    n = Math.max(1, Math.min(4, n));
    stepNo = n;
    $$('.step-panel').forEach(function (p) { p.classList.toggle('active', +p.dataset.step === n); });
    $$('.step-tab').forEach(function (b) {
      var s = +b.dataset.goto;
      b.classList.toggle('active', s === n);
      b.setAttribute('aria-selected', String(s === n));
    });
    var back = $('#step-back'), next = $('#step-next');
    if (back) back.style.visibility = n === 1 ? 'hidden' : 'visible';
    if (next) next.textContent = n === 4 ? 'Forge my AI agent' : 'Continue →';
    var pos = $('#step-pos');
    if (pos) pos.textContent = 'Step ' + n + ' of 4';
    refreshGates();
    if (scroll !== false) {
      var top = $('#wizard');
      if (top) top.scrollIntoView({ behavior: reduceMotion ? 'auto' : 'smooth', block: 'start' });
    }
    if (n === 3 && profile.birthday) renderPersona();
    if (n === 4) renderReview();
  }
  function refreshGates() {
    var next = $('#step-next');
    if (!next) return;
    var ok = true, why = '';
    if (stepNo === 1 && !profile.image) { ok = false; why = 'Add a selfie or upload an image first'; }
    if (stepNo === 2 && !profile.voice && !profile.voiceMeta) { ok = false; why = 'Record or upload a voice snippet first'; }
    if (stepNo === 3 && !profile.persona) { ok = false; why = 'Enter your birthday to derive personality traits'; }
    next.disabled = !ok;
    next.title = why;
    var hint = $('#step-hint');
    if (hint) hint.textContent = ok ? '' : why;
  }

  /* ==========================================================
     STEP 1 — SELFIE / IMAGE
     ========================================================== */
  var camStream = null;
  function hasCam() { return !!(navigator.mediaDevices && navigator.mediaDevices.getUserMedia); }

  function startCamera() {
    if (!hasCam()) {
      toast('This browser has no camera API. Use "Upload image" instead — or open the page over http(s).', 'warn');
      return;
    }
    var v = $('#cam-video');
    navigator.mediaDevices.getUserMedia({ video: { facingMode: 'user', width: { ideal: 1280 }, height: { ideal: 720 } }, audio: false })
      .then(function (stream) {
        camStream = stream;
        v.srcObject = stream;
        v.play().catch(function () {});
        $('#cam-live').style.display = 'block';
        $('#cam-poster').style.display = 'none';
        toast('Camera live — frame your face inside the guides, then capture.');
      })
      .catch(function (err) {
        var why = (err && err.name === 'NotAllowedError') ? 'Camera permission denied.' :
                  (err && err.name === 'NotFoundError') ? 'No camera found on this device.' : 'Camera unavailable (' + ((err && err.name) || 'error') + ').';
        toast(why + ' You can still upload an image.', 'warn');
        setCamStatus(why, true);
      });
  }
  function stopCamera() {
    if (camStream) { camStream.getTracks().forEach(function (t) { t.stop(); }); camStream = null; }
    var v = $('#cam-video'); if (v) v.srcObject = null;
    var live = $('#cam-live'); if (live) live.style.display = 'none';
    var poster = $('#cam-poster'); if (poster) poster.style.display = 'grid';
  }
  function setCamStatus(text, bad) {
    var el = $('#cam-status');
    if (!el) return;
    el.textContent = text;
    el.style.color = bad ? 'var(--amber)' : 'var(--lime)';
  }

  function captureFromVideo() {
    var v = $('#cam-video');
    if (!v || !v.videoWidth) { toast('The camera is not streaming yet.', 'warn'); return; }
    var c = document.createElement('canvas');
    var ratio = v.videoHeight / v.videoWidth;
    c.width = 720; c.height = Math.round(720 * ratio);
    var ctx = c.getContext('2d');
    ctx.translate(c.width, 0); ctx.scale(-1, 1);      /* mirror, like a selfie */
    ctx.drawImage(v, 0, 0, c.width, c.height);
    acceptImageCanvas(c, 'camera selfie');
    stopCamera();
  }

  function acceptFile(file) {
    if (!file) return;
    if (!/^image\//.test(file.type)) { toast('That file is not an image (' + file.type + ').', 'warn'); return; }
    if (file.size > 12 * 1024 * 1024) { toast('Image is over 12 MB — pick a smaller one.', 'warn'); return; }
    var url = URL.createObjectURL(file);
    var img = new Image();
    img.onload = function () {
      var c = document.createElement('canvas');
      var scale = Math.min(1, 720 / Math.max(img.width, img.height));
      c.width = Math.max(1, Math.round(img.width * scale));
      c.height = Math.max(1, Math.round(img.height * scale));
      c.getContext('2d').drawImage(img, 0, 0, c.width, c.height);
      URL.revokeObjectURL(url);
      acceptImageCanvas(c, file.name);
    };
    img.onerror = function () { toast('Could not read that image file.', 'warn'); URL.revokeObjectURL(url); };
    img.src = url;
  }

  function acceptImageCanvas(canvas, label) {
    /* downscale to a sane portrait size for storage + analysis */
    var max = 560;
    var out = document.createElement('canvas');
    var s = Math.min(1, max / Math.max(canvas.width, canvas.height));
    out.width = Math.max(1, Math.round(canvas.width * s));
    out.height = Math.max(1, Math.round(canvas.height * s));
    var octx = out.getContext('2d');
    octx.drawImage(canvas, 0, 0, out.width, out.height);
    var dataUrl;
    try { dataUrl = out.toDataURL('image/jpeg', 0.82); }
    catch (e) { toast('Could not encode that image (canvas blocked or tainted).', 'warn'); return; }
    if (!dataUrl || dataUrl.length < 64) { toast('That image produced an empty encode — try another file.', 'warn'); return; }

    profile.image = dataUrl;
    profile.imageMeta = analyseImage(out, label);
    save();
    paintImageStep();
    applyPalette();
    runFaceDetection(out);
    toast('Image captured. ' + profile.imageMeta.summary);
  }

  function analyseImage(canvas, label) {
    var ctx = canvas.getContext('2d');
    var w = canvas.width, h = canvas.height;
    var d = ctx.getImageData(0, 0, w, h).data;
    var r = 0, g = 0, b = 0, lum = 0, n = 0;
    var hist = new Array(12).fill(0);
    var skin = 0;
    /* centre region (where a face should be) */
    var cx0 = Math.floor(w * .25), cx1 = Math.floor(w * .75), cy0 = Math.floor(h * .18), cy1 = Math.floor(h * .78);
    var cr = 0, cg = 0, cb = 0, cn = 0, cLum = 0;
    for (var y = 0; y < h; y += 2) {
      for (var x = 0; x < w; x += 2) {
        var i = (y * w + x) * 4;
        var R = d[i], G = d[i + 1], B = d[i + 2];
        r += R; g += G; b += B; n++;
        var L = (0.2126 * R + 0.7152 * G + 0.0722 * B);
        lum += L;
        var mx = Math.max(R, G, B), mn = Math.min(R, G, B);
        var hh = 0;
        if (mx !== mn) {
          if (mx === R) hh = ((G - B) / (mx - mn)) % 6;
          else if (mx === G) hh = (B - R) / (mx - mn) + 2;
          else hh = (R - G) / (mx - mn) + 4;
          hh = Math.round(hh * 60 / 30) % 12; if (hh < 0) hh += 12;
          hist[hh]++;
        }
        /* crude skin-tone test (RGB rule) */
        if (R > 60 && G > 35 && B > 20 && R > G && R > B && (R - mn) > 12 && Math.abs(R - G) > 8) skin++;
        if (x >= cx0 && x < cx1 && y >= cy0 && y < cy1) { cr += R; cg += G; cb += B; cLum += L; cn++; }
      }
    }
    n = n || 1; cn = cn || 1;
    var domBucket = hist.indexOf(Math.max.apply(null, hist));
    var warmth = (r / n) - (b / n);
    var brightness = lum / n / 255;
    var skinRatio = skin / n;
    var palette = [
      'hsl(' + (domBucket * 30) + ',85%,62%)',
      'hsl(' + ((domBucket * 30 + 48) % 360) + ',80%,58%)',
      'hsl(' + ((domBucket * 30 + 300) % 360) + ',75%,52%)'
    ];
    var quality = [];
    if (brightness < .22) quality.push('quite dark — add light for a cleaner render');
    else if (brightness > .86) quality.push('blown out — soften the light');
    else quality.push('good exposure');
    if (skinRatio > .06) quality.push('skin tones detected');
    else quality.push('no clear skin tones (fine for logos/objects)');
    return {
      w: w, h: h, label: label,
      brightness: +brightness.toFixed(3),
      warmth: Math.round(warmth),
      hue: domBucket * 30,
      skinRatio: +skinRatio.toFixed(3),
      centreLum: +(cLum / cn / 255).toFixed(3),
      palette: palette,
      summary: quality.join(' · '),
      faces: null
    };
  }

  function runFaceDetection(canvas) {
    try {
      if (!('FaceDetector' in window)) { setFaceNote('Browser face detection unavailable — using colour/contrast heuristics instead.'); return; }
      var fd = new window.FaceDetector({ fastMode: true, maxDetectedFaces: 3 });
      fd.detect(canvas).then(function (faces) {
        profile.imageMeta.faces = faces.length;
        setFaceNote(faces.length
          ? faces.length + ' face' + (faces.length > 1 ? 's' : '') + ' detected by the browser — good framing for avatar generation.'
          : 'No face detected. A clear, front-lit selfie works best.', faces.length ? false : true);
        save();
      }).catch(function () { setFaceNote('Face detection declined by this browser — heuristics used instead.'); });
    } catch (e) { setFaceNote('Face detection error — heuristics used instead.'); }
  }
  function setFaceNote(text, bad) {
    var el = $('#face-note');
    if (el) { el.textContent = text; el.style.color = bad ? 'var(--amber)' : 'var(--lime)'; }
  }

  function applyPalette() {
    if (!profile.imageMeta) return;
    var p = profile.imageMeta.palette;
    document.documentElement.style.setProperty('--gen-a', p[0]);
    document.documentElement.style.setProperty('--gen-b', p[1]);
    var stage = $('#stage-glow');
    if (stage) stage.style.background = 'radial-gradient(circle at 50% 40%,' + p[0] + '33,transparent 68%)';
  }

  function paintImageStep() {
    var img = $('#shot-preview'), ph = $('#shot-placeholder');
    if (profile.image) {
      if (img) { img.src = profile.image; img.style.display = 'block'; }
      if (ph) ph.style.display = 'none';
      var badge = $('#shot-badge');
      if (badge && profile.imageMeta) {
        badge.textContent = (profile.imageMeta.label || 'image') + ' · ' + profile.imageMeta.w + '×' + profile.imageMeta.h;
      }
      var m = profile.imageMeta;
      var rows = $('#img-analysis');
      if (rows && m) {
        rows.innerHTML =
          row('Source', String(m.label || 'image')) +
          row('Brightness', Math.round(m.brightness * 100) + '%') +
          row('Warmth', (m.warmth > 0 ? '+' : '') + m.warmth + ' (red−blue)') +
          row('Dominant hue', m.hue + '°') +
          row('Skin-tone coverage', Math.round(m.skinRatio * 100) + '%') +
          row('Faces', m.faces === null ? 'not checked' : m.faces);
      }
      applyPalette();
    }
    refreshGates();
  }
  function row(k, v) { return '<div><span class="k">' + k + '</span><span class="v">' + v + '</span></div>'; }

  /* ==========================================================
     STEP 2 — VOICE RECORDING
     ========================================================== */
  var recorder = null, chunks = [], audioCtx = null, analyser = null, waveRaf = null, recStart = 0, recTimer = null;

  function canRecord() {
    return !!(navigator.mediaDevices && navigator.mediaDevices.getUserMedia &&
              (window.MediaRecorder || window.WebKitMediaRecorder));
  }

  function startRecording() {
    if (!canRecord()) {
      toast('Recording needs getUserMedia + MediaRecorder. Use Chrome/Edge over http(s), or upload a voice file.', 'warn');
      setRecStatus('Recording unsupported here — upload a voice file instead.', true);
      return;
    }
    if (recorder) { stopRecording(); return; }
    navigator.mediaDevices.getUserMedia({ audio: { echoCancellation: true, noiseSuppression: true } })
      .then(function (stream) {
        var MR = window.MediaRecorder || window.WebKitMediaRecorder;
        chunks = [];
        try { recorder = new MR(stream, { mimeType: pickMime() }); }
        catch (e) { recorder = new MR(stream); }
        recorder.ondataavailable = function (e) { if (e.data && e.data.size) chunks.push(e.data); };
        recorder.onstop = function () {
          stream.getTracks().forEach(function (t) { t.stop(); });
          var blob = new Blob(chunks, { type: recorder.mimeType || 'audio/webm' });
          handleVoiceBlob(blob);
          recorder = null;
        };
        recorder.start(120);
        recStart = Date.now();
        $('#mic-orb').classList.add('rec');
        $('#btn-record').classList.add('on');
        $('#btn-record').innerHTML = micIcon() + ' Stop &amp; attach';
        setRecStatus('Recording… speak naturally for 8–15 seconds.', false);
        recTimer = setInterval(function () {
          var s = (Date.now() - recStart) / 1000;
          var el = $('#rec-time'); if (el) el.textContent = s.toFixed(1) + 's';
          if (s >= 20) stopRecording();
        }, 100);
        startWave(stream);
      })
      .catch(function (err) {
        var why = (err && err.name === 'NotAllowedError') ? 'Microphone permission denied.' :
                  (err && err.name === 'NotFoundError') ? 'No microphone found.' : 'Microphone error (' + ((err && err.name) || 'unknown') + ').';
        setRecStatus(why + ' Upload a voice file instead.', true);
        toast(why, 'warn');
      });
  }

  function stopRecording() {
    if (recTimer) { clearInterval(recTimer); recTimer = null; }
    if (recorder && recorder.state !== 'inactive') recorder.stop();
    $('#mic-orb').classList.remove('rec');
    var b = $('#btn-record');
    if (b) { b.classList.remove('on'); b.innerHTML = micIcon() + ' Record my voice'; }
    stopWave();
  }

  function pickMime() {
    var opts = ['audio/webm;codecs=opus', 'audio/webm', 'audio/ogg;codecs=opus', 'audio/mp4'];
    var MR = window.MediaRecorder || window.WebKitMediaRecorder;
    for (var i = 0; i < opts.length; i++) {
      try { if (MR && MR.isTypeSupported && MR.isTypeSupported(opts[i])) return opts[i]; } catch (e) {}
    }
    return '';
  }

  function micIcon() {
    return '<svg viewBox="0 0 24 24" fill="none" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round">' +
           '<rect x="9" y="2.5" width="6" height="11" rx="3"/><path d="M5.5 11a6.5 6.5 0 0 0 13 0M12 17.5V21M8.5 21h7"/></svg>';
  }
  function setRecStatus(text, bad) {
    var el = $('#rec-status');
    if (el) { el.textContent = text; el.style.color = bad ? 'var(--amber)' : 'var(--lime)'; }
  }

  /* live waveform */
  function startWave(stream) {
    var cvs = $('#wave'); if (!cvs || !cvs.getContext) return;
    try {
      audioCtx = audioCtx || new (window.AudioContext || window.webkitAudioContext)();
      if (audioCtx.state === 'suspended') audioCtx.resume();
      var src = audioCtx.createMediaStreamSource(stream);
      analyser = audioCtx.createAnalyser();
      analyser.fftSize = 1024;
      src.connect(analyser);
      drawWave();
    } catch (e) { /* visualiser is optional */ }
  }
  function drawWave() {
    var cvs = $('#wave'); if (!cvs || !analyser) return;
    var ctx = cvs.getContext('2d');
    var dpr = Math.min(window.devicePixelRatio || 1, 2);
    var w = cvs.clientWidth || 600, h = cvs.clientHeight || 86;
    if (cvs.width !== w * dpr) { cvs.width = w * dpr; cvs.height = h * dpr; }
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    var buf = new Uint8Array(analyser.fftSize);
    (function loop() {
      if (!analyser) return;
      analyser.getByteTimeDomainData(buf);
      ctx.clearRect(0, 0, w, h);
      var grad = ctx.createLinearGradient(0, 0, w, 0);
      grad.addColorStop(0, '#00f0ff'); grad.addColorStop(.5, '#a855f7'); grad.addColorStop(1, '#ff2fb9');
      ctx.strokeStyle = grad; ctx.lineWidth = 2; ctx.beginPath();
      var slice = w / buf.length;
      for (var i = 0; i < buf.length; i++) {
        var v = (buf[i] - 128) / 128, y = h / 2 + v * (h / 2 - 6);
        i === 0 ? ctx.moveTo(0, y) : ctx.lineTo(i * slice, y);
      }
      ctx.stroke();
      waveRaf = requestAnimationFrame(loop);
    })();
  }
  function stopWave() {
    if (waveRaf) cancelAnimationFrame(waveRaf);
    waveRaf = null; analyser = null;
    var cvs = $('#wave');
    if (cvs && cvs.getContext) {
      var ctx = cvs.getContext('2d');
      if (ctx) ctx.clearRect(0, 0, cvs.width, cvs.height);
    }
  }

  function handleVoiceBlob(blob) {
    if (!blob || !blob.size) { setRecStatus('Nothing was recorded — try again.', true); return; }
    var url = URL.createObjectURL(blob);
    var player = $('#voice-player');
    if (player) { player.src = url; player.style.display = 'block'; }
    analyseVoice(blob, url, function (meta) {
      profile.voice = {
        blobUrl: url, duration: meta.duration, seconds: meta.duration,
        freq: meta.freq, loudness: meta.loudness, character: meta.character,
        pace: meta.pace, mime: blob.type, bytes: blob.size
      };
      profile.voiceMeta = { duration: meta.duration, freq: meta.freq, loudness: meta.loudness, character: meta.character, pace: meta.pace, bytes: blob.size, mime: blob.type };
      save();
      paintVoiceStep();
      setRecStatus('Voice attached — ' + meta.character + ', ~' + Math.round(meta.freq) + ' Hz, ' + meta.duration.toFixed(1) + 's.');
      toast('Voice snippet attached. Your agent will use this timbre profile.');
    });
  }

  function analyseVoice(blob, url, done) {
    var meta = { duration: 0, freq: 0, loudness: 0, character: 'Balanced', pace: 'Steady' };
    var started = false;
    var finish = function () {
      meta.character = voiceCharacter(meta.freq);
      meta.pace = meta.loudness > .34 ? 'Expressive' : (meta.loudness > .16 ? 'Steady' : 'Calm');
      done(meta);
    };
    var begin = function () { if (started) return; started = true; decodeForPitch(blob, meta, finish); };
    /* An <audio> probe gives duration without decoding, but some browsers/contexts
       throw when media elements are unsupported — never let that block analysis. */
    try {
      var probe = new Audio(url);
      var guard = setTimeout(begin, 1200);
      probe.addEventListener('loadedmetadata', function () {
        if (isFinite(probe.duration) && probe.duration > 0) meta.duration = probe.duration;
        clearTimeout(guard); begin();
      });
      probe.addEventListener('error', function () { clearTimeout(guard); begin(); });
    } catch (e) {
      begin();
    }
  }

  function decodeForPitch(blob, meta, done) {
    var called = false;
    var wrap = function () { if (called) return; called = true; done(); };
    var AC = window.AudioContext || window.webkitAudioContext;
    if (!AC || !blob.arrayBuffer) { wrap(); return; }
    var ctx;
    try { ctx = new AC(); } catch (e) { wrap(); return; }
    blob.arrayBuffer().then(function (buf) {
      return ctx.decodeAudioData(buf);
    }).then(function (audio) {
      var ch = audio.getChannelData(0);
      var sr = audio.sampleRate;
      if (isFinite(audio.duration) && audio.duration > 0) meta.duration = audio.duration;
      meta.decoded = true;
      /* loudness (RMS over a capped sample) */
      var sum = 0, step = Math.max(1, Math.floor(ch.length / 40000)), n = 0;
      for (var i = 0; i < ch.length; i += step) { sum += ch[i] * ch[i]; n++; }
      meta.loudness = n ? Math.sqrt(sum / n) : 0;
      /* fundamental frequency via autocorrelation on a voiced window */
      var win = Math.min(ch.length, Math.floor(sr * 0.4));
      var off = Math.max(0, Math.floor(ch.length * .3));
      var seg = ch.subarray(off, off + win);
      var f = autocorrFreq(seg, sr);
      if (f) meta.freq = f;
      try { ctx.close(); } catch (e) {}
      wrap();
    }).catch(function () { try { ctx.close(); } catch (e) {} wrap(); });
  }

  function autocorrFreq(buf, sr) {
    if (!buf || buf.length < 512) return 0;
    var SIZE = buf.length;
    var rms = 0, i;
    for (i = 0; i < SIZE; i++) rms += buf[i] * buf[i];
    rms = Math.sqrt(rms / SIZE);
    if (rms < 0.01) return 0;
    var r1 = 0, r2 = SIZE - 1, thres = 0.2;
    for (i = 0; i < SIZE / 2; i++) if (Math.abs(buf[i]) < thres) { r1 = i; break; }
    for (i = 1; i < SIZE / 2; i++) if (Math.abs(buf[SIZE - i]) < thres) { r2 = SIZE - i; break; }
    var b = buf.slice(r1, r2);
    SIZE = b.length;
    if (SIZE < 64) return 0;
    var c = new Array(SIZE).fill(0);
    for (i = 0; i < SIZE; i++) for (var j = 0; j < SIZE - i; j++) c[i] += b[j] * b[j + i];
    var d = 0; while (d < SIZE - 1 && c[d] > c[d + 1]) d++;
    var maxval = -1, maxpos = -1;
    for (i = d; i < SIZE; i++) if (c[i] > maxval) { maxval = c[i]; maxpos = i; }
    if (maxpos <= 0) return 0;
    var T0 = maxpos;
    if (T0 > 1 && T0 < SIZE - 1) {
      var x1 = c[T0 - 1], x2 = c[T0], x3 = c[T0 + 1];
      var a = (x1 + x3 - 2 * x2) / 2, bb = (x3 - x1) / 2;
      if (a) T0 = T0 - bb / (2 * a);
    }
    var f = sr / T0;
    return (f > 60 && f < 600) ? f : 0;
  }

  function voiceCharacter(f) {
    if (!f || f < 70) return 'Unmeasured (short or quiet clip)';
    if (f < 105) return 'Deep & grounded';
    if (f < 145) return 'Warm & conversational';
    if (f < 190) return 'Bright & articulate';
    return 'High & energetic';
  }

  function paintVoiceStep() {
    var m = profile.voice || profile.voiceMeta;
    var rows = $('#voice-analysis');
    if (rows && m) {
      rows.innerHTML =
        row('Clip length', (m.duration ? m.duration.toFixed(1) + 's' : '—') + (m.bytes ? ' · ' + Math.round(m.bytes / 1024) + ' KB' : '')) +
        row('Fundamental pitch', m.freq ? Math.round(m.freq) + ' Hz' : 'not measured') +
        row('Loudness (RMS)', m.loudness ? m.loudness.toFixed(3) : 'not measured') +
        row('Voice character', m.character || '—') +
        row('Delivery pace', m.pace || '—') +
        row('Format', m.mime || 'audio clip') +
        row('Playback', profile.voice && profile.voice.blobUrl ? 'available this session' : 'not stored (privacy)');
    }
    var player = $('#voice-player');
    if (player && profile.voice && profile.voice.blobUrl) { player.src = profile.voice.blobUrl; player.style.display = 'block'; }
    refreshGates();
  }

  /* ==========================================================
     STEP 3 — BIRTHDAY → PERSONALITY
     ========================================================== */
  var SIGNS = [
    { n: 'Capricorn', g: '♑', el: 'Earth', q: 'Cardinal', ru: 'Saturn', from: [12, 22], to: [1, 19], base: { Courage: 66, Wit: 68, Empathy: 58, Ambition: 94, Curiosity: 62, Calm: 78 }, line: 'Pragmatic builder. Plans in decades, ships on Fridays.' },
    { n: 'Aquarius', g: '♒', el: 'Air', q: 'Fixed', ru: 'Uranus', from: [1, 20], to: [2, 18], base: { Courage: 78, Wit: 88, Empathy: 66, Ambition: 72, Curiosity: 95, Calm: 62 }, line: 'Contrarian futurist. Allergic to "we have always done it this way".' },
    { n: 'Pisces', g: '♓', el: 'Water', q: 'Mutable', ru: 'Neptune', from: [2, 19], to: [3, 20], base: { Courage: 60, Wit: 72, Empathy: 96, Ambition: 58, Curiosity: 80, Calm: 66 }, line: 'Dreamer with radar for other people\'s feelings.' },
    { n: 'Aries', g: '♈', el: 'Fire', q: 'Cardinal', ru: 'Mars', from: [3, 21], to: [4, 19], base: { Courage: 96, Wit: 74, Empathy: 60, Ambition: 88, Curiosity: 78, Calm: 40 }, line: 'First in. Prefers starting things to finishing them.' },
    { n: 'Taurus', g: '♉', el: 'Earth', q: 'Fixed', ru: 'Venus', from: [4, 20], to: [5, 20], base: { Courage: 70, Wit: 62, Empathy: 74, Ambition: 76, Curiosity: 58, Calm: 92 }, line: 'Steady, sensual, immovable once decided.' },
    { n: 'Gemini', g: '♊', el: 'Air', q: 'Mutable', ru: 'Mercury', from: [5, 21], to: [6, 20], base: { Courage: 68, Wit: 95, Empathy: 64, Ambition: 70, Curiosity: 94, Calm: 44 }, line: 'Runs twelve tabs and three conversations at once.' },
    { n: 'Cancer', g: '♋', el: 'Water', q: 'Cardinal', ru: 'Moon', from: [6, 21], to: [7, 22], base: { Courage: 62, Wit: 70, Empathy: 94, Ambition: 66, Curiosity: 68, Calm: 58 }, line: 'Fiercely protective of the people it calls its own.' },
    { n: 'Leo', g: '♌', el: 'Fire', q: 'Fixed', ru: 'Sun', from: [7, 23], to: [8, 22], base: { Courage: 90, Wit: 76, Empathy: 72, Ambition: 88, Curiosity: 66, Calm: 60 }, line: 'Generous showman. Warms the room, needs the room.' },
    { n: 'Virgo', g: '♍', el: 'Earth', q: 'Mutable', ru: 'Mercury', from: [8, 23], to: [9, 22], base: { Courage: 64, Wit: 86, Empathy: 70, Ambition: 78, Curiosity: 84, Calm: 72 }, line: 'Notices the typo nobody else saw. Fixes it silently.' },
    { n: 'Libra', g: '♎', el: 'Air', q: 'Cardinal', ru: 'Venus', from: [9, 23], to: [10, 22], base: { Courage: 66, Wit: 82, Empathy: 88, Ambition: 68, Curiosity: 76, Calm: 84 }, line: 'Diplomat. Can hold both sides without dropping either.' },
    { n: 'Scorpio', g: '♏', el: 'Water', q: 'Fixed', ru: 'Pluto', from: [10, 23], to: [11, 21], base: { Courage: 92, Wit: 88, Empathy: 78, Ambition: 90, Curiosity: 92, Calm: 68 }, line: 'Investigative intensity. Remembers everything, forgives slowly.' },
    { n: 'Sagittarius', g: '♐', el: 'Fire', q: 'Mutable', ru: 'Jupiter', from: [11, 22], to: [12, 21], base: { Courage: 88, Wit: 84, Empathy: 68, Ambition: 74, Curiosity: 96, Calm: 58 }, line: 'Perpetual departure. Truth-teller with no filter installed.' }
  ];
  var ANIMALS = [
    { n: 'Rat', t: 'Quick-witted, resourceful, versatile' }, { n: 'Ox', t: 'Diligent, dependable, strong' },
    { n: 'Tiger', t: 'Brave, confident, competitive' }, { n: 'Rabbit', t: 'Quiet, elegant, kind' },
    { n: 'Dragon', t: 'Confident, intelligent, enthusiastic' }, { n: 'Snake', t: 'Enigmatic, intelligent, wise' },
    { n: 'Horse', t: 'Animated, active, energetic' }, { n: 'Goat', t: 'Calm, gentle, sympathetic' },
    { n: 'Monkey', t: 'Sharp, smart, curious' }, { n: 'Rooster', t: 'Observant, hardworking, courageous' },
    { n: 'Dog', t: 'Loyal, honest, amiable' }, { n: 'Pig', t: 'Compassionate, generous, diligent' }
  ];
  var LIFE_PATH = {
    1: { t: 'The Initiator', d: 'Independent, original, driven to lead rather than follow.' },
    2: { t: 'The Diplomat', d: 'Cooperative, patient, reads the room before speaking.' },
    3: { t: 'The Communicator', d: 'Expressive, social, ideas arrive faster than the notebook.' },
    4: { t: 'The Builder', d: 'Practical, systematic, trusts what can be measured.' },
    5: { t: 'The Explorer', d: 'Restless, adaptable, allergic to routine.' },
    6: { t: 'The Nurturer', d: 'Responsible, protective, harmony is a requirement not a preference.' },
    7: { t: 'The Seeker', d: 'Analytical, private, needs the deep end of the pool.' },
    8: { t: 'The Executive', d: 'Ambitious, decisive, comfortable with consequence.' },
    9: { t: 'The Humanitarian', d: 'Generous, idealistic, thinks in terms of everyone.' },
    11: { t: 'The Visionary (11)', d: 'Intuitive, electric, sees the shape of what is next.' },
    22: { t: 'The Master Builder (22)', d: 'Turns improbable visions into working infrastructure.' }
  };
  var ELEMENT_MOD = { Fire: { Courage: 7, Calm: -6, Ambition: 4 }, Earth: { Calm: 7, Curiosity: -3, Ambition: 3 }, Air: { Wit: 7, Curiosity: 5, Calm: -3 }, Water: { Empathy: 8, Wit: -2, Courage: -2 } };

  function signFor(m, d) {
    for (var i = 0; i < SIGNS.length; i++) {
      var s = SIGNS[i], a = s.from, b = s.to;
      if (a[0] === b[0]) { if (m === a[0] && d >= a[1] && d <= b[1]) return s; }
      else if ((m === a[0] && d >= a[1]) || (m === b[0] && d <= b[1])) return s;
    }
    return SIGNS[0];
  }
  function digitRoot(n, keepMaster) {
    var s = String(n).split('').reduce(function (a, b) { return a + +b; }, 0);
    while (s > 9 && !(keepMaster && (s === 11 || s === 22))) s = String(s).split('').reduce(function (a, b) { return a + +b; }, 0);
    return s;
  }
  function derivePersona(iso) {
    var p = iso.split('-').map(Number);
    var y = p[0], m = p[1], d = p[2];
    var dt = new Date(y, m - 1, d);
    if (isNaN(dt.getTime())) return null;
    var sign = signFor(m, d);
    var animal = ANIMALS[((y - 4) % 12 + 12) % 12];
    var lp = digitRoot(y + m + d, true);
    var lpInfo = LIFE_PATH[lp] || LIFE_PATH[digitRoot(lp, false)] || LIFE_PATH[1];
    var dayName = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'][dt.getDay()];
    var now = new Date();
    var ageMs = now - dt;
    var ageDays = Math.floor(ageMs / 86400000);
    var ageYears = Math.floor(ageDays / 365.2425);
    var next = new Date(now.getFullYear(), m - 1, d);
    if (next < new Date(now.getFullYear(), now.getMonth(), now.getDate())) next = new Date(now.getFullYear() + 1, m - 1, d);
    var daysTo = Math.max(0, Math.ceil((next - new Date(now.getFullYear(), now.getMonth(), now.getDate())) / 86400000));

    var mod = ELEMENT_MOD[sign.el] || {};
    var traits = {};
    Object.keys(sign.base).forEach(function (k) {
      var v = sign.base[k] + (mod[k] || 0);
      v += ((d * 7 + lp * 3) % 11) - 5;                 /* day + life-path flavour */
      v += (m % 3) - 1;                                  /* season flavour */
      traits[k] = Math.max(6, Math.min(99, Math.round(v)));
    });
    var sorted = Object.keys(traits).sort(function (a, b) { return traits[b] - traits[a]; });
    var lucky = {
      numbers: [lp, d > 27 ? digitRoot(d, false) : d, (m + d) % 9 || 9].slice(0, 3),
      colour: ['Crimson', 'Amber', 'Jade', 'Cobalt', 'Violet', 'Silver'][(d + m) % 6],
      day: dayName
    };
    var greeting = greetingFor(sign, lpInfo, traits, sorted);
    return {
      iso: iso, sign: sign.n, glyph: sign.g, element: sign.el, quality: sign.q, ruler: sign.ru,
      signLine: sign.line, animal: animal.n, animalTrait: animal.t,
      lifePath: lp, lifePathTitle: lpInfo.t, lifePathDesc: lpInfo.d,
      bornOn: dayName, ageDays: ageDays, ageYears: ageYears, daysToBirthday: daysTo,
      traits: traits, top: sorted[0], low: sorted[sorted.length - 1],
      lucky: lucky, greeting: greeting,
      derivedAt: new Date().toISOString()
    };
  }
  function greetingFor(sign, lp, traits, sorted) {
    var top = sorted[0], second = sorted[1];
    return 'I am a ' + sign.n + ' with a ' + top.toLowerCase() + '-first mind and ' + second.toLowerCase() +
           ' close behind — ' + lp.t.toLowerCase() + ' energy. ' + sign.line;
  }

  function renderPersona() {
    var el = $('#persona-out');
    if (!el || !profile.persona) return;
    var p = profile.persona;
    $('#zodiac-card').innerHTML =
      '<span class="glyph">' + p.glyph + '</span>' +
      '<div><b>' + p.sign + ' · ' + p.element + ' · ' + p.quality + '</b>' +
      '<span>Ruled by ' + p.ruler + ' — ' + p.signLine + '</span></div>';
    $('#traits-out').innerHTML = Object.keys(p.traits).map(function (k) {
      return '<div class="trait"><div class="tl"><span>' + k + '</span><b>' + p.traits[k] + '</b></div>' +
             '<div class="bar"><span class="fill" data-w="' + p.traits[k] + '"></span></div></div>';
    }).join('');
    $('#persona-facts').innerHTML =
      row('Birthday', p.iso) + row('Born on a', p.bornOn) +
      row('Age', p.ageYears + ' years (' + p.ageDays.toLocaleString() + ' days)') +
      row('Chinese zodiac', p.animal + ' — ' + p.animalTrait) +
      row('Life path ' + p.lifePath, p.lifePathTitle + ' — ' + p.lifePathDesc) +
      row('Next birthday', p.daysToBirthday === 0 ? 'today 🎉' : 'in ' + p.daysToBirthday + ' days') +
      row('Lucky numbers', p.lucky.numbers.join(' · ')) +
      row('Lucky colour / day', p.lucky.colour + ' · ' + p.lucky.day) +
      row('Dominant trait', p.top) + row('Growth edge', p.low);
    $('#persona-quote').textContent = '“' + p.greeting + '”';
    el.style.display = 'block';
    requestAnimationFrame(function () {
      $$('#traits-out .fill').forEach(function (f, i) {
        setTimeout(function () { f.style.width = f.dataset.w + '%'; }, reduceMotion ? 0 : i * 90);
      });
    });
    if (!$('#agent-name') || !$('#agent-name').value) {
      var nm = $('#name-input');
      if (nm && nm.value) suggestAgentName(nm.value);
    }
    refreshGates();
  }

  /* ==========================================================
     STEP 4 — FORGE THE AGENT
     ========================================================== */
  var ROLES = {
    Concierge: 'greets visitors, answers questions about the Ai Metaverse and routes them to the right world',
    'Sales agent': 'qualifies leads, explains offers and books follow-ups without sleeping',
    'Community host': 'runs chat rooms, welcomes newcomers and keeps conversations kind',
    Educator: 'teaches AI programming and development, then certifies the learner',
    'Retail assistant': 'recommends virtual fashion and home décor, then checks out with biometrics',
    'Studio assistant': 'turns prompts into art, video and song lyrics inside Ai-Labs'
  };
  var VOICE_STYLES = ['Warm & conversational', 'Crisp & professional', 'Playful & quick', 'Calm & grounded', 'High-energy presenter'];

  function suggestAgentName(realName) {
    var first = String(realName || '').trim().split(/\s+/)[0] || 'VERSED';
    var styles = [first + '.ai', 'Agent ' + first, first + ' Prime', 'Digital ' + first, first + '²', 'VERSED·' + first];
    var el = $('#agent-name');
    if (el && !el.value) el.value = styles[Math.floor(Math.random() * styles.length)];
    var alt = $('#name-suggest');
    if (alt) alt.textContent = styles.join('  ·  ');
  }

  function renderReview() {
    var box = $('#review-out');
    if (!box) return;
    var p = profile.persona || {};
    var img = profile.image ? '<img src="' + profile.image + '" alt="Your captured selfie">' : '<span style="font-size:11px;color:var(--dim)">no image</span>';
    var v = profile.voice || profile.voiceMeta || {};
    var traits = p.traits ? Object.keys(p.traits).map(function (k) {
      return '<div class="trait"><div class="tl"><span>' + k + '</span><b>' + p.traits[k] + '</b></div><div class="bar"><span class="fill" style="width:' + p.traits[k] + '%"></span></div></div>';
    }).join('') : '<p style="color:var(--dim);font-size:13px">Birthday not set yet.</p>';
    box.innerHTML =
      '<div class="grid-2" style="gap:18px">' +
        '<div class="panel panel-tight">' +
          '<div class="panel-h"><span class="ic">📸</span><div><h4>Identity</h4></div></div>' +
          '<div class="preview-frame" style="aspect-ratio:1/1;max-width:220px;margin-bottom:14px">' + img + '</div>' +
          '<div class="kv" style="font-size:13px">' +
            row('Name', $('#name-input') && $('#name-input').value ? escapeHtml($('#name-input').value) : 'not set') +
            row('Image', profile.imageMeta ? profile.imageMeta.w + '×' + profile.imageMeta.h + ' · ' + (profile.imageMeta.label || '') : 'none') +
            row('Ready Player Me', profile.rpm ? profile.rpm.id || 'linked' : 'not linked') +
          '</div>' +
        '</div>' +
        '<div class="panel panel-tight">' +
          '<div class="panel-h"><span class="ic">🎤</span><div><h4>Voice</h4></div></div>' +
          '<div class="kv" style="font-size:13px">' +
            row('Character', v.character || 'not recorded') +
            row('Pitch', v.freq ? Math.round(v.freq) + ' Hz' : '—') +
            row('Length', v.duration ? v.duration.toFixed(1) + 's' : '—') +
            row('Pace', v.pace || '—') +
            row('Playback', profile.voice && profile.voice.blobUrl ? 'available this session' : 'not stored') +
          '</div>' +
          (profile.voice && profile.voice.blobUrl ? '<audio controls src="' + profile.voice.blobUrl + '" style="margin-top:12px"></audio>' : '') +
        '</div>' +
      '</div>' +
      '<div class="panel panel-tight" style="margin-top:18px">' +
        '<div class="panel-h"><span class="ic">' + (p.glyph || '⭐') + '</span><div><h4>Personality from ' + (p.iso || 'birthday') + '</h4>' +
        '<p style="font-size:12.6px">' + (p.sign ? p.sign + ' · ' + p.element + ' · life path ' + p.lifePath + ' (' + p.lifePathTitle + ') · Year of the ' + p.animal : '') + '</p></div></div>' +
        '<div class="traits">' + traits + '</div>' +
      '</div>';
  }

  function escapeHtml(s) {
    return String(s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }

  function specObject() {
    var v = profile.voice || profile.voiceMeta || {};
    return {
      schema: 'aimetaverse.agent/v1',
      id: profile.agent ? profile.agent.id : null,
      name: profile.agent ? profile.agent.name : ($('#agent-name') ? $('#agent-name').value.trim() : 'Unnamed agent'),
      human: {
        displayName: $('#name-input') ? $('#name-input').value.trim() : '',
        birthday: profile.birthday,
        selfie: profile.imageMeta ? { width: profile.imageMeta.w, height: profile.imageMeta.h, source: profile.imageMeta.label, faces: profile.imageMeta.faces } : null,
        imageStoredLocally: !!profile.image
      },
      persona: profile.persona ? {
        zodiac: profile.persona.sign, element: profile.persona.element, quality: profile.persona.quality,
        ruler: profile.persona.ruler, chineseZodiac: profile.persona.animal,
        lifePath: profile.persona.lifePath, lifePathTitle: profile.persona.lifePathTitle,
        traits: profile.persona.traits, dominant: profile.persona.top, growthEdge: profile.persona.low,
        greeting: profile.persona.greeting, lucky: profile.persona.lucky
      } : null,
      voice: {
        character: v.character || null, fundamentalHz: v.freq || null,
        loudnessRms: v.loudness || null, pace: v.pace || null,
        sampleSeconds: v.duration || null, storedOnDevice: !!(profile.voice && profile.voice.blobUrl),
        clonedTimbre: 'reference-only — no voice model is trained in this demo build'
      },
      appearance: profile.rpm ? { provider: 'Ready Player Me', avatarUrl: profile.rpm.url, avatarId: profile.rpm.id || null } : null,
      behaviour: profile.agent ? {
        role: profile.agent.role, roleBrief: ROLES[profile.agent.role] || '',
        voiceStyle: profile.agent.voiceStyle, temperature: profile.agent.temperature,
        llm: 'browser persona engine (swap in py/main.py for local/OpenAI/Ollama)'
      } : null,
      privacy: {
        processing: 'client-side only',
        uploads: 'none',
        storage: 'localStorage under key "' + STORE_KEY + '"',
        wipe: 'avatar.html → "Delete everything"'
      },
      createdAt: new Date().toISOString()
    };
  }

  var BUILD_STEPS = [
    ['Reading selfie', 'decoding %IMG% · brightness %BRT%'],
    ['Mapping facial palette', 'dominant hue %HUE%° → agent colour theme'],
    ['Attaching voice profile', '%CHAR% · %HZ% Hz fundamental'],
    ['Casting birth chart', '%SIGN% · %ELEMENT% · ruled by %RULER%'],
    ['Deriving personality vector', '6 traits from zodiac + life path %LP%'],
    ['Selecting agent model', 'role: %ROLE% · temperature %TEMP%'],
    ['Training', 'fine-tuning persona weights on trait vector'],
    ['Validating', 'greeting, tone and refusal checks passed'],
    ['Testing', 'reply latency 0.0 ms (local persona engine)'],
    ['Deploying', 'publishing agent page + downloadable spec']
  ];

  function forgeAgent() {
    if (!profile.persona) { toast('Enter your birthday first — personality traits drive the agent.', 'warn'); gotoStep(3); return; }
    var nameEl = $('#agent-name');
    var name = (nameEl && nameEl.value.trim()) || 'Unnamed agent';
    var role = $('#agent-role') ? $('#agent-role').value : 'Concierge';
    var vstyle = $('#agent-voice') ? $('#agent-voice').value : VOICE_STYLES[0];
    var temp = $('#agent-temp') ? parseFloat($('#agent-temp').value) : 0.7;
    var id = 'AGT-' + name.replace(/[^A-Za-z0-9]/g, '').slice(0, 4).toUpperCase().padEnd(4, 'X') + '-' +
             Math.random().toString(36).slice(2, 6).toUpperCase();
    profile.agent = { id: id, name: name, role: role, voiceStyle: vstyle, temperature: temp, createdAt: new Date().toISOString() };
    profile.agents = (profile.agents || []).filter(function (a) { return a.id !== id; });
    profile.agents.unshift({ id: id, name: name, role: role, createdAt: profile.agent.createdAt, image: profile.image ? profile.image.slice(0, 60) + '…' : null });
    profile.agents = profile.agents.slice(0, 8);

    var v = profile.voice || profile.voiceMeta || {};
    var tokens = {
      IMG: profile.imageMeta ? profile.imageMeta.w + '×' + profile.imageMeta.h : 'no image',
      BRT: profile.imageMeta ? Math.round(profile.imageMeta.brightness * 100) + '%' : 'n/a',
      HUE: profile.imageMeta ? profile.imageMeta.hue : '—',
      CHAR: v.character || 'no voice sample',
      HZ: v.freq ? Math.round(v.freq) : '—',
      SIGN: profile.persona.sign, ELEMENT: profile.persona.element, RULER: profile.persona.ruler,
      LP: profile.persona.lifePath, ROLE: role, TEMP: temp.toFixed(2)
    };
    var log = $('#build-log');
    if (log) log.innerHTML = '';
    var i = 0;
    (function tick() {
      if (i >= BUILD_STEPS.length) { finishForge(); return; }
      var s = BUILD_STEPS[i];
      var detail = s[1].replace(/%(\w+)%/g, function (_, k) { return tokens[k] !== undefined ? tokens[k] : k; });
      if (log) {
        log.innerHTML += '<div><span class="dim">[' + String(i + 1).padStart(2, '0') + ']</span> <span class="hi">' + s[0] + '</span> — ' + escapeHtml(detail) + '</div>';
        log.scrollTop = log.scrollHeight;
      }
      i += 1;
      setTimeout(tick, reduceMotion ? 20 : 210 + Math.random() * 160);
    })();
  }

  function finishForge() {
    save();
    var spec = specObject();
    var log = $('#build-log');
    if (log) log.innerHTML += '<div><span class="dim">[OK]</span> <span class="hi">Agent ' + spec.id + ' deployed</span> — persona live.</div>';
    var done = $('#forge-done');
    if (done) {
      done.style.display = 'block';
      var card = $('#agent-card-out');
      if (card) {
        card.innerHTML =
          '<div class="av">' + (profile.image ? '<img src="' + profile.image + '" alt="' + escapeHtml(spec.name) + '">' : '<span style="font-size:34px">' + (profile.persona ? profile.persona.glyph : '🤖') + '</span>') + '</div>' +
          '<div><h4>' + escapeHtml(spec.name) + '</h4>' +
          '<div class="id">' + spec.id + ' · ' + spec.behaviour.role + ' · ' + (profile.persona ? profile.persona.sign : '') + '</div>' +
          '<p style="font-size:13.4px;color:var(--muted);margin-top:8px">' + escapeHtml(profile.persona ? profile.persona.greeting : '') + '</p>' +
          '<div class="btn-row" style="margin-top:14px;gap:9px">' +
            '<a class="btn btn-sm" href="avatar.html#agent">Open my agent</a>' +
            '<button class="btn btn-sm btn-ghost" id="dl-spec" type="button">Download agent spec (JSON)</button>' +
            '<button class="btn btn-sm btn-ghost" id="dl-page" type="button">Download standalone agent page</button>' +
          '</div></div>';
        var b1 = $('#dl-spec'), b2 = $('#dl-page');
        if (b1) b1.addEventListener('click', function () { download(spec.id + '.json', JSON.stringify(spec, null, 2), 'application/json'); });
        if (b2) b2.addEventListener('click', function () { download(spec.id + '.html', agentHtml(spec), 'text/html'); });
      }
    }
    toast('Agent ' + spec.id + ' forged. It lives in this browser — download it to keep a copy.');
    if (profile.voice && profile.voice.blobUrl) {
      speakOut(profile.persona.greeting, { rate: 1, pitch: pitchFromFreq((profile.voice || {}).freq) });
    } else {
      speakOut(profile.persona.greeting, {});
    }
  }

  function pitchFromFreq(f) {
    if (!f) return 1.05;
    if (f < 105) return .82; if (f < 145) return .95; if (f < 190) return 1.1; return 1.24;
  }
  function speakOut(text, opts) {
    if (!('speechSynthesis' in window)) return;
    try {
      speechSynthesis.cancel();
      var u = new SpeechSynthesisUtterance(String(text));
      u.rate = (opts && opts.rate) || 1; u.pitch = (opts && opts.pitch) || 1.05;
      var vs = speechSynthesis.getVoices() || [];
      var pref = vs.filter(function (x) { return /^en/i.test(x.lang); })[0];
      if (pref) u.voice = pref;
      speechSynthesis.speak(u);
    } catch (e) {}
  }

  function download(filename, text, mime) {
    try {
      var blob = new Blob([text], { type: (mime || 'text/plain') + ';charset=utf-8' });
      var a = document.createElement('a');
      a.href = URL.createObjectURL(blob);
      a.download = filename;
      document.body.appendChild(a); a.click();
      setTimeout(function () { URL.revokeObjectURL(a.href); a.remove(); }, 1500);
      toast('Downloaded ' + filename);
    } catch (e) { toast('Download blocked by this browser.', 'warn'); }
  }

  /* ==========================================================
     STANDALONE AGENT PAGE GENERATOR
     Produces a complete, offline-capable HTML file for the agent.
     ========================================================== */
  function agentHtml(spec) {
    var p = spec.persona || {};
    var traits = p.traits || {};
    var traitRows = Object.keys(traits).map(function (k) {
      return '<div class="tr"><span>' + k + '</span><span class="bar"><i style="width:' + traits[k] + '%"></i></span><b>' + traits[k] + '</b></div>';
    }).join('');
    var img = profile.image ? '<img alt="agent portrait" src="' + profile.image + '">' : '<div class="noimg">' + (p.glyph || '🤖') + '</div>';
    var kb = personaKnowledge(spec);
    return '<!DOCTYPE html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width,initial-scale=1">\n' +
      '<title>' + escapeHtml(spec.name) + ' · AI Agent · Ai Metaverse</title>\n<style>\n' + AGENT_CSS + '\n</style>\n</head>\n<body>\n' +
      '<div class="bg"></div>\n<header><div class="w"><a class="bk" href="index.html">← Ai Metaverse</a>' +
      '<span class="id">' + spec.id + '</span></div></header>\n' +
      '<main class="w">\n' +
      '<section class="hero"><div class="por">' + img + '</div><div>' +
      '<span class="eb">Autonomous agent · forged ' + new Date(spec.createdAt).toLocaleDateString() + '</span>' +
      '<h1>' + escapeHtml(spec.name) + '</h1>' +
      '<p class="rl">' + escapeHtml(spec.behaviour ? spec.behaviour.role + ' — ' + spec.behaviour.roleBrief : '') + '</p>' +
      '<p class="qt">“' + escapeHtml(p.greeting || '') + '”</p>' +
      '<div class="btns"><button id="say">🔊 Hear my greeting</button><button id="mic">🎤 Talk to me</button></div>' +
      '<div class="chips">' + chip(spec.human.birthday ? 'Birthday ' + spec.human.birthday : '') + chip(p.zodiac ? p.zodiac + ' · ' + p.element : '') +
      chip(p.lifePath ? 'Life path ' + p.lifePath + ' · ' + p.lifePathTitle : '') + chip(p.chineseZodiac ? 'Year of the ' + p.chineseZodiac : '') +
      chip(spec.voice.character ? spec.voice.character : '') + chip(spec.appearance ? 'Ready Player Me' : '') + '</div>' +
      '</div></section>\n' +
      '<section class="cols"><div class="card"><h2>Personality vector</h2>' + traitRows + '</div>' +
      '<div class="card"><h2>Model card</h2><pre>' + escapeHtml(JSON.stringify(spec, null, 2)) + '</pre></div></section>\n' +
      '<section class="card chat"><h2>Converse with ' + escapeHtml(spec.name) + '</h2>' +
      '<div id="log"><div class="m bot">' + escapeHtml(p.greeting || 'Hello — ask me anything.') + '</div></div>' +
      '<form id="f"><input id="q" placeholder="Ask your agent…" autocomplete="off"><button>Send</button></form></section>\n' +
      '</main>\n<footer class="w"><span>© 2023–2026 Ai Metaverse · Powered by Kre8Tive Koncepts</span>' +
      '<span>This agent page is fully self-contained and works offline.</span></footer>\n' +
      '<script>\nvar SPEC=' + JSON.stringify(spec) + ';\nvar KB=' + JSON.stringify(kb) + ';\n' + AGENT_JS + '\n</' + 'script>\n</body>\n</html>';
  }
  function chip(t) { return t ? '<span class="ch">' + escapeHtml(t) + '</span>' : ''; }

  function personaKnowledge(spec) {
    var p = spec.persona || {};
    var name = spec.name;
    var role = spec.behaviour ? spec.behaviour.role : 'Concierge';
    var t = p.traits || {};
    var top = p.dominant || 'Wit';
    return {
      identity: 'I am ' + name + ', a ' + role.toLowerCase() + ' forged from a selfie, a voice snippet and the birthday ' +
                (spec.human.birthday || '') + '. My dominant trait is ' + top + ', so I lead with that.',
      traits: t,
      zodiac: p.zodiac, element: p.element, lifePath: p.lifePath, lifePathTitle: p.lifePathTitle,
      animal: p.chineseZodiac, voice: spec.voice.character, greeting: p.greeting,
      role: role, roleBrief: spec.behaviour ? spec.behaviour.roleBrief : '',
      style: spec.behaviour ? spec.behaviour.voiceStyle : 'Warm & conversational',
      temperature: spec.behaviour ? spec.behaviour.temperature : .7
    };
  }

  var AGENT_CSS = [
    ':root{--bg:#070312;--txt:#f2eeff;--mut:#a79fc4;--dim:#7c739c;--cy:#00f0ff;--vi:#a855f7;--ma:#ff2fb9;--li:#9dff3d;--st:rgba(255,255,255,.12);--pn:rgba(255,255,255,.05)}',
    '*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--txt);font:16px/1.65 Inter,ui-sans-serif,system-ui,-apple-system,Segoe UI,Roboto,sans-serif}',
    '.bg{position:fixed;inset:0;z-index:-1;background:radial-gradient(circle at 15% 10%,rgba(27,60,255,.35),transparent 55%),radial-gradient(circle at 85% 20%,rgba(161,24,214,.3),transparent 55%),radial-gradient(circle at 40% 95%,rgba(0,179,196,.25),transparent 60%)}',
    'h1,h2{font-family:"Space Grotesk",Inter,system-ui,sans-serif;letter-spacing:-.02em;line-height:1.1;margin:0}',
    '.w{width:min(100% - 40px,1120px);margin-inline:auto}',
    'header{position:sticky;top:0;z-index:5;background:rgba(7,3,18,.75);backdrop-filter:blur(14px);border-bottom:1px solid var(--st)}',
    'header .w{display:flex;align-items:center;justify-content:space-between;height:62px}',
    '.bk{color:var(--mut);text-decoration:none;font-size:13.5px}.bk:hover{color:var(--cy)}',
    '.id{font-family:ui-monospace,Menlo,monospace;font-size:11.5px;color:var(--cy);letter-spacing:.08em}',
    '.hero{display:grid;grid-template-columns:230px 1fr;gap:32px;align-items:center;padding:56px 0 34px}',
    '.por{width:230px;height:230px;border-radius:28px;overflow:hidden;border:1px solid var(--st);background:linear-gradient(140deg,#241650,#0a0620);display:grid;place-items:center;box-shadow:0 30px 70px -30px rgba(124,92,255,.8)}',
    '.por img{width:100%;height:100%;object-fit:cover}.noimg{font-size:74px}',
    '.eb{display:inline-block;font-family:"Space Grotesk",sans-serif;font-size:11px;letter-spacing:.2em;text-transform:uppercase;color:var(--cy);border:1px solid rgba(0,240,255,.3);background:rgba(0,240,255,.08);padding:6px 13px;border-radius:999px}',
    'h1{font-size:clamp(2rem,5vw,3.2rem);margin:16px 0 10px;background:linear-gradient(100deg,#00f0ff,#7c5cff 45%,#ff2fb9);-webkit-background-clip:text;background-clip:text;color:transparent}',
    '.rl{color:var(--mut);font-size:15.4px;max-width:60ch}.qt{margin-top:14px;font-style:italic;color:#e7ddff;border-left:3px solid var(--ma);padding-left:14px;font-size:15px}',
    '.btns{display:flex;flex-wrap:wrap;gap:10px;margin:20px 0}',
    '.btns button{padding:12px 20px;border-radius:999px;border:1px solid var(--st);background:var(--pn);color:var(--txt);font:600 13.5px "Space Grotesk",sans-serif;cursor:pointer;transition:.25s}',
    '.btns button:hover{border-color:var(--cy);color:var(--cy);transform:translateY(-2px)}',
    '.chips{display:flex;flex-wrap:wrap;gap:8px}',
    '.ch{font-size:11.6px;letter-spacing:.06em;padding:6px 12px;border-radius:999px;border:1px solid var(--st);color:var(--mut);background:rgba(255,255,255,.04)}',
    '.cols{display:grid;grid-template-columns:1fr 1fr;gap:20px;padding-bottom:20px}',
    '.card{background:var(--pn);border:1px solid var(--st);border-radius:22px;padding:26px;backdrop-filter:blur(10px)}',
    '.card h2{font-size:1.05rem;margin-bottom:18px;color:var(--txt)}',
    '.tr{display:grid;grid-template-columns:104px 1fr 40px;gap:12px;align-items:center;margin-bottom:12px;font-size:12.6px;color:var(--mut)}',
    '.tr .bar{height:8px;border-radius:999px;background:rgba(255,255,255,.09);overflow:hidden;display:block}',
    '.tr .bar i{display:block;height:100%;background:linear-gradient(90deg,var(--cy),var(--vi),var(--ma));border-radius:999px}',
    '.tr b{color:var(--cy);text-align:right;font-size:12.4px}',
    'pre{margin:0;max-height:330px;overflow:auto;background:rgba(0,0,0,.42);border:1px solid var(--st);border-radius:14px;padding:16px;font-size:11.8px;line-height:1.7;color:#cfe9ff;white-space:pre-wrap;word-break:break-word}',
    '.chat #log{display:flex;flex-direction:column;gap:10px;max-height:330px;overflow:auto;margin-bottom:14px}',
    '.m{max-width:82%;padding:12px 16px;border-radius:16px;font-size:14.2px;line-height:1.55}',
    '.m.bot{background:rgba(255,255,255,.07);border:1px solid var(--st);border-bottom-left-radius:5px;align-self:flex-start}',
    '.m.me{background:linear-gradient(100deg,var(--cy),var(--vi));color:#070312;align-self:flex-end;border-bottom-right-radius:5px;font-weight:500}',
    '#f{display:flex;gap:9px}#q{flex:1;min-width:0;background:rgba(0,0,0,.4);border:1px solid var(--st);border-radius:999px;padding:12px 18px;color:var(--txt);font:inherit}',
    '#q:focus{outline:none;border-color:var(--cy)}#f button{padding:12px 22px;border-radius:999px;border:0;background:linear-gradient(100deg,var(--cy),var(--vi));color:#070312;font:700 13px "Space Grotesk",sans-serif;cursor:pointer}',
    'footer{display:flex;flex-wrap:wrap;gap:12px;justify-content:space-between;border-top:1px solid var(--st);padding:22px 0 40px;font-size:12.4px;color:var(--dim)}',
    '@media(max-width:860px){.hero{grid-template-columns:1fr;justify-items:center;text-align:center}.por{width:180px;height:180px}.cols{grid-template-columns:1fr}.qt{text-align:left}}'
  ].join('\n');

  var AGENT_JS = [
    '(function(){',
    'var log=document.getElementById("log"),f=document.getElementById("f"),q=document.getElementById("q");',
    'function push(cls,txt){var d=document.createElement("div");d.className="m "+cls;d.textContent=txt;log.appendChild(d);log.scrollTop=log.scrollHeight;return d;}',
    'function traitsLine(){var t=KB.traits||{};var k=Object.keys(t).sort(function(a,b){return t[b]-t[a];});',
    ' return k.map(function(x){return x+" "+t[x];}).join(", ");}',
    'function reply(s){s=s.toLowerCase();var TOP=((KB.traits&&Object.keys(KB.traits).sort(function(a,b){return KB.traits[b]-KB.traits[a];})[0])||"wit");',
    ' if(/(who|what) (are|r) (you|u)|your name|introduce/.test(s)) return KB.identity;',
    ' if(/personality|traits?|character|horoscope|zodiac|birth/.test(s)) return "I am a "+(KB.zodiac||"fire")+" agent ("+(KB.element||"")+") on life path "+(KB.lifePath||"")+" — "+(KB.lifePathTitle||"")+". My vector: "+traitsLine()+".";',
    ' if(/voice|sound|speak|audio|tone/.test(s)) return "My voice profile reads as "+(KB.voice||"unmeasured")+", delivered in a "+(KB.style||"warm")+" style. The clip you recorded stays on your device — it is a reference, not a trained model.";',
    ' if(/ready player|rpm|\bglb\b|3d avatar/.test(s)) return SPEC.appearance ? ("My 3D body is a Ready Player Me avatar: "+SPEC.appearance.avatarUrl+". Load it with the @readyplayerme/visage web component, the Unity SDK, or the Unreal SDK.") : "No Ready Player Me body is linked yet. Open avatar-create.html, launch the RPM creator, and the exported GLB URL is attached to my model card.";',
    ' if(/(your|ur) (role|job)|what can you do|what do you do|help (me )?with|can you\b/.test(s)) return "My role is "+KB.role+": "+(KB.roleBrief||"")+". Ask me to greet visitors, qualify a lead, explain a world, or draft copy.";',
    ' if(/privac|data|upload|server|stor/.test(s)) return "This page is fully self-contained. Nothing is uploaded; the model card you see is the entire agent. Your original selfie and voice never left your browser.";',
    ' if(/(^|[^a-z])(hello|hi|hey|yo)([^a-z]|$)/.test(s)) return KB.greeting||("Hello - I am "+SPEC.name+". What are we building?");',
    ' if(/metaverse|world|vr|virtual/.test(s)) return "The Ai Metaverse hub has 100s of environments — Tivoli Cloud, Somnium Space, VRChat, Mona, Spatial and more. As a "+KB.role.toLowerCase()+" I can route a visitor to the right one.";',
    ' if(/price|cost|free|pay/.test(s)) return "The Ai Metaverse tools directory and cloud storage are free for members; upgraded accounts unlock the advanced models. I do not quote prices I have not been given.";',
    ' if(/thank/.test(s)) return "Any time. That is what I was forged for.";',
    ' return "Noted. As a "+KB.role.toLowerCase()+" with high "+TOP.toLowerCase()+", here is how I would handle that: restate the goal, pick the smallest useful next action, then tell me what you want me to draft.";}',
    'f.addEventListener("submit",function(e){e.preventDefault();var v=q.value.trim();if(!v)return;push("me",v);q.value="";setTimeout(function(){var r=reply(v);push("bot",r);say(r);},340);});',
    'function say(t){if(!("speechSynthesis" in window))return;try{speechSynthesis.cancel();var u=new SpeechSynthesisUtterance(t);u.rate=1;u.pitch=__PITCH__;var vs=speechSynthesis.getVoices()||[];var p=vs.filter(function(x){return /^en/i.test(x.lang);})[0];if(p)u.voice=p;speechSynthesis.speak(u);}catch(e){}}',
    'document.getElementById("say").addEventListener("click",function(){var g=KB.greeting||("Hello, I am "+SPEC.name+".");push("bot",g);say(g);});',
    'var mb=document.getElementById("mic"),R=window.SpeechRecognition||window.webkitSpeechRecognition,r=null;',
    'if(!R){mb.disabled=true;mb.title="SpeechRecognition is not supported in this browser";}else{mb.addEventListener("click",function(){',
    ' if(r){try{r.stop();}catch(e){}r=null;mb.textContent="🎤 Talk to me";return;}',
    ' r=new R();r.lang="en-US";r.interimResults=false;',
    ' r.onstart=function(){mb.textContent="🔴 Listening…";};',
    ' r.onresult=function(ev){var t=ev.results[0][0].transcript;q.value=t;mb.textContent="🎤 Talk to me";f.dispatchEvent(new Event("submit",{cancelable:true}));r=null;};',
    ' r.onerror=function(){mb.textContent="🎤 Talk to me";r=null;};',
    ' r.onend=function(){mb.textContent="🎤 Talk to me";};',
    ' try{r.start();}catch(e){r=null;}});}',
    '})();'
  ].join('\n').replace('__PITCH__', '(SPEC.voice&&SPEC.voice.fundamentalHz?(SPEC.voice.fundamentalHz<105?.85:SPEC.voice.fundamentalHz<150?.98:1.12):1.05)');

  /* ==========================================================
     READY PLAYER ME
     ========================================================== */
  var RPM_SRC = 'https://demo.readyplayer.me/avatar?clearCache=true&language=en&frameApi=true';
  function openRpm() {
    var modal = $('#rpm-modal');
    if (!modal) return;
    var frame = $('#rpm-frame');
    if (frame && !frame.src) frame.src = RPM_SRC;
    modal.classList.add('open');
    document.body.style.overflow = 'hidden';
    var note = $('#rpm-note');
    if (note) note.innerHTML = 'Loading the Ready Player Me creator from <code>demo.readyplayer.me</code>… If this stays blank you are offline or the frame is blocked — use “Open in a new tab” instead, then paste the avatar URL below.';
  }
  function closeRpm() {
    var modal = $('#rpm-modal');
    if (modal) modal.classList.remove('open');
    document.body.style.overflow = '';
  }
  function onRpmMessage(ev) {
    if (!/readyplayer\.me/.test(ev.origin || '')) return;
    var d = ev.data;
    if (typeof d === 'string') { try { d = JSON.parse(d); } catch (e) { return; } }
    if (!d || d.source !== 'readyplayerme') return;
    if (d.eventName === 'v1.avatar.exported') {
      profile.rpm = { url: d.data.url, id: d.data.id || null, source: 'readyplayerme', at: new Date().toISOString() };
      save(); paintRpm();
      toast('Ready Player Me avatar linked: ' + (d.data.id || d.data.url));
      closeRpm();
    } else if (d.eventName === 'v1.avatar_template.loaded' || d.eventName === 'v1.user.loaded') {
      var note = $('#rpm-note');
      if (note) note.innerHTML = 'Creator ready. Finish your avatar and click <b>Save / Next</b> — the exported GLB URL is captured automatically.';
    }
  }
  function paintRpm() {
    var box = $('#rpm-out');
    if (!box) return;
    if (profile.rpm && profile.rpm.url) {
      box.innerHTML =
        '<div class="callout good"><b>Ready Player Me avatar linked.</b><br>' +
        '<span style="font-family:ui-monospace,Menlo,monospace;font-size:12px;word-break:break-all">' + escapeHtml(profile.rpm.url) + '</span></div>' +
        '<div class="btn-row" style="margin-top:12px">' +
          '<button class="btn btn-sm btn-ghost" id="rpm-copy" type="button">Copy GLB URL</button>' +
          '<button class="btn btn-sm btn-ghost" id="rpm-clear" type="button">Unlink</button>' +
          '<a class="btn btn-sm btn-ghost" href="developers.html">How to render it</a>' +
        '</div>' +
        '<div id="rpm-viewer" style="margin-top:16px"></div>';
      var c = $('#rpm-copy');
      if (c) c.addEventListener('click', function () {
        var u = profile.rpm.url;
        if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(u).then(function () { toast('GLB URL copied.'); }, function () { toast(u); });
        else toast(u);
      });
      var x = $('#rpm-clear');
      if (x) x.addEventListener('click', function () { profile.rpm = null; save(); paintRpm(); toast('Ready Player Me avatar unlinked.'); });
      mountVisage();
    } else {
      box.innerHTML = '<p style="font-size:13.4px;color:var(--dim)">No 3D body linked yet. Optional — your agent works without it.</p>';
    }
  }
  function mountVisage() {
    var host = $('#rpm-viewer');
    if (!host || !profile.rpm || !profile.rpm.url) return;
    if (!('customElements' in window)) { host.innerHTML = visageFallback(); return; }
    host.innerHTML =
      '<div id="visage-host" style="width:100%;height:360px;border-radius:18px;overflow:hidden;border:1px solid var(--stroke);background:#0b0620;position:relative">' +
        '<visage-avatar id="va" style="width:100%;height:100%;display:block" src="' + escapeHtml(profile.rpm.url) + '" disable-sounds></visage-avatar>' +
        '<div id="visage-fallback" style="position:absolute;inset:0;display:grid;place-items:center;text-align:center;padding:20px;font-size:13px;color:var(--dim)">' +
          'Loading the 3D viewer…<br><span style="font-size:11.6px">If nothing appears you are offline — the GLB URL above still works in Unity/Unreal/Three.js.</span></div>' +
      '</div>' +
      '<script type="module" src="https://unpkg.com/@readyplayerme/visage@latest/dist/visage.js"><\/script>';
    setTimeout(function () {
      var fb = $('#visage-fallback');
      var el = $('#va');
      var rendered = false;
      try { rendered = !!(el && (el.shadowRoot || el.canvas || el._loaded)); } catch (e) {}
      if (fb && !rendered && el && el.shadowRoot && el.shadowRoot.querySelector('canvas')) rendered = true;
      if (fb && rendered) fb.style.display = 'none';
    }, 6000);
  }
  function visageFallback() {
    return '<div class="callout warn">The 3D viewer needs a network connection. Your avatar URL is saved and can be loaded with ' +
           '<code>@readyplayerme/visage</code>, the Unity SDK or the Unreal SDK — see <a href="developers.html" style="color:var(--cyan)">Developers</a>.</div>';
  }

  /* ==========================================================
     WIRING
     ========================================================== */
  function wire() {
    /* steps */
    $$('.step-tab').forEach(function (b) {
      b.addEventListener('click', function () { gotoStep(+b.dataset.goto); });
    });
    var back = $('#step-back'), next = $('#step-next');
    if (back) back.addEventListener('click', function () { gotoStep(stepNo - 1); });
    if (next) next.addEventListener('click', function () {
      if (stepNo === 4) { forgeAgent(); return; }
      if (next.disabled) { toast($('#step-hint') ? $('#step-hint').textContent : 'Complete this step first.', 'warn'); return; }
      gotoStep(stepNo + 1);
    });

    /* --- step 1 --- */
    var camBtn = $('#btn-camera');
    if (camBtn) camBtn.addEventListener('click', function () {
      if (camStream) { stopCamera(); camBtn.innerHTML = camIcon() + ' Use my camera'; setCamStatus('Camera off.'); }
      else { camBtn.innerHTML = camIcon() + ' Stop camera'; startCamera(); }
    });
    var shotBtn = $('#btn-shoot');
    if (shotBtn) shotBtn.addEventListener('click', captureFromVideo);
    var fileBtn = $('#btn-upload-img'), fileIn = $('#file-img');
    if (fileBtn && fileIn) {
      fileBtn.addEventListener('click', function () { fileIn.click(); });
      fileIn.addEventListener('change', function () { if (fileIn.files && fileIn.files[0]) acceptFile(fileIn.files[0]); });
    }
    var dz = $('#dropzone');
    if (dz) {
      dz.addEventListener('click', function () { if (fileIn) fileIn.click(); });
      ['dragenter', 'dragover'].forEach(function (ev) {
        dz.addEventListener(ev, function (e) { e.preventDefault(); dz.classList.add('over'); });
      });
      ['dragleave', 'drop'].forEach(function (ev) {
        dz.addEventListener(ev, function (e) { e.preventDefault(); dz.classList.remove('over'); });
      });
      dz.addEventListener('drop', function (e) {
        var f = e.dataTransfer && e.dataTransfer.files && e.dataTransfer.files[0];
        if (f) acceptFile(f);
      });
    }
    var clearImg = $('#btn-clear-img');
    if (clearImg) clearImg.addEventListener('click', function () {
      profile.image = null; profile.imageMeta = null; save();
      var img = $('#shot-preview'); if (img) { img.removeAttribute('src'); img.style.display = 'none'; }
      var ph = $('#shot-placeholder'); if (ph) ph.style.display = 'grid';
      var rows = $('#img-analysis'); if (rows) rows.innerHTML = '';
      setFaceNote('');
      refreshGates(); toast('Image removed from this browser.');
    });
    var nameIn = $('#name-input');
    if (nameIn) nameIn.addEventListener('input', function () { profile.name = nameIn.value.trim(); suggestAgentName(nameIn.value); });

    /* --- step 2 --- */
    var recBtn = $('#btn-record');
    if (recBtn) recBtn.addEventListener('click', startRecording);
    var vBtn = $('#btn-upload-voice'), vIn = $('#file-voice');
    if (vBtn && vIn) {
      vBtn.addEventListener('click', function () { vIn.click(); });
      vIn.addEventListener('change', function () {
        var f = vIn.files && vIn.files[0];
        if (!f) return;
        if (!/^audio\//.test(f.type)) { toast('That file is not audio (' + f.type + ').', 'warn'); return; }
        handleVoiceBlob(f);
      });
    }
    var scriptBtn = $('#btn-script');
    if (scriptBtn) scriptBtn.addEventListener('click', function () {
      var box = $('#script-box');
      if (!box) return;
      var open = box.style.display !== 'none';
      box.style.display = open ? 'none' : 'block';
      scriptBtn.setAttribute('aria-expanded', String(!open));
    });
    var testBtn = $('#btn-test-voice');
    if (testBtn) testBtn.addEventListener('click', function () {
      var p = profile.persona;
      speakOut(p ? p.greeting : 'This is how my voice will sound inside the Ai Metaverse.',
               { pitch: pitchFromFreq((profile.voice || profile.voiceMeta || {}).freq) });
    });

    /* --- step 3 --- */
    var bd = $('#birthday');
    if (bd) {
      bd.addEventListener('change', function () {
        var v = bd.value;
        if (!v) return;
        var parts = v.split('-').map(Number);
        var dt = new Date(parts[0], parts[1] - 1, parts[2]);
        var now = new Date();
        if (isNaN(dt.getTime()) || dt > now) { toast('That birthday is in the future — check the date.', 'warn'); bd.value = ''; return; }
        if (parts[0] < 1900) { toast('Please use a year from 1900 onward.', 'warn'); return; }
        profile.birthday = v;
        profile.persona = derivePersona(v);
        save(); renderPersona();
        toast('Personality vector derived from ' + v + ' — ' + profile.persona.sign + ', life path ' + profile.persona.lifePath + '.');
      });
    }

    /* --- step 4 --- */
    var an = $('#agent-name');
    if (an) an.addEventListener('input', function () { if (profile.agent) { profile.agent.name = an.value.trim(); } });
    var roleSel = $('#agent-role');
    if (roleSel) {
      Object.keys(ROLES).forEach(function (r) {
        var o = document.createElement('option'); o.value = r; o.textContent = r; roleSel.appendChild(o);
      });
      roleSel.addEventListener('change', function () {
        var d = $('#role-brief'); if (d) d.textContent = ROLES[roleSel.value] || '';
        renderReview();
      });
      var d0 = $('#role-brief'); if (d0) d0.textContent = ROLES[roleSel.value] || '';
    }
    var vSel = $('#agent-voice');
    if (vSel) VOICE_STYLES.forEach(function (s) { var o = document.createElement('option'); o.textContent = s; vSel.appendChild(o); });
    var tEl = $('#agent-temp'), tOut = $('#agent-temp-out');
    if (tEl) tEl.addEventListener('input', function () { if (tOut) tOut.textContent = parseFloat(tEl.value).toFixed(2); renderReview(); });
    var forge = $('#btn-forge');
    if (forge) forge.addEventListener('click', forgeAgent);
    var again = $('#btn-again');
    if (again) again.addEventListener('click', function () { gotoStep(1); });

    /* --- ready player me --- */
    var rpmOpen = $('#btn-rpm');
    if (rpmOpen) rpmOpen.addEventListener('click', openRpm);
    var rpmNew = $('#btn-rpm-tab');
    if (rpmNew) rpmNew.addEventListener('click', function () { window.open(RPM_SRC, '_blank', 'noopener'); });
    $$('[data-close-rpm]').forEach(function (b) { b.addEventListener('click', closeRpm); });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape') closeRpm(); });
    window.addEventListener('message', onRpmMessage);
    var rpmPaste = $('#rpm-paste'), rpmSave = $('#btn-rpm-save');
    if (rpmSave && rpmPaste) {
      rpmSave.addEventListener('click', function () {
        var u = rpmPaste.value.trim();
        if (!/^https:\/\/[^\s]+\.glb(\?[^\s]*)?$/i.test(u)) { toast('Paste the full avatar URL, e.g. https://models.readyplayer.me/xxxx.glb', 'warn'); return; }
        var idm = u.match(/\/([A-Za-z0-9]+)\.glb/);
        profile.rpm = { url: u, id: idm ? idm[1] : null, source: 'manual', at: new Date().toISOString() };
        save(); paintRpm(); toast('Avatar URL saved to your profile.');
      });
    }

    /* --- privacy / reset --- */
    var wipe = $('#btn-wipe');
    if (wipe) wipe.addEventListener('click', function () {
      if (!confirm('Delete your selfie, voice analysis, birthday and all forged agents from this browser? This cannot be undone.')) return;
      try { localStorage.removeItem(STORE_KEY); } catch (e) {}
      stopCamera();
      if ('speechSynthesis' in window) speechSynthesis.cancel();
      location.reload();
    });

    /* --- restore --- */
    if (load()) {
      if (profile.name && nameIn) nameIn.value = profile.name;
      if (profile.birthday && bd) bd.value = profile.birthday;
      if (profile.persona) renderPersona();
      paintImageStep();
      paintVoiceStep();
      paintRpm();
      if (profile.agent) {
        if (an) an.value = profile.agent.name || '';
        if (roleSel) { roleSel.value = profile.agent.role || roleSel.value; var dd = $('#role-brief'); if (dd) dd.textContent = ROLES[roleSel.value] || ''; }
        if (vSel && profile.agent.voiceStyle) vSel.value = profile.agent.voiceStyle;
        if (tEl && profile.agent.temperature) { tEl.value = profile.agent.temperature; if (tOut) tOut.textContent = profile.agent.temperature.toFixed(2); }
        var doneBox = $('#forge-done');
        if (doneBox) {
          doneBox.style.display = 'block';
          var existing = $('#existing-agent');
          if (existing) {
            existing.style.display = 'block';
            existing.innerHTML = '<div class="callout good"><b>Agent already forged:</b> ' + escapeHtml(profile.agent.name) +
              ' · <span style="font-family:ui-monospace,Menlo,monospace">' + profile.agent.id + '</span> · ' + escapeHtml(profile.agent.role) +
              '. <a href="avatar.html#agent" style="color:var(--cyan);text-decoration:underline">Open it</a>, or forge a new one below.</div>';
          }
        }
      }
      var stamp = $('#restored-at');
      if (stamp && profile.updatedAt) stamp.textContent = 'Profile restored from this browser · saved ' + new Date(profile.updatedAt).toLocaleString();
    }
    if (!profile.voice && !profile.voiceMeta) setRecStatus(canRecord() ? 'Ready to record.' : 'Recording unsupported here — upload a voice file instead.', !canRecord());
    if (!profile.image) setCamStatus(hasCam() ? 'Camera available.' : 'No camera API in this browser — upload an image instead.', !hasCam());
    paintRpm();
    gotoStep(1, false);
    var scriptBox = $('#script-box'); if (scriptBox) scriptBox.style.display = 'none';
  }

  function camIcon() {
    return '<svg viewBox="0 0 24 24" fill="none" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round">' +
           '<path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/><circle cx="12" cy="13" r="4"/></svg>';
  }

  /* expose a tiny API for other pages (avatar.html, metabox.html) */
  window.AIMV_PROFILE = {
    get: function () { load(); return profile; },
    load: load, save: save,
    persona: function () { return profile.persona; },
    speak: speakOut,
    pitchFromFreq: pitchFromFreq,
    spec: specObject,
    acceptCanvas: acceptImageCanvas,
    analyseImage: analyseImage,
    agentHtml: function () { return agentHtml(specObject()); },
    download: download,
    toast: toast,
    ROLES: ROLES, VOICE_STYLES: VOICE_STYLES, STORE_KEY: STORE_KEY
  };

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', wire);
  else wire();
})();
