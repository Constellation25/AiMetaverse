const { JSDOM } = require('jsdom');
const fs = require('fs');
const html = fs.readFileSync('prompter/index.html', 'utf8');
const errors = [];
let copied = null;
const dom = new JSDOM(html, {
  runScripts: 'dangerously', pretendToBeVisual: true,
  url: 'https:///prompter/index.html',
  beforeParse(w) {
    w.matchMedia = () => ({ matches: false, addListener(){}, removeListener(){}, addEventListener(){}, removeEventListener(){} });
    w.scrollTo = () => {};
    w.alert = () => {};
    w.speechSynthesis = { speak(){}, cancel(){}, getVoices(){ return []; }, addEventListener(){} };
    w.SpeechRecognition = function(){ this.start=()=>{}; this.stop=()=>{}; this.abort=()=>{}; this.addEventListener=()=>{}; };
    w.webkitSpeechRecognition = w.SpeechRecognition;
    w.HTMLCanvasElement.prototype.getContext = function(){ throw new Error('no canvas'); };
    try { Object.defineProperty(w.navigator, 'clipboard', { configurable: true, value: { writeText: (t) => { copied = t; return Promise.resolve(); } } }); } catch (e) {}
    w.addEventListener('error', e => errors.push('window.error: ' + (e.error && e.error.stack || e.message)));
    w.console.error = (...a) => { errors.push('console.error: ' + a.join(' ')); };
  }
});
setTimeout(() => {
  const w = dom.window, d = w.document;
  const q = s => d.querySelector(s);
  const qa = s => Array.from(d.querySelectorAll(s));
  const t = s => (q(s) ? q(s).textContent.trim() : '(missing)');
  const checks = [];
  const C = (name, cond) => checks.push([cond ? 'PASS' : 'FAIL', name]);
  const click = el => el.dispatchEvent(new w.MouseEvent('click', { bubbles: true, cancelable: true }));

  // --- structure ---
  C('base href ../', q('base') && q('base').getAttribute('href') === '../');
  C('pr-embed present', !!q('.pr-embed'));
  C('section heading', /Select avatar prompts with/.test(t('#prompter .sec-head')) && /Prompter/.test(t('#prompter .sec-head h2')));
  C('crosslink to forge', !!q('#prompter a[href="avatar-create/index.html"]'));

  // --- initial render (all avatars) ---
  C('9 avatar buttons', qa('#avatarList .avatar-btn').length === 9);
  C('8 prompt cards', qa('#promptGrid .prompt-card').length === 8);
  C('resultCount 8', t('#resultCount') === '8');
  C('libraryTitle All Prompts', t('#libraryTitle') === 'All Prompts');
  C('2 suggestions for all', qa('#suggestionCards > div').length === 2);
  C('search input present', !!q('#searchInput'));
  C('View Repo is a github link', !!q('header a[href="https://github.com/x1xhlol/system-prompts"]') && !/View Repo<\/button>/.test(q('header').innerHTML));
  C('inline onclick wired (avatar)', /onclick="selectAvatar\('windsurf'\)"/.test(q('#avatarList').innerHTML));
  C('inline onclick wired (card)', /onclick="openModal\(/.test(q('#promptGrid').innerHTML));

  // --- avatar filter via a REAL click (proves inline handler runs) ---
  const windsurfBtn = qa('#avatarList .avatar-btn').find(b => /Windsurf/.test(b.textContent));
  click(windsurfBtn);
  C('click Windsurf -> 1 card', qa('#promptGrid .prompt-card').length === 1);
  C('Windsurf card is Tools Wave 11', /Tools Wave 11/.test(q('#promptGrid').textContent));
  C('libraryTitle Windsurf', t('#libraryTitle') === 'Windsurf');
  C('resultCount 1', t('#resultCount') === '1');
  C('1 suggestion for windsurf', qa('#suggestionCards > div').length === 1);
  const activeBtn = q('#avatarList .avatar-btn.active');
  C('active class on windsurf btn', !!activeBtn && /Windsurf/.test(activeBtn.textContent));

  // --- reset + search filter ---
  w.selectAvatar('all');
  C('reset -> 8 cards', qa('#promptGrid .prompt-card').length === 8);
  const si = q('#searchInput'); si.value = 'CLI';
  si.dispatchEvent(new w.Event('input', { bubbles: true }));
  C('search CLI -> Qwen only', qa('#promptGrid .prompt-card').length === 1 && /Qwen Code Agent CLI/.test(q('#promptGrid').textContent));
  si.value = 'zzzznomatch'; si.dispatchEvent(new w.Event('input', { bubbles: true }));
  C('empty state on no match', /No prompts found/.test(q('#promptGrid').textContent));
  si.value = ''; si.dispatchEvent(new w.Event('input', { bubbles: true }));
  C('clear search -> 8 cards', qa('#promptGrid .prompt-card').length === 8);

  // --- suggestion click fills search ---
  w.selectAvatar('all');
  const sugg = q('#suggestionCards > div');
  click(sugg);
  C('suggestion click filters', qa('#promptGrid .prompt-card').length >= 1 && q('#searchInput').value.length > 0);
  w.selectAvatar('all'); q('#searchInput').value=''; w.renderPrompts();

  // --- modal open/close ---
  w.openModal(1);
  const modal = q('#promptModal');
  C('modal opens (hidden removed)', !modal.classList.contains('hidden'));
  C('modal title', t('#modalTitle') === 'Agent Prompt 2.0');
  C('modal avatar label', /Cursor/.test(t('#modalAvatar')));
  C('modal file', t('#modalFile') === 'Agent Prompt 2.0.txt');
  C('modal content non-empty', /expert AI coding assistant/.test(t('#modalContent')));
  w.closeModal();
  C('modal closes (hidden added)', modal.classList.contains('hidden'));

  // --- copy action ---
  copied = null;
  w.copyPromptById(8);
  C('copy writes clipboard', copied && /Qwen-Coder/.test(copied));
  C('copy toast', /Prompt copied to clipboard/.test(t('#toastMessage')));

  // --- fork action persists to workspace ---
  w.localStorage.removeItem('aimv_prompt_forks');
  w.forkPromptById(3);
  let forks = [];
  try { forks = JSON.parse(w.localStorage.getItem('aimv_prompt_forks') || '[]'); } catch (e) {}
  C('fork persisted 1', forks.length === 1 && forks[0].title === 'Tools Wave 11');
  C('fork stores content', /Windsurf, an AI pair programmer/.test(forks[0].text || ''));
  C('fork toast reflects count', /Forked .* to your workspace \(1 saved\)/.test(t('#toastMessage')));
  w.forkPromptById(3); // dedupe
  try { forks = JSON.parse(w.localStorage.getItem('aimv_prompt_forks') || '[]'); } catch (e) {}
  C('fork dedupes same title', forks.length === 1);
  w.forkPromptById(4);
  try { forks = JSON.parse(w.localStorage.getItem('aimv_prompt_forks') || '[]'); } catch (e) {}
  C('fork adds second', forks.length === 2);
  C('typos removed from source', !/In real tim/.test(html));

  // --- no unexpected JS errors ---
  const bad = errors.filter(e => !/Could not parse CSS|no canvas|Not implemented|css parsing|getContext/i.test(e));
  C('no JS errors (' + bad.length + ')', bad.length === 0);
  if (bad.length) console.log(bad.slice(0, 4).join('\n---\n'));

  let fails = 0;
  checks.forEach(([s, n]) => { if (s === 'FAIL') fails++; console.log(s, n); });
  console.log(fails ? 'FAILURES: ' + fails : 'ALL PASS (' + checks.length + ' checks)');
  process.exit(fails ? 1 : 0);
}, 1800);
