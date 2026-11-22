(() => {
  const GRAPH_URL = "./data/platform-token-graph.json";
  const MANIFEST_URL = "./data/module-runtime-manifest.json";
  const STATE_URL = "./data/system-state.json";

  async function sha256Hex(input) {
    const str = String(input);
    if (typeof crypto !== "undefined" && crypto.subtle && typeof TextEncoder !== "undefined") {
      const buf = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(str));
      return Array.from(new Uint8Array(buf))
        .map((b) => b.toString(16).padStart(2, "0"))
        .join("");
    }
    let h = 2166136261;
    for (let i = 0; i < str.length; i += 1) {
      h ^= str.charCodeAt(i);
      h = Math.imul(h, 16777619);
    }
    return (h >>> 0).toString(16).padStart(8, "0").repeat(8).slice(0, 64);
  }

  async function issueCallToken(scope, subject) {
    const nonceBytes = new Uint8Array(12);
    if (typeof crypto !== "undefined" && crypto.getRandomValues) {
      crypto.getRandomValues(nonceBytes);
    } else {
      for (let i = 0; i < nonceBytes.length; i += 1) {
        nonceBytes[i] = (i * 37 + Date.now()) & 0xff;
      }
    }
    const nonce = Array.from(nonceBytes).map((b) => b.toString(16).padStart(2, "0")).join("");
    const hex = await sha256Hex(`${scope}:${subject}:${Date.now()}:${nonce}`);
    return `tok_${hex.slice(0, 16)}`;
  }

  class PlatformBus {
    constructor() {
      this.graph = null;
      this.manifest = null;
      this.state = null;
      this.sessionToken = null;
      this.apiRoutes = new Map();
    }

    registerApiEndpoint(name, handler) {
      this.apiRoutes.set(String(name), handler);
      return name;
    }

    registerDefaultEndpoints() {
      this.registerApiEndpoint("state.get", async () => {
        const res = await fetch(STATE_URL, { cache: "no-cache" });
        if (!res.ok) throw new Error(`HTTP ${res.status} on ${STATE_URL}`);
        this.state = await res.json();
        return this.state;
      });

      this.registerApiEndpoint("manifest.get", async () => {
        const res = await fetch(MANIFEST_URL, { cache: "no-cache" });
        if (!res.ok) throw new Error(`HTTP ${res.status} on ${MANIFEST_URL}`);
        this.manifest = await res.json();
        return this.manifest;
      });

      this.registerApiEndpoint("graph.get", async () => {
        const res = await fetch(GRAPH_URL, { cache: "no-cache" });
        if (!res.ok) throw new Error(`HTTP ${res.status} on ${GRAPH_URL}`);
        this.graph = await res.json();
        return this.graph;
      });

      this.registerApiEndpoint("route.lookup", async (payload = {}) => {
        const q = String(payload.query || "").trim();
        const st = this.state || (await this.apiRoutes.get("state.get")());
        const routes = Array.isArray(st.routes) ? st.routes : [];
        const found = routes.find(
          (r) => r.broken_path === q || r.target_path === q || r.target_url === q
        );
        return { query: q, found: Boolean(found), route: found || null };
      });
    }

    async init() {
      this.registerDefaultEndpoints();
      this.sessionToken = await issueCallToken("session", "aimetaverse-platform");
      const [gRes, mRes, sRes] = await Promise.allSettled([
        this.apiRoutes.get("graph.get")(),
        this.apiRoutes.get("manifest.get")(),
        this.apiRoutes.get("state.get")(),
      ]);
      if (window.C25ModuleRuntime && typeof window.C25ModuleRuntime.bindDiscoveredModules === "function") {
        await window.C25ModuleRuntime.bindDiscoveredModules();
      }
      return {
        sessionToken: this.sessionToken,
        graphLoaded: gRes.status === "fulfilled",
        manifestLoaded: mRes.status === "fulfilled",
        stateLoaded: sRes.status === "fulfilled",
        registeredEndpoints: Array.from(this.apiRoutes.keys()),
      };
    }

    getDependencyChain(nodePath) {
      if (!this.graph || !this.graph.nodes || !this.graph.nodes[nodePath]) {
        return { node: nodePath, token: null, dependsOn: [], reverseDependents: [] };
      }
      const target = this.graph.nodes[nodePath];
      const reverseDependents = Object.entries(this.graph.nodes)
        .filter(([, info]) => Array.isArray(info.resolved_depends_on) && info.resolved_depends_on.includes(nodePath))
        .map(([k, info]) => ({ path: k, token: info.token }));

      return {
        node: nodePath,
        token: target.token,
        dependsOn: target.resolved_depends_on || [],
        reverseDependents,
      };
    }

    async invoke(target, payload = {}, opts = {}) {
      const callToken = await issueCallToken("invoke", target);
      const startedAt = performance.now();

      try {
        let data;
        if (this.apiRoutes.has(target)) {
          data = await this.apiRoutes.get(target)(payload);
        } else if (window.C25ModuleRuntime && typeof window.C25ModuleRuntime.call === "function") {
          const [modId, actionName = "inspect"] = String(target).split(":");
          const modRes = await window.C25ModuleRuntime.call(modId, actionName, payload, { render: false });
          if (!modRes.ok) {
            throw new Error(modRes.error || `Module call failed for ${target}`);
          }
          data = modRes.data;
        } else {
          throw new Error(`Unknown toolset or API route: ${target}`);
        }

        const envelope = {
          ok: true,
          token: callToken,
          sessionToken: this.sessionToken,
          target,
          data,
          error: null,
          durationMs: Math.max(0, Math.round((performance.now() - startedAt) * 100) / 100),
          timestamp: new Date().toISOString(),
        };

        if (window.C25LiveSystem) {
          window.C25LiveSystem.recordActivity(`bus:${target}`, `token=${callToken}`, "ok");
          if (opts.targetSelector) {
            window.C25LiveSystem.renderToEndUser(envelope, opts.targetSelector);
          }
        }
        return envelope;
      } catch (err) {
        const msg = err && err.message ? err.message : String(err);
        const envelope = {
          ok: false,
          token: callToken,
          sessionToken: this.sessionToken,
          target,
          data: null,
          error: msg,
          durationMs: Math.max(0, Math.round((performance.now() - startedAt) * 100) / 100),
          timestamp: new Date().toISOString(),
        };
        if (window.C25LiveSystem) {
          window.C25LiveSystem.recordActivity(`bus:${target}`, msg, "error");
          if (opts.targetSelector) {
            window.C25LiveSystem.renderToEndUser(envelope, opts.targetSelector);
          }
        }
        return envelope;
      }
    }
  }

  window.C25PlatformBus = new PlatformBus();
})();
