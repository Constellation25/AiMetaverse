(() => {
  const STORAGE_KEY = "c25_aimetaverse_activity_v1";
  const STATE_URL = "./data/system-state.json";

  function nowIso() {
    return new Date().toISOString();
  }

  function loadActivity() {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      const parsed = raw ? JSON.parse(raw) : [];
      return Array.isArray(parsed) ? parsed : [];
    } catch (_) {
      return [];
    }
  }

  function recordActivity(eventType, detail, status = "ok") {
    const entries = loadActivity();
    entries.unshift({
      ts: nowIso(),
      type: String(eventType || "call"),
      status: String(status || "ok"),
      detail: String(detail || "").slice(0, 300),
    });
    const trimmed = entries.slice(0, 100);
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(trimmed));
    } catch (_) {}
    return trimmed;
  }

  function formatResultEnvelope({ ok, moduleName, actionName, data = null, error = null, startedAt = performance.now() }) {
    const durationMs = Math.max(0, Math.round((performance.now() - startedAt) * 100) / 100);
    return {
      ok: Boolean(ok),
      module: String(moduleName || "unknown"),
      action: String(actionName || "default"),
      data,
      error: error ? String(error) : null,
      durationMs,
      timestamp: nowIso(),
    };
  }

  function renderToEndUser(envelope, targetSelector = "#c25-module-output") {
    if (typeof document === "undefined") {
      return envelope;
    }
    const el = document.querySelector(targetSelector);
    if (!el) {
      return envelope;
    }
    const badge = envelope.ok ? "OK" : "ERROR";
    const payloadText = envelope.ok
      ? JSON.stringify(envelope.data, null, 2)
      : `Error: ${envelope.error}`;

    el.dataset.c25Status = badge;
    el.innerHTML = "";

    const header = document.createElement("div");
    header.textContent = `[${badge}] ${envelope.module}.${envelope.action} (${envelope.durationMs}ms)`;

    const pre = document.createElement("pre");
    pre.textContent = payloadText;

    el.appendChild(header);
    el.appendChild(pre);
    return envelope;
  }

  async function fetchSystemState(forceRefresh = false) {
    const cacheMode = forceRefresh ? "reload" : "no-cache";
    const res = await fetch(STATE_URL, { cache: cacheMode });
    if (!res.ok) {
      throw new Error(`Unable to load system-state.json (HTTP ${res.status})`);
    }
    return res.json();
  }

  async function deliverCall(moduleName, actionName, fn, payload = {}, opts = {}) {
    const startedAt = performance.now();
    try {
      const rawResult = await fn(payload);
      const envelope = formatResultEnvelope({
        ok: true,
        moduleName,
        actionName,
        data: rawResult,
        error: null,
        startedAt,
      });
      recordActivity(`${moduleName}.${actionName}`, JSON.stringify(rawResult).slice(0, 200), "ok");
      if (opts.targetSelector) {
        renderToEndUser(envelope, opts.targetSelector);
      }
      return envelope;
    } catch (err) {
      const msg = err && err.message ? err.message : String(err);
      const envelope = formatResultEnvelope({
        ok: false,
        moduleName,
        actionName,
        data: null,
        error: msg,
        startedAt,
      });
      recordActivity(`${moduleName}.${actionName}`, msg, "error");
      if (opts.targetSelector) {
        renderToEndUser(envelope, opts.targetSelector);
      }
      return envelope;
    }
  }

  window.C25LiveSystem = {
    loadActivity,
    recordActivity,
    formatResultEnvelope,
    renderToEndUser,
    fetchSystemState,
    deliverCall,
  };
})();
