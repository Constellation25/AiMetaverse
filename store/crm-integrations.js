/* ============================================================
   Agentik CRM — real-world integration layer
   Replaces the simulate* mocks with live API paths (config-first,
   graceful fallback to the original simulations):
     · Google Sheets API  -> real rows into the pipeline
     · Twilio             -> real calls via your serverless endpoint
     · OpenAI / Ollama    -> real AI for the assistant chat
   Config lives in localStorage['agentik_integrations'] and is edited
   in the sidebar -> Integrations view. Nothing is transmitted until
   you save a real endpoint/key.
   ============================================================ */
(function () {
  'use strict';
  var LS = 'agentik_integrations';
  function cfg() { try { return JSON.parse(localStorage.getItem(LS) || '{}'); } catch (e) { return {}; } }
  function saveCfg(c) { try { localStorage.setItem(LS, JSON.stringify(c)); } catch (e) {} }

  /* ---------- tiny CSV parser (Sheets gviz/export fallback) ---------- */
  function parseCsv(text) {
    var rows = [], row = [], cur = '', inQ = false;
    for (var i = 0; i < text.length; i++) {
      var ch = text[i];
      if (inQ) {
        if (ch === '"') { if (text[i + 1] === '"') { cur += '"'; i++; } else inQ = false; }
        else cur += ch;
      } else if (ch === '"') inQ = true;
      else if (ch === ',') { row.push(cur); cur = ''; }
      else if (ch === '\n' || ch === '\r') {
        if (ch === '\r' && text[i + 1] === '\n') i++;
        row.push(cur); cur = '';
        if (row.length > 1 || row[0] !== '') rows.push(row);
        row = [];
      } else cur += ch;
    }
    row.push(cur);
    if (row.length > 1 || row[0] !== '') rows.push(row);
    return rows;
  }

  /* ---------- 1 · Google Sheets: fetch real rows ---------- */
  var legacySheetImport = window.simulateSheetImport;
  window.simulateSheetImport = function () {
    var c = cfg();
    if (!c.sheetsId) {
      showToast('No Google Sheet configured — sample import. Add a Sheet ID in Integrations.');
      return legacySheetImport && legacySheetImport();
    }
    showToast('Fetching rows from Google Sheets…');
    var url = c.sheetsKey
      ? 'https://sheets.googleapis.com/v4/spreadsheets/' + c.sheetsId + '/values/' + encodeURIComponent(c.sheetsRange || 'A:D') + '?key=' + encodeURIComponent(c.sheetsKey)
      : 'https://docs.google.com/spreadsheets/d/' + c.sheetsId + '/gviz/tq?tqx=out:csv';
    fetch(url)
      .then(function (r) { if (!r.ok) throw new Error('HTTP ' + r.status); return r.text(); })
      .then(function (txt) {
        var rows = c.sheetsKey ? normApiRows(txt) : parseCsv(txt).slice(1);
        var added = rows.filter(function (r) { return r && r[0]; }).map(function (r, i) {
          return { id: Date.now() + i, name: String(r[0] || 'Imported'), company: String(r[1] || '—'), phone: String(r[2] || '—'), value: parseInt(r[3] || 0, 10) || 0, status: 'New' };
        });
        if (!added.length) { showToast('Sheet returned no rows.'); return; }
        leads = leads.concat(added); saveLeads(); renderKanban(); renderContacts();
        showToast('Google Sheets import complete: ' + added.length + ' rows.');
        logActivity('Imported ' + added.length + ' leads from Google Sheets (' + c.sheetsId + ')');
      })
      .catch(function (e) {
        showToast('Sheets fetch failed (' + e.message + ') — sample import instead.');
        legacySheetImport && legacySheetImport();
      });
  };
  function normApiRows(txt) {
    try {
      var j = JSON.parse(txt);
      return (j.values || []).slice(1);
    } catch (e) { return parseCsv(txt).slice(1); }
  }

  /* ---------- 2 · Twilio: real calls through your endpoint ----------
     Browsers must not hold Twilio credentials. Point this at a tiny
     serverless function (Vercel/Netlify/Cloudflare) that wraps:
       twilio.calls.create({ to, from, twiml: '<Say>…</Say>' })
     Example body it should accept: { "to": "+1555…", "name": "Jane" }        */
  var legacyDial = window.simulateDial;
  window.simulateDial = function (phone, name) {
    var c = cfg();
    if (!c.twilioEndpoint) {
      showToast('Twilio endpoint not configured — simulated call. Add it in Integrations.');
      return legacyDial && legacyDial(phone, name);
    }
    showToast('Auto-Dialer: requesting a real Twilio call…');
    fetch(c.twilioEndpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ to: phone, name: name })
    })
      .then(function (r) { if (!r.ok) throw new Error('HTTP ' + r.status); return r.json(); })
      .then(function (j) {
        showToast('Twilio call queued' + (j.sid ? ' (' + String(j.sid).slice(0, 8) + '…)' : '') + ' for ' + name);
        logActivity('Twilio call queued for ' + name + ' at ' + phone);
      })
      .catch(function (e) {
        showToast('Twilio endpoint error (' + e.message + ') — simulated call instead.');
        legacyDial && legacyDial(phone, name);
      });
  };

  /* ---------- 3 · Real AI: Ollama (local) or OpenAI ---------- */
  function canned(text) {
    if (text.toLowerCase().includes('email') || text.toLowerCase().includes('draft')) {
      return "Here's a draft: \n\n*Subject: Quick question about [Company]*\n\nHi [Name],\n\nI noticed your team is doing great work in [Industry]. I'd love to show you how Agentik AI can automate your outreach and save 10+ hours a week.\n\nAre you free for a 5-min chat this Thursday?\n\nBest,\n[Your Name]";
    }
    if (text.toLowerCase().includes('summarize') || text.toLowerCase().includes('lead')) {
      return 'You currently have ' + leads.length + ' active leads. Total pipeline value is $' + leads.reduce(function (s, l) { return s + l.value; }, 0).toLocaleString() + '. 2 leads are ready for the auto-dialer.';
    }
    if (text.toLowerCase().includes('dial') || text.toLowerCase().includes('call')) {
      simulateDial('Batch', 'New Leads');
      return "Initiating Auto-Dialer sequence for all 'New' status leads. I will log voicemails and update their status to 'Contacted' automatically.";
    }
    return "I'm processing that request. I can help draft emails, summarize lead data, or trigger the auto-dialer.";
  }
  function askRealAI(text) {
    var c = cfg();
    var sys = 'You are Agentik, a concise CRM assistant inside the Ai Metaverse site. Answer in under 120 words.';
    if (c.aiProvider === 'ollama' && c.ollamaUrl) {
      return fetch(c.ollamaUrl.replace(/\/$/, '') + '/api/chat', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ model: c.ollamaModel || 'llama3.1', stream: false, messages: [{ role: 'system', content: sys }, { role: 'user', content: text }] })
      }).then(function (r) { if (!r.ok) throw new Error('HTTP ' + r.status); return r.json(); })
        .then(function (j) { return j.message && j.message.content; });
    }
    if (c.aiProvider === 'openai' && c.openaiKey) {
      return fetch('https://api.openai.com/v1/chat/completions', {
        method: 'POST', headers: { 'Content-Type': 'application/json', 'Authorization': 'Bearer ' + c.openaiKey },
        body: JSON.stringify({ model: c.openaiModel || 'gpt-4o-mini', messages: [{ role: 'system', content: sys }, { role: 'user', content: text }] })
      }).then(function (r) { if (!r.ok) throw new Error('HTTP ' + r.status); return r.json(); })
        .then(function (j) { return j.choices && j.choices[0] && j.choices[0].message.content; });
    }
    return Promise.resolve(null);
  }
  window.sendMessage = function () {
    var input = document.getElementById('chat-input');
    var text = input.value.trim();
    if (!text) return;
    var chatBody = document.getElementById('chat-body');
    chatBody.innerHTML += '<div class="message user"></div>';
    chatBody.lastChild.textContent = text;
    input.value = '';
    chatBody.scrollTop = chatBody.scrollHeight;
    var c = cfg();
    var live = (c.aiProvider === 'ollama' && c.ollamaUrl) || (c.aiProvider === 'openai' && c.openaiKey);
    var p = live ? askRealAI(text).catch(function () { return null; }) : Promise.resolve(null);
    p.then(function (resp) {
      var answer = resp || canned(text);
      var d = document.createElement('div');
      d.className = 'message ai';
      d.style.whiteSpace = 'pre-line';
      d.textContent = (resp ? '' : '[offline brain] ') + answer;
      chatBody.appendChild(d);
      chatBody.scrollTop = chatBody.scrollHeight;
    });
  };

  /* ---------- Integrations view + persistence ---------- */
  function buildUI() {
    var side = document.querySelector('.crm-embed .sidebar');
    var content = document.querySelector('.crm-embed .content-area');
    if (!side || !content || document.getElementById('nav-integrations')) return;
    var item = document.createElement('div');
    item.className = 'nav-item'; item.id = 'nav-integrations';
    item.innerHTML = '<i class="fa-solid fa-plug"></i> Integrations';
    item.setAttribute('onclick', "switchView('integrations', this)");
    side.insertBefore(item, side.querySelector('.upgrade-banner'));

    var view = document.createElement('div');
    view.id = 'integrations'; view.className = 'view';
    view.innerHTML =
      '<h3 style="margin-bottom:8px;font-family:\'Space Grotesk\'">Real-world integrations</h3>' +
      '<p style="color:var(--text-muted);font-size:.9rem;margin-bottom:20px">To connect this CRM to real-world tools, the simulate… functions were replaced with actual API calls. Save a value below and the matching button goes live; empty values keep the offline simulation. Settings stay in this browser only.</p>' +
      '<div class="stats-grid">' +
        '<div class="stat-card"><h3><i class="fa-brands fa-google"></i> Google Sheets</h3>' +
          '<div class="form-group"><label>Spreadsheet ID</label><input id="int-sheets-id" placeholder="1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"></div>' +
          '<div class="form-group"><label>API key (optional — else sheet must be public)</label><input id="int-sheets-key" type="password" placeholder="AIza…"></div>' +
          '<div class="form-group"><label>Range</label><input id="int-sheets-range" placeholder="A:D"></div>' +
          '<p style="font-size:.8rem;color:var(--text-muted)">“Import Sheets” then fetches real rows via the Sheets API (or the public CSV endpoint).</p>' +
        '</div>' +
        '<div class="stat-card"><h3><i class="fa-solid fa-phone-volume"></i> Twilio auto-dialer</h3>' +
          '<div class="form-group"><label>Call endpoint (POST {to,name}) — local FastAPI: http://localhost:8000/api/dial</label><input id="int-twilio" placeholder="http://localhost:8000/api/dial  (or https://your-app.vercel.app/api/dial)"></div>' +
          '<p style="font-size:.8rem;color:var(--text-muted)">Keep Twilio credentials server-side. py/server.py already implements this endpoint (/api/dial) — run <code>uvicorn py.server:app</code> and paste http://localhost:8000/api/dial, or deploy it to Vercel/Railway and use that URL. “Dial” then queues real calls.</p>' +
        '</div>' +
        '<div class="stat-card"><h3><i class="fa-solid fa-brain"></i> Real AI for the assistant</h3>' +
          '<div class="form-group"><label>Provider</label><select id="int-ai"><option value="mock">Offline brain (default)</option><option value="ollama">Ollama (local)</option><option value="openai">OpenAI</option></select></div>' +
          '<div class="form-group"><label>Ollama URL</label><input id="int-ollama" placeholder="http://localhost:11434"></div>' +
          '<div class="form-group"><label>Ollama model</label><input id="int-ollama-model" placeholder="llama3.1"></div>' +
          '<div class="form-group"><label>OpenAI API key (browser-side — use at your own risk)</label><input id="int-openai-key" type="password" placeholder="sk-…"></div>' +
          '<div class="form-group"><label>OpenAI model</label><input id="int-openai-model" placeholder="gpt-4o-mini"></div>' +
        '</div>' +
      '</div>' +
      '<div class="modal-actions" style="justify-content:flex-start"><button class="btn btn-primary" id="int-save"><i class="fa-solid fa-floppy-disk"></i> Save integrations</button>' +
      '<button class="btn btn-outline" id="int-clear">Clear all</button></div>' +
      '<p style="margin-top:18px;font-size:.8rem;color:var(--text-muted)">Notes: Google Sheets → Sheets API fetches real rows. Auto-Dialer → Twilio API for real phone calls & voicemail drops. Real AI → replace mock chatbot responses with the OpenAI API or a local Ollama instance.</p>';
    content.appendChild(view);

    var c = cfg();
    function val(id) { var el = document.getElementById(id); return el ? el.value.trim() : ''; }
    function set(id, v) { var el = document.getElementById(id); if (el && v) el.value = v; }
    set('int-sheets-id', c.sheetsId); set('int-sheets-key', c.sheetsKey); set('int-sheets-range', c.sheetsRange);
    set('int-twilio', c.twilioEndpoint); set('int-ollama', c.ollamaUrl); set('int-ollama-model', c.ollamaModel);
    set('int-openai-key', c.openaiKey); set('int-openai-model', c.openaiModel);
    var sel = document.getElementById('int-ai'); if (sel && c.aiProvider) sel.value = c.aiProvider;

    document.getElementById('int-save').addEventListener('click', function () {
      saveCfg({
        sheetsId: val('int-sheets-id'), sheetsKey: val('int-sheets-key'), sheetsRange: val('int-sheets-range'),
        twilioEndpoint: val('int-twilio'),
        aiProvider: sel ? sel.value : 'mock',
        ollamaUrl: val('int-ollama'), ollamaModel: val('int-ollama-model'),
        openaiKey: val('int-openai-key'), openaiModel: val('int-openai-model')
      });
      showToast('Integrations saved — live API paths active where configured.');
      logActivity('CRM integrations configuration updated');
    });
    document.getElementById('int-clear').addEventListener('click', function () {
      try { localStorage.removeItem(LS); } catch (e) {}
      ['int-sheets-id', 'int-sheets-key', 'int-sheets-range', 'int-twilio', 'int-ollama', 'int-ollama-model', 'int-openai-key', 'int-openai-model'].forEach(function (id) { var el = document.getElementById(id); if (el) el.value = ''; });
      if (sel) sel.value = 'mock';
      showToast('Integrations cleared — back to offline simulations.');
    });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', buildUI);
  else buildUI();
})();
