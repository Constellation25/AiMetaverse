(() => {
  const TOOLSET_URL = "./data/endless-ai-toolset.json";

  class EndlessAIToolset {
    constructor(runtime) {
      this.runtime = runtime || (typeof window !== "undefined" ? window.C25ModuleRuntime : null);
      this.catalog = [];
      this.loopTimer = null;
      this.loopCycle = 0;
    }

    async loadCatalog(overrideList = null) {
      if (Array.isArray(overrideList)) {
        this.catalog = overrideList;
        return this.catalog;
      }
      if (typeof fetch === "function") {
        const res = await fetch(TOOLSET_URL, { cache: "no-cache" });
        if (!res || !res.ok) {
          throw new Error(`Failed to fetch toolset catalog (${res ? res.status : "no response"})`);
        }
        const json = await res.json();
        if (Array.isArray(json.tools)) {
          this.catalog = json.tools;
        }
      }
      return this.catalog;
    }

    registerIntoRuntime(runtimeInstance = null, overrideList = null) {
      const rt = runtimeInstance || this.runtime || (typeof window !== "undefined" ? window.C25ModuleRuntime : null);
      if (!rt || typeof rt.register !== "function") {
        throw new Error("C25ModuleRuntime is not available to register endless AI tools");
      }
      this.runtime = rt;

      if (Array.isArray(overrideList)) {
        this.catalog = overrideList;
      }

      rt.register("endless_ai", "list", async (payload = {}) => {
        const onlyAi = Boolean(payload && payload.aiOnly);
        const list = onlyAi ? this.catalog.filter((t) => t.aiFocused) : this.catalog;
        return {
          mode: "production-live",
          count: list.length,
          totalCatalog: this.catalog.length,
          loopRunning: Boolean(this.loopTimer),
          loopCycle: this.loopCycle,
          tools: list,
        };
      });

      rt.register("endless_ai", "call", async (payload = {}) => {
        const targetKey = payload && payload.tool ? String(payload.tool) : "";
        const argsPayload = payload && payload.input !== undefined ? payload.input : payload;
        if (!targetKey) {
          throw new Error("endless_ai:call requires payload.tool (e.g. 'store_crm_integrations:askRealAI')");
        }
        const [modId, fnName] = targetKey.includes(":")
          ? targetKey.split(":", 2)
          : ["endless_ai", targetKey];
        return rt.call(modId, fnName, argsPayload, { render: false });
      });

      rt.register("endless_ai", "startLoop", async (payload = {}) => {
        const intervalMs = Math.max(250, Number(payload.intervalMs) || 5000);
        const toolKeys = Array.isArray(payload.tools) && payload.tools.length
          ? payload.tools
          : this.catalog.filter((t) => t.aiFocused).map((t) => t.key);
        this.stopLoop();
        let idx = 0;
        this.loopTimer = setInterval(async () => {
          if (!toolKeys.length) return;
          this.loopCycle += 1;
          const nextKey = toolKeys[idx % toolKeys.length];
          idx += 1;
          const [modId, fnName] = nextKey.split(":", 2);
          try {
            await rt.call(modId, fnName, { cycle: this.loopCycle, prompt: "Endless AI heartbeat" }, { render: false });
          } catch (_) {
            // Keep loop alive across individual tool errors
          }
        }, intervalMs);
        return { started: true, mode: "production-live", intervalMs, queuedTools: toolKeys.length };
      });

      rt.register("endless_ai", "stopLoop", async () => {
        this.stopLoop();
        return { stopped: true, completedCycles: this.loopCycle };
      });

      let bound = 0;
      for (const tool of this.catalog) {
        if (!tool || !tool.moduleId || !tool.fn) continue;
        rt.register(tool.moduleId, tool.fn, async (inputPayload = {}) => {
          const scopeObj = typeof window !== "undefined" ? window : globalThis;
          const liveFn = scopeObj ? scopeObj[tool.fn] : undefined;
          if (typeof liveFn !== "function") {
            throw new Error(`Live function '${tool.fn}' (${tool.key}) is not loaded in runtime scope`);
          }
          const output = await liveFn(inputPayload);
          return {
            key: tool.key,
            file: tool.file,
            fn: tool.fn,
            mode: "production-live",
            output: output === undefined ? null : output,
          };
        });
        bound += 1;
      }

      return { bound };
    }

    stopLoop() {
      if (this.loopTimer) {
        clearInterval(this.loopTimer);
        this.loopTimer = null;
      }
    }
  }

  const toolset = new EndlessAIToolset();
  if (typeof window !== "undefined") {
    window.C25EndlessAIToolset = toolset;
    if (window.C25ModuleRuntime) {
      toolset.registerIntoRuntime(window.C25ModuleRuntime);
    }
  }
  if (typeof module !== "undefined" && module.exports) {
    module.exports = { EndlessAIToolset, toolset };
  }
})();
