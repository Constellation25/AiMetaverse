const { JSDOM } = require('jsdom');
const fs = require('fs');
const html = fs.readFileSync('twin-studio/index.html', 'utf8');
const errors = [];
let spoke = 0, listened = 0;
const dom = new JSDOM(html, {
  runScripts: 'dangerously', pretendToBeVisual: true,
  url: 'https://constillation25.github.io/AiMetaverse/twin-studio/index.html',
  beforeParse(w) {
    w.matchMedia = () => ({ matches: false, addListener(){}, removeListener(){}, addEventListener(){}, removeEventListener(){} });
    w.scrollTo = () => {};
    w.alert = () => {};
    w.speechSynthesis = { speak(){}, cancel(){}, getVoices(){ return []; }, addEventListener(){} };
    w.SpeechRecognition = function(){ this.start=()=>{}; this.stop=()=>{}; this.abort=()=>{}; this.addEventListener=()=>{}; };
    w.webkitSpeechRecognition = w.SpeechRecognition;
    w.HTMLCanvasElement.prototype.getContext = function(){ throw new Error('no canvas'); };
    w.addEventListener('error', e => errors.push('window.error: ' + (e.error && e.error.stack || e.message)));
    w.console.error = (...a) => { errors.push('console.error: ' + a.join(' ')); };
  }
});
const checks = [];
const C = (name, cond) => checks.push([cond ? 'PASS' : 'FAIL', name]);

