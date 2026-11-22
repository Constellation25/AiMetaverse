(() => {
  const MANIFEST_URL = "./data/module-runtime-manifest.json";
  const STATE_URL = "./data/system-state.json";

  class ModuleRuntime {
    constructor() {
      this.handlers = new Map();
      this.manifest = null;
      this.registerCoreHandlers();
    }

    register(moduleId, actionName, fn) {
      const key = `${moduleId}:${actionName}`;
      this.handlers.set(key, fn);
      return key;
    }

    registerCoreHandlers() {
      this.register("system", "status", async () => {
        const res = await fetch(STATE_URL, { cache: "no-cache" });
        if (!res.ok) throw new Error(`HTTP ${res.status} loading system-state.json`);
        return res.json();
      });

      this.register("system", "listModules", async () => {
        if (!this.manifest) {
          const res = await fetch(MANIFEST_URL, { cache: "no-cache" });
          if (!res.ok) throw new Error(`HTTP ${res.status} loading module-runtime-manifest.json`);
          this.manifest = await res.json();
        }
        return this.manifest;
      });

      this.register("system", "resolveRoute", async (payload = {}) => {
        const query = String(payload.route || "").trim();
        const state = await this.call("system", "status", {}, { render: false });
        const routes = Array.isArray(state.data && state.data.routes) ? state.data.routes : [];
        const match = routes.find(
          (r) => r.broken_path === query || r.target_path === query || r.target_url === query
        );
        return {
          query,
          matched: Boolean(match),
          route: match || null,
          totalRoutes: routes.length,
        };
      });

      this.register("system", "activity", async () => {
        const sys = window.C25LiveSystem;
        return {
          entries: sys ? sys.loadActivity() : [],
        };
      });
    }

    async bindDiscoveredModules() {
      const manRes = await this.call("system", "listModules", {}, { render: false });
      const list = (manRes.data && manRes.data.modules) || [];
      for (const mod of list) {
        this.register(mod.id, "inspect", async () => ({
          id: mod.id,
          path: mod.path,
          type: mod.type,
          symbols: mod.symbols,
        }));
      }
      return { boundModules: list.length };
    }

    async call(moduleId, actionName = "inspect", payload = {}, opts = {}) {
      const key = `${moduleId}:${actionName}`;
      let fn = this.handlers.get(key);
      if (!fn && actionName === "inspect") {
        await this.bindDiscoveredModules();
        fn = this.handlers.get(key);
      }
      if (!fn) {
        const errEnvelope = {
          ok: false,
          module: moduleId,
          action: actionName,
          data: null,
          error: `No registered handler for ${key}`,
          durationMs: 0,
          timestamp: new Date().toISOString(),
        };
        if (opts.targetSelector && window.C25LiveSystem) {
          window.C25LiveSystem.renderToEndUser(errEnvelope, opts.targetSelector);
        }
        return errEnvelope;
      }

      if (window.C25LiveSystem && typeof window.C25LiveSystem.deliverCall === "function") {
        return window.C25LiveSystem.deliverCall(moduleId, actionName, fn, payload, opts);
      }

      const startedAt = performance.now();
      try {
        const data = await fn(payload);
        return {
          ok: true,
          module: moduleId,
          action: actionName,
          data,
          error: null,
          durationMs: Math.max(0, Math.round((performance.now() - startedAt) * 100) / 100),
          timestamp: new Date().toISOString(),
        };
      } catch (err) {
        return {
          ok: false,
          module: moduleId,
          action: actionName,
          data: null,
          error: err && err.message ? err.message : String(err),
          durationMs: Math.max(0, Math.round((performance.now() - startedAt) * 100) / 100),
          timestamp: new Date().toISOString(),
        };
      }
    }
  }

  const runtime = new ModuleRuntime();
  window.C25ModuleRuntime = runtime;
})();
