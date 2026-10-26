const { JSDOM } = require('jsdom');
const fs = require('fs');
const html = fs.readFileSync('voice-lipsync/index.html', 'utf8');
const errors = [];
const downloads = [];
const dom = new JSDOM(html, {
  runScripts: 'dangerously', pretendToBeVisual: true,
  url: 'https:///voice-lipsync/index.html',
  beforeParse(w) {
    w.matchMedia = () => ({ matches: false, addListener(){}, removeListener(){}, addEventListener(){}, removeEventListener(){} });
    w.scrollTo = () => {};
    w.alert = () => {};
    w.speechSynthesis = { speak(){}, cancel(){}, getVoices(){ return []; }, addEventListener(){} };
    w.SpeechRecognition = function(){ this.start=()=>{}; this.stop=()=>{}; this.abort=()=>{}; this.addEventListener=()=>{}; };
    w.webkitSpeechRecognition = w.SpeechRecognition;
    w.HTMLCanvasElement.prototype.getContext = function(){ throw new Error('no canvas'); };
    w.HTMLAnchorElement.prototype.click = function(){ downloads.push({ name: this.download, href: (this.href || '').slice(0, 30) }); };
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
  C('vl-embed present', !!q('.vl-embed'));
  C('section heading', /Upload your voice/.test(t('#voice-lipsync .sec-head')));
  C('module header stripped', !/VOICE & LIP-SYNC <span/.test(html));
  C('module footer stripped', !/Privacy Guaranteed/.test(html));
  C('crosslink to twin-studio (folder form)', !!q('#voice-lipsync a[href="twin-studio/index.html"]'));
  C('crosslink to avatar-create (folder form)', !!q('#voice-lipsync a[href="avatar-create/index.html"]'));
  C('tailwind c25 palette inlined', /colors:\{c25:\{dark:'#020617'/.test(html));
  C('scan keyframes defined', /@keyframes scan\{0%\{top:0%\}100%\{top:100%\}\}/.test(html));
  C('wave keyframes defined', /@keyframes wave\{0%,100%\{height:20%\}50%\{height:100%\}\}/.test(html));
  C('pulse-glow keyframes (purple)', /@keyframes pulse-glow\{0%,100%\{box-shadow:0 0 20px rgba\(139,92,246/.test(html));
  C('fadeIn keyframes intact', /@keyframes fadeIn \{ from/.test(html));
  C('toast moved off humanoid dock', /\.vl-embed #toast\{left:16px;right:auto/.test(html));
  C('no assets/ refs', !/(src|href)="assets\//.test(html));
  C('no external tailwind cdn script', !/src="https:\/\/cdn\.tailwindcss\.com/.test(html));
  C('no innerText left', !/\.innerText/.test(html));
  C('grid backdrop kept', /gap-8 bg-grid/.test(html));
  C('textarea maxlength 500', q('#scriptInput') && q('#scriptInput').getAttribute('maxlength') === '500');
  C('export button wired', !!q('#exportBtn') && /exportMP4\(\)/.test(q('#exportBtn').getAttribute('onclick') || ''));
  C('all step ids present', ['avatarInput','voiceInput','btn-photo','btn-video','avatarPreview','previewImg','voiceFileName','charCount','generateBtn','renderPlaceholder','renderActive','renderImage','processingOverlay','progressBar','processStatus','processDetail','videoComplete','finalAvatarImg','mouthOverlay','voiceVisualizer','finalScriptDisplay','toast','toastMessage'].every(id => !!q('#' + id)));

  // --- handlers exported from IIFE ---
  C('handlers exported', ['setAvatarType','handleAvatarUpload','handleVoiceUpload','startRendering','resetStudio','exportMP4'].every(fn => typeof w[fn] === 'function'));

  // --- avatar source toggle ---
  w.setAvatarType('video');
  C('video mode: accept switched', q('#avatarInput').getAttribute('accept') === 'video/*');
  C('video mode: button active', /bg-c25-purple\/20/.test(q('#btn-video').className) && /bg-slate-800/.test(q('#btn-photo').className));
  w.setAvatarType('photo');
  C('photo mode: accept switched back', q('#avatarInput').getAttribute('accept') === 'image/*');
  C('photo mode: button active', /bg-c25-purple\/20/.test(q('#btn-photo').className));

  // --- guards ---
  click(q('#generateBtn'));
  C('guard toast (no avatar)', /upload an avatar photo or video first/i.test(t('#toastMessage')));
  C('guard keeps stage idle', q('#renderActive').classList.contains('hidden'));
  const imgFile = new w.File(['fakepngbytes'], 'portrait.png', { type: 'image/png' });
  w.handleAvatarUpload({ files: [imgFile] });

  setTimeout(() => {
    click(q('#generateBtn'));
    C('guard toast (no voice)', /voice cloning sample/i.test(t('#toastMessage')));
    w.handleVoiceUpload({ files: [{ name: 'my-voice-10s.mp3' }] });
    q('#scriptInput').value = 'Hello world, this is my twin speaking.';
    q('#scriptInput').dispatchEvent(new w.Event('input', { bubbles: true }));
    C('char counter updated', t('#charCount') === '38 / 500 chars');
    click(q('#generateBtn'));
    C('render starts when all inputs ready', !q('#renderActive').classList.contains('hidden'));

    setTimeout(() => {
      C('avatar preview shown', !q('#previewImg').classList.contains('hidden') && /^data:image\/png/.test(q('#previewImg').src));
      C('dropzone faded', q('#avatarPreview').classList.contains('opacity-0'));
      C('voice name shown', t('#voiceFileName') === 'my-voice-10s.mp3');
      C('voice name styled', q('#voiceFileName').classList.contains('text-c25-purple'));
      C('placeholder hidden', q('#renderPlaceholder').classList.contains('hidden'));
      C('stage active + scanning', q('#renderActive').classList.contains('scanning'));
      C('generateBtn disabled', q('#generateBtn').disabled === true);
      C('synthesizing label', /Synthesizing/.test(q('#generateBtn').innerHTML));
      C('render bg = uploaded avatar', /^data:image\/png/.test(q('#renderImage').src));
      C('final img = uploaded avatar', /^data:image\/png/.test(q('#finalAvatarImg').src));
      // re-entrancy guard: clicking again while rendering must not restart the chain
      click(q('#generateBtn'));
      C('isRendering guard holds', q('#generateBtn').disabled === true);

      setTimeout(() => { // ~2.6s: step 2 (45%)
        C('progress at 45%', q('#progressBar').style.width === '45%');
        C('status = facial landmarks', /Mapping Facial Landmarks/i.test(t('#processStatus')));
        C('detail = 68 points', /68 facial points/i.test(t('#processDetail')));

        setTimeout(() => { // >8.2s: complete
          C('scanning stopped', !q('#renderActive').classList.contains('scanning'));
          C('overlay hidden', q('#processingOverlay').classList.contains('hidden'));
          C('video revealed', !q('#videoComplete').classList.contains('hidden') && q('#videoComplete').classList.contains('fade-in'));
          C('progress 100%', q('#progressBar').style.width === '100%');
          C('script displayed quoted', /"Hello world, this is my twin speaking\."/.test(t('#finalScriptDisplay')));
          C('40 visualizer bars', qa('#voiceVisualizer > div').length === 40);
          C('success toast', /Lip-sync video successfully generated/i.test(t('#toastMessage')));

          setTimeout(() => {
            C('mouth overlay animating', q('#mouthOverlay').style.opacity !== '' && q('#mouthOverlay').style.height !== '');

            // --- export MP4 (anchor click stubbed) ---
            w.exportMP4();
            C('export downloaded render', downloads.length === 1 && downloads[0].name === 'c25-lipsync-render.png' && /^data:image\/png/.test(downloads[0].href));
            C('export toast', /exported locally/i.test(t('#toastMessage')));

            // --- reset ---
            w.resetStudio();
            C('reset: stage idle', q('#renderActive').classList.contains('hidden') && !q('#renderPlaceholder').classList.contains('hidden'));
            C('reset: video hidden', q('#videoComplete').classList.contains('hidden'));
            C('reset: overlay back', !q('#processingOverlay').classList.contains('hidden'));
            C('reset: progress 0', q('#progressBar').style.width === '0%');
            C('reset: btn re-enabled', q('#generateBtn').disabled === false && /Generate Lip-Sync Video/.test(q('#generateBtn').innerHTML));
            C('reset: inputs cleared', t('#voiceFileName') === 'No file chosen' && q('#scriptInput').value === '' && t('#charCount') === '0 / 500 chars' && q('#previewImg').classList.contains('hidden'));
            const mouthAfterReset = q('#mouthOverlay').style.height;

            setTimeout(() => { // timers must stay dead after reset
              C('reset: talking interval cleared', q('#mouthOverlay').style.height === mouthAfterReset);
              C('reset: render timeouts cleared', q('#progressBar').style.width === '0%' && q('#renderActive').classList.contains('hidden'));
              // re-render after reset must work (guard released)
              click(q('#generateBtn'));
              C('post-reset guard toast (inputs empty)', /upload an avatar photo or video first/i.test(t('#toastMessage')));

              const bad = errors.filter(e => !/Could not parse CSS|no canvas|Not implemented|css parsing|getContext/i.test(e));
              C('no JS errors (' + bad.length + ')', bad.length === 0);
              if (bad.length) console.log(bad.slice(0, 4).join('\n---\n'));

              let fails = 0;
              checks.forEach(([s, n]) => { if (s === 'FAIL') fails++; console.log(s, n); });
              console.log(fails ? 'FAILURES: ' + fails : 'ALL PASS (' + checks.length + ' checks)');
              process.exit(fails ? 1 : 0);
            }, 1300);
          }, 400);
        }, 5700);
      }, 2600);
    }, 400);
  }, 300);
}, 1800);