setTimeout(() => {
  const w = dom.window, d = w.document;
  const q = s => d.querySelector(s);
  const qa = s => Array.from(d.querySelectorAll(s));
  const t = s => (q(s) ? q(s).textContent.trim() : '(missing)');
  const click = el => el.dispatchEvent(new w.MouseEvent('click', { bubbles: true, cancelable: true }));

  // --- structure ---
  C('base href ../', q('base') && q('base').getAttribute('href') === '../');
  C('vt-embed present', !!q('.vt-embed'));
  C('section heading', /Create myself as an/.test(t('#twin-studio .sec-head')));
  C('module header stripped', !/VIRTUAL TWIN <span/.test(html));
  C('module footer stripped', !/Privacy Guaranteed/.test(html));
  C('crosslink to avatar-create (folder form)', !!q('#twin-studio a[href="avatar-create/index.html"]'));
  C('tailwind c25 palette inlined', /colors:\{c25:\{dark:'#020617'/.test(html));
  C('scan keyframes defined', /@keyframes scan\{0%\{top:0%\}100%\{top:100%\}\}/.test(html));
  C('fadeIn keyframes intact', /@keyframes fadeIn \{ from/.test(html));
  C('toast moved off humanoid dock', /\.vt-embed #toast\{left:16px;right:auto/.test(html));
  C('no assets/ refs', !/(src|href)="assets\//.test(html));
  C('no innerText left', !/\.innerText/.test(html));
  C('no stray markup (6)', !/\/>\s*\n\s*6\s*\n/.test(html));
  C('no unclosed </div', !/<\/div\s*\n/.test(html));
  C('toast closed properly', /Action successful<\/span>\s*<\/div>/.test(html));
  C('chat hooks present', !!q('#twinInput') && !!q('#twinMic') && !!q('#twinChat'));
  C('grid backdrop kept', /gap-8 bg-grid/.test(html));

  // --- handlers exported from IIFE ---
  C('handlers exported', ['handleImageUpload','handleVoiceUpload','startRendering','resetStudio'].every(fn => typeof w[fn] === 'function'));

  // --- guard: no image yet ---
  click(q('#createBtn'));
  C('guard toast (no image)', /upload a spatial image first/i.test(t('#toastMessage')));
  C('guard keeps stage idle', q('#renderActive').classList.contains('hidden'));

  // --- uploads ---
  const imgFile = new w.File(['fakepngbytes'], 'spatial-scan.png', { type: 'image/png' });
  w.handleImageUpload({ files: [imgFile] });
  const voiceFile = new w.File(['fakeaudiobytes'], 'my-voice-10s.wav', { type: 'audio/wav' });
  w.handleVoiceUpload({ files: [voiceFile] });
  q('#personaInput').value = 'Confident, analytical, dry humor';

  setTimeout(() => {
    C('image preview shown', !q('#previewImg').classList.contains('hidden') && /^data:image\/png/.test(q('#previewImg').src));
    C('dropzone faded', q('#imagePreview').classList.contains('opacity-0'));
    C('image toast', /Spatial image synced/i.test(t('#toastMessage')));
    C('voice name shown', t('#voiceFileName') === 'my-voice-10s.wav');
    C('voice name styled', q('#voiceFileName').classList.contains('text-c25-purple'));

    // --- start the render ---
    click(q('#createBtn'));
    C('placeholder hidden', q('#renderPlaceholder').classList.contains('hidden'));
    C('stage active + scanning', !q('#renderActive').classList.contains('hidden') && q('#renderActive').classList.contains('scanning'));
    C('createBtn disabled', q('#createBtn').disabled === true);
    C('render bg = uploaded image', /^data:image\/png/.test(q('#renderImage').src));

    setTimeout(() => { // ~3s into render: step 2 (50%)
      C('progress at 50%', q('#progressBar').style.width === '50%');
      C('status = voice biometrics', /voice biometrics/i.test(t('#processStatus')));

      setTimeout(() => { // >6.5s: complete
        C('scanning stopped', !q('#renderActive').classList.contains('scanning'));
        C('overlay hidden', q('#processingOverlay').classList.contains('hidden'));
        C('twin revealed', !q('#twinComplete').classList.contains('hidden') && q('#twinComplete').classList.contains('fade-in'));
        C('progress 100%', q('#progressBar').style.width === '100%');
        C('persona woven into greeting', /Confident, analytical, dry humor/.test(t('#twinGreeting')));
        C('40 visualizer bars', qa('#voiceVisualizer > div').length === 40);
        C('success toast', /successfully created and activated/i.test(t('#toastMessage')));

        // --- twin chat (stub the companion brain) ---
        w.AIMV_HUMANOID = { brain: qq => 'TWIN-REPLY:' + qq, speak: () => { spoke++; }, listen: () => { listened++; } };
        q('#twinInput').value = 'hello twin';
        q('#twinInput').dispatchEvent(new w.KeyboardEvent('keydown', { key: 'Enter', bubbles: true }));
        C('user bubble pushed', /hello twin/.test(q('#twinChat').textContent));
        C('input cleared', q('#twinInput').value === '');

        setTimeout(() => {
          C('bot replied via brain', /TWIN-REPLY:hello twin/.test(q('#twinChat').textContent));
          C('reply spoken', spoke === 1);
          click(q('#twinMic'));
          C('mic routes to companion listen', listened === 1);

          // --- XSS: user text escaped ---
          w.AIMV_HUMANOID = { brain: () => 'ok', speak: () => {} };
          q('#twinInput').value = '<img src=x onerror=alert(1)>';
          q('#twinInput').dispatchEvent(new w.KeyboardEvent('keydown', { key: 'Enter', bubbles: true }));
          C('user html escaped', !/<img src=x/.test(q('#twinChat').innerHTML.replace(/&lt;img src=x/g, '')) && /&lt;img src=x/.test(q('#twinChat').innerHTML));

          // --- reset ---
          w.resetStudio();
          C('reset: stage idle', q('#renderActive').classList.contains('hidden') && !q('#renderPlaceholder').classList.contains('hidden'));
          C('reset: twin hidden', q('#twinComplete').classList.contains('hidden'));
          C('reset: overlay back', !q('#processingOverlay').classList.contains('hidden'));
          C('reset: progress 0', q('#progressBar').style.width === '0%');
          C('reset: btn re-enabled', q('#createBtn').disabled === false && /Create My Virtual Twin as an AI/.test(q('#createBtn').innerHTML));
          C('reset: inputs cleared', t('#voiceFileName') === 'No file chosen' && q('#personaInput').value === '' && q('#previewImg').classList.contains('hidden'));

          // --- no unexpected JS errors ---
          const bad = errors.filter(e => !/Could not parse CSS|no canvas|Not implemented|css parsing|getContext/i.test(e));
          C('no JS errors (' + bad.length + ')', bad.length === 0);
          if (bad.length) console.log(bad.slice(0, 4).join('\n---\n'));

          let fails = 0;
          checks.forEach(([s, n]) => { if (s === 'FAIL') fails++; console.log(s, n); });
          console.log(fails ? 'FAILURES: ' + fails : 'ALL PASS (' + checks.length + ' checks)');
          process.exit(fails ? 1 : 0);
        }, 700);
      }, 5400);
    }, 3000);
  }, 400);
}, 1800);
