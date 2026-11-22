(() => {
  const MANIFEST_URL = "./data/module-runtime-manifest.json";
  const STATE_URL = "./data/system-state.json";

  const HARNESS_SPECS = [
    {
      moduleId: "store_tailwindcdn",
      scriptPath: "store/tailwindcdn.js",
      targetPage: "index.html",
      kind: "browser-bundle",
      notes: "Tailwind CDN bundle loaded via <script> tag.",
    },
    {
      moduleId: "tools_tpr",
      scriptPath: "tools/tpr.js",
      targetPage: "prompter/index.html",
      kind: "jsdom-harness",
      notes: "Loads prompter/index.html in JSDOM and tracks errors and copied state.",
    },
    {
      moduleId: "tools_tvl",
      scriptPath: "tools/tvl.js",
      targetPage: "voice-lipsync/index.html",
      kind: "jsdom-harness",
      notes: "Loads voice-lipsync/index.html in JSDOM and tracks errors and downloads.",
    },
    {
      moduleId: "tools_tvt",
      scriptPath: "tools/tvt.js",
      targetPage: "twin-studio/index.html",
      kind: "jsdom-harness",
      notes: "Loads twin-studio/index.html in JSDOM and tracks errors, spoke, and listened counts.",
    },
  ];

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
        const sys = typeof window !== "undefined" ? window.C25LiveSystem : null;
        return {
          entries: sys ? sys.loadActivity() : [],
        };
      });

      this.registerToolsetActions();
      this.registerHarnessVerifiedStoreFunctions();
    }

    hasScriptInDom(relPath) {
      if (typeof document === "undefined" || typeof document.querySelectorAll !== "function") {
        return false;
      }
      const base = relPath.split("/").pop();
      return Array.from(document.querySelectorAll("script[src]")).some((el) => {
        const src = el.getAttribute("src") || "";
        return src === relPath || src === `./${relPath}` || src.endsWith(`/${base}`);
      });
    }

    async probeTargetPage(targetPage) {
      if (typeof fetch !== "function") return { reachable: null, status: null };
      try {
        const res = await fetch(`./${targetPage}`, { cache: "no-cache" });
        return { reachable: res.ok, status: res.status };
      } catch (err) {
        return { reachable: false, status: null, error: err && err.message ? err.message : String(err) };
      }
    }

    runNodeHarness(scriptPath) {
      if (typeof process === "undefined" || !process.versions || !process.versions.node) {
        return null;
      }
      try {
        const { execFileSync } = require("child_process");
        const path = require("path");
        const repoRoot = path.join(process.env.HOME || ".", "AiMetaverse");
        const fullScript = path.join(repoRoot, scriptPath);
        const stdout = execFileSync(process.execPath, [fullScript], {
          cwd: repoRoot,
          encoding: "utf8",
          timeout: 15000,
        });
        return {
          executed: true,
          cwd: repoRoot,
          stdout: stdout.trim(),
        };
      } catch (err) {
        return {
          executed: false,
          error: err && err.message ? err.message : String(err),
          stdout: err && err.stdout ? String(err.stdout).trim() : "",
          stderr: err && err.stderr ? String(err.stderr).trim() : "",
        };
      }
    }

    registerToolsetActions() {
      for (const spec of HARNESS_SPECS) {
        this.register(spec.moduleId, "inspect", async () => {
          const targetProbe = await this.probeTargetPage(spec.targetPage);
          return {
            moduleId: spec.moduleId,
            scriptPath: spec.scriptPath,
            targetPage: spec.targetPage,
            kind: spec.kind,
            loadedInDom: this.hasScriptInDom(spec.scriptPath),
            targetPageProbe: targetProbe,
            supportedActions: ["inspect", "checkTarget", "run"],
            notes: spec.notes,
          };
        });

        this.register(spec.moduleId, "checkTarget", async () => {
          const targetProbe = await this.probeTargetPage(spec.targetPage);
          return {
            moduleId: spec.moduleId,
            targetPage: spec.targetPage,
            ...targetProbe,
          };
        });

        this.register(spec.moduleId, "run", async (payload = {}) => {
          const targetProbe = await this.probeTargetPage(spec.targetPage);
          if (spec.kind === "jsdom-harness") {
            const harness = this.runNodeHarness(spec.scriptPath);
            return {
              moduleId: spec.moduleId,
              scriptPath: spec.scriptPath,
              targetPage: spec.targetPage,
              targetPageProbe: targetProbe,
              harness,
              payload,
            };
          }
          return {
            moduleId: spec.moduleId,
            scriptPath: spec.scriptPath,
            targetPage: spec.targetPage,
            targetPageProbe: targetProbe,
            loadedInDom: this.hasScriptInDom(spec.scriptPath),
            payload,
          };
        });
      }
    }

    registerHarnessVerifiedStoreFunctions() {
      const verifiedStoreFunctions = {};
      for (const [scriptPath, fns] of Object.entries(verifiedStoreFunctions)) {
        const moduleId = scriptPath.replace(/\.(m?js|ts|jsx|tsx|html)$/i, "").replace(/[^A-Za-z0-9]+/g, "_").replace(/^_+|_+$/g, "").toLowerCase();
        this.register(moduleId, "listVerifiedFunctions", async () => ({
          moduleId,
          scriptPath,
          verifiedFunctions: fns,
        }));
      }
        // No passing store AI functions found in report.
    }

    async bindDiscoveredModules() {
      const manRes = await this.call("system", "listModules", {}, { render: false });
      const list = (manRes.data && manRes.data.modules) || [];
      for (const mod of list) {
        if (!this.handlers.has(`${mod.id}:inspect`)) {
          this.register(mod.id, "inspect", async () => ({
            id: mod.id,
            path: mod.path,
            type: mod.type,
            symbols: mod.symbols,
          }));
        }
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
        if (opts.targetSelector && typeof window !== "undefined" && window.C25LiveSystem) {
          window.C25LiveSystem.renderToEndUser(errEnvelope, opts.targetSelector);
        }
        return errEnvelope;
      }

      const liveSys = typeof window !== "undefined" ? window.C25LiveSystem : null;
      if (liveSys && typeof liveSys.deliverCall === "function") {
        return liveSys.deliverCall(moduleId, actionName, fn, payload, opts);
      }

      const startedAt = typeof performance !== "undefined" && performance.now ? performance.now() : Date.now();
      const nowMs = () => (typeof performance !== "undefined" && performance.now ? performance.now() : Date.now());
      try {
        const data = await fn(payload);
        return {
          ok: true,
          module: moduleId,
          action: actionName,
          data,
          error: null,
          durationMs: Math.max(0, Math.round((nowMs() - startedAt) * 100) / 100),
          timestamp: new Date().toISOString(),
        };
      } catch (err) {
        return {
          ok: false,
          module: moduleId,
          action: actionName,
          data: null,
          error: err && err.message ? err.message : String(err),
          durationMs: Math.max(0, Math.round((nowMs() - startedAt) * 100) / 100),
          timestamp: new Date().toISOString(),
        };
      }
    }
  }

  const runtime = new ModuleRuntime();
  if (typeof window !== "undefined") {
    window.C25ModuleRuntime = runtime;
  }
  if (typeof module !== "undefined" && module.exports) {
    module.exports = { ModuleRuntime, runtime };
  }
})();
