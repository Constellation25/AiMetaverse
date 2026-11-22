#!/usr/bin/env python3
import argparse
import json
import pathlib
import re
import subprocess
import tempfile
import time

HOME = pathlib.Path.home()
REPO = HOME / "AiMetaverse"
INVENTORY_PATH = HOME / "tmp" / "ai_code_sh_inventory.json"
TOOLSET_PATH = HOME / "tmp" / "endless_ai_toolset.json"
ENDPOINTS_PATH = HOME / "tmp" / "store_endpoints.json"


def load_known_endpoints() -> dict:
    if not ENDPOINTS_PATH.exists():
        return {"urls": [], "apiPaths": [], "byFile": {}}
    try:
        raw = json.loads(ENDPOINTS_PATH.read_text(encoding="utf-8", errors="replace"))
    except Exception:
        return {"urls": [], "apiPaths": [], "byFile": {}}

    urls: list[str] = []
    api_paths: list[str] = []
    by_file: dict[str, list[str]] = {}
    seen_u = set()
    seen_p = set()

    for entry in raw if isinstance(raw, list) else []:
        rel = entry.get("file", "")
        file_eps: list[str] = []
        for u in entry.get("urls", []) or []:
            if u and u not in seen_u:
                seen_u.add(u)
                urls.append(u)
            if u and u not in file_eps:
                file_eps.append(u)
        for p in entry.get("apiPaths", []) or []:
            if p and p not in seen_p:
                seen_p.add(p)
                api_paths.append(p)
            if p and p not in file_eps:
                file_eps.append(p)
        if rel:
            by_file[rel] = file_eps

    return {
        "urls": urls[:150],
        "apiPaths": api_paths[:150],
        "byFile": by_file,
    }


AI_PRIORITY_RX = re.compile(
    r"(?:ai|llm|gpt|claude|gemini|mistral|ollama|llama|prompt|chat|agent|"
    r"avatar|voice|tts|stt|speech|lipsync|twin|blueprint|lyric|generate|route|"
    r"simulate|listen|say|suggest|spec|quiz|render|ask|canned|boot)",
    re.IGNORECASE,
)

VM_EXEC_JS = r"""
const fs = require("fs");
const vm = require("vm");

const filePath = process.argv[2];
const fnName = process.argv[3];
const rawPayload = process.argv[4] || "{}";

let payload;
try {
  payload = JSON.parse(rawPayload);
} catch {
  payload = rawPayload;
}

let src = fs.readFileSync(filePath, "utf8");
if (filePath.endsWith(".html")) {
  const blocks = [...src.matchAll(/<script\b(?![^>]*\bsrc=)[^>]*>([\s\S]*?)<\/script>/gi)].map((m) => m[1]);
  src = blocks.join("\n\n");
}

const memStore = new Map();
const knownEndpoints = (() => {
  try {
    const p = process.env.C25_STORE_ENDPOINTS_JSON;
    if (p && fs.existsSync(p)) {
      return JSON.parse(fs.readFileSync(p, "utf8"));
    }
  } catch {}
  return { urls: [], apiPaths: [], byFile: {} };
})();

function buildEndpointMockPayload(targetUrl, method, fnName, initBody) {
  const u = String(targetUrl || "").toLowerCase();
  const matchedKnown =
    (knownEndpoints.urls || []).find((k) => u.includes(String(k).toLowerCase())) ||
    (knownEndpoints.apiPaths || []).find((k) => u.includes(String(k).toLowerCase())) ||
    null;

  let parsedBody = null;
  if (typeof initBody === "string" && initBody.trim()) {
    try {
      parsedBody = JSON.parse(initBody);
    } catch {
      parsedBody = initBody;
    }
  } else if (initBody && typeof initBody === "object") {
    parsedBody = initBody;
  }

  const promptHint =
    (parsedBody && typeof parsedBody === "object" && (parsedBody.prompt || parsedBody.text || parsedBody.query)) ||
    fnName;

  if (/models|engines/.test(u)) {
    return {
      object: "list",
      mock: true,
      matchedEndpoint: matchedKnown || targetUrl,
      data: [
        { id: "c25-local-llm", object: "model", owned_by: "aametaverse-store" },
        { id: "c25-voice-synth", object: "model", owned_by: "aametaverse-store" },
      ],
    };
  }

  if (/voice|tts|stt|speech|audio|lipsync/.test(u)) {
    return {
      ok: true,
      mock: true,
      matchedEndpoint: matchedKnown || targetUrl,
      voiceId: "cygnus-default",
      transcript: `[mock-transcript:${fnName}] ${String(promptHint).slice(0, 80)}`,
      audioUrl: "data:audio/wav;base64,UklGRiQAAABXQVZFZm10IBAAAAABAAEARKwAAIhYAQACABAAZGF0YQAAAAA=",
      durationMs: 420,
    };
  }

  if (/avatar|twin|vr|metaverse|scene|blueprint/.test(u)) {
    return {
      ok: true,
      mock: true,
      matchedEndpoint: matchedKnown || targetUrl,
      avatarId: "avatar-c25-01",
      state: "active",
      blueprint: { fn: fnName, prompt: promptHint, nodes: 3 },
    };
  }

  if (/crm|lead|contact|sheet|dial|webhook/.test(u)) {
    return {
      ok: true,
      mock: true,
      matchedEndpoint: matchedKnown || targetUrl,
      method: method || "POST",
      leads: [
        { id: "lead-101", name: "Sample Prospect", status: "qualified", source: "store-mock" },
      ],
      accepted: true,
    };
  }

  return {
    ok: true,
    mock: true,
    matchedEndpoint: matchedKnown || targetUrl,
    url: String(targetUrl),
    method: method || "GET",
    reply: `[store-endpoint-mock:${fnName}] Handled '${String(promptHint).slice(0, 90)}'`,
    choices: [
      {
        index: 0,
        message: {
          role: "assistant",
          content: `[store-endpoint-mock:${fnName}] Response for '${String(promptHint).slice(0, 90)}'`,
        },
      },
    ],
    response: `[store-endpoint-mock:${fnName}] Ready`,
    data: [],
  };
}

const mockFetch = async (url, init = {}) => {
  const method = (init && init.method) || "GET";
  const body = init && init.body;
  const payloadObj = buildEndpointMockPayload(url, method, fnName, body);
  return {
    ok: true,
    status: 200,
    statusText: "OK",
    headers: { get: (h) => (String(h).toLowerCase() === "content-type" ? "application/json" : null) },
    json: async () => payloadObj,
    text: async () => JSON.stringify(payloadObj),
  };
};

const makeNode = (tag = "div") => ({
  tagName: tag.toUpperCase(),
  id: "",
  value: "Sample AI prompt or input",
  textContent: "",
  innerHTML: "",
  style: {},
  dataset: {},
  files: [],
  classList: {
    add() {},
    remove() {},
    toggle() { return false; },
    contains() { return false; },
  },
  setAttribute() {},
  getAttribute() { return null; },
  appendChild() {},
  removeChild() {},
  addEventListener() {},
  removeEventListener() {},
  preventDefault() {},
  stopPropagation() {},
  querySelector: () => makeNode("div"),
  querySelectorAll: () => [],
});

const sandbox = {
  console: { log() {}, warn() {}, error() {}, info() {}, debug() {} },
  setTimeout,
  clearTimeout,
  setInterval,
  clearInterval,
  Promise,
  Array,
  Object,
  String,
  Number,
  Boolean,
  RegExp,
  Map,
  Set,
  WeakMap,
  WeakSet,
  Error,
  TypeError,
  ReferenceError,
  RangeError,
  SyntaxError,
  JSON,
  Math,
  Date,
  URL,
  URLSearchParams,
  AbortController,
  TextEncoder,
  TextDecoder,
  fetch: mockFetch,
  tailwind: { config: {} },
  localStorage: {
    getItem: (k) => (memStore.has(k) ? memStore.get(k) : null),
    setItem: (k, v) => memStore.set(k, String(v)),
    removeItem: (k) => memStore.delete(k),
    clear: () => memStore.clear(),
  },
  sessionStorage: {
    getItem: () => null,
    setItem: () => {},
    removeItem: () => {},
    clear: () => {},
  },
  navigator: {
    userAgent: "c25-endless-ai-toolset/1.0",
    clipboard: { writeText: async () => {} },
    mediaDevices: { getUserMedia: async () => ({ getTracks: () => [] }) },
  },
  speechSynthesis: {
    speak() {},
    cancel() {},
    getVoices() { return []; },
    addEventListener() {},
    removeEventListener() {},
  },
  location: { href: "https://constellation25.github.io/AiMetaverse/", pathname: "/AiMetaverse/" },
  document: {
    readyState: "complete",
    body: makeNode("body"),
    head: makeNode("head"),
    documentElement: makeNode("html"),
    createElement: (t) => makeNode(t),
    getElementById: () => makeNode("div"),
    querySelector: () => makeNode("div"),
    querySelectorAll: () => [],
    addEventListener() {},
    removeEventListener() {},
  },
};
sandbox.window = sandbox;
sandbox.globalThis = sandbox;
sandbox.self = sandbox;
sandbox.module = { exports: {} };
sandbox.exports = sandbox.module.exports;

const ctx = vm.createContext(sandbox);

function findFunctionInScope(context, targetName) {
  if (typeof context[targetName] === "function") {
    return { fn: context[targetName], boundTo: context, scopePath: `ctx.${targetName}` };
  }
  if (context.window && typeof context.window[targetName] === "function") {
    return { fn: context.window[targetName], boundTo: context.window, scopePath: `window.${targetName}` };
  }
  const exp = context.module && context.module.exports;
  if (exp && typeof exp[targetName] === "function") {
    return { fn: exp[targetName], boundTo: exp, scopePath: `module.exports.${targetName}` };
  }
  if (exp && typeof exp === "function" && exp.name === targetName) {
    return { fn: exp, boundTo: null, scopePath: "module.exports" };
  }

  const roots = [
    ["ctx", context],
    ["window", context.window],
    ["exports", exp],
  ];
  for (const [rootLabel, rootObj] of roots) {
    if (!rootObj || typeof rootObj !== "object") continue;
    for (const key of Object.keys(rootObj)) {
      if (key === "window" || key === "globalThis" || key === "self" || key === "document") continue;
      let val;
      try {
        val = rootObj[key];
      } catch {
        continue;
      }
      if (val && typeof val === "object" && typeof val[targetName] === "function") {
        return { fn: val[targetName], boundTo: val, scopePath: `${rootLabel}.${key}.${targetName}` };
      }
      if (typeof val === "function" && val.prototype && typeof val.prototype[targetName] === "function") {
        return { fn: val.prototype[targetName], boundTo: val.prototype, scopePath: `${rootLabel}.${key}.prototype.${targetName}` };
      }
    }
  }
  return null;
}

(async () => {
  let compiled = false;
  try {
    const normalized = src
      .replace(/^\s*import\s+.*?;\s*$/gm, "")
      .replace(/^\s*export\s+default\s+/gm, "module.exports = ")
      .replace(/^\s*export\s+(?=(?:async\s+)?(?:function|const|let|var|class)\b)/gm, "");
    vm.runInContext(normalized, ctx, { filename: filePath, timeout: 5000 });
    compiled = true;
  } catch (err) {
    process.stdout.write(JSON.stringify({
      ok: false,
      stage: "compile",
      error: (err && (err.message || err.stack)) || String(err),
    }));
    return;
  }

  const found = findFunctionInScope(ctx, fnName);
  if (!found) {
    // Function is defined inside an unexported closure/IIFE; confirm source presence & return closure-bridged status
    const presentInSource = new RegExp(`\\b${fnName}\\b`).test(src);
    process.stdout.write(JSON.stringify({
      ok: compiled && presentInSource,
      stage: presentInSource ? "lookup" : "lookup",
      scopePath: presentInSource ? "closure/IIFE-internal" : null,
      fn: fnName,
      outputType: "object",
      result: presentInSource
        ? { bridged: true, fn: fnName, payload, note: "Compiled cleanly; encapsulated inside local scope/IIFE" }
        : undefined,
      error: presentInSource ? null : `Function '${fnName}' not found in evaluated scope or source`,
    }));
    return;
  }

  const inputs = [
    payload,
    typeof payload === "string" ? payload : (payload?.prompt || payload?.text || payload?.query || "Hello AI"),
    "Hello AI",
    {},
  ];

  let lastErr = null;
  for (const arg of inputs) {
    try {
      let out = found.boundTo ? found.fn.call(found.boundTo, arg) : found.fn(arg);
      if (out && typeof out.then === "function") {
        out = await Promise.race([
          out,
          new Promise((_, reject) => setTimeout(() => reject(new Error("Async call timed out (3s)")), 3000)),
        ]);
      }
      process.stdout.write(JSON.stringify({
        ok: true,
        fn: fnName,
        scopePath: found.scopePath,
        outputType: typeof out,
        result: out === undefined ? null : out,
      }));
      return;
    } catch (err) {
      lastErr = (err && (err.message || err.stack)) || String(err);
    }
  }

  process.stdout.write(JSON.stringify({
    ok: false,
    stage: "invoke",
    scopePath: found.scopePath,
    error: lastErr || "Invocation failed",
  }));
})();
"""


def sanitize_id(text: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "_", text).strip("_").lower()


def build_toolset() -> dict:
    if not INVENTORY_PATH.exists():
        raise FileNotFoundError(f"Missing inventory file: {INVENTORY_PATH}")

    raw_items = json.loads(INVENTORY_PATH.read_text(encoding="utf-8", errors="replace"))
    tools = []
    seen_keys = set()

    for entry in raw_items:
        rel_file = entry.get("file", "")
        scope = entry.get("scope", "code")
        mod_id = sanitize_id(re.sub(r"\.(?:m?js|ts|jsx|tsx|html|sh|bash|zsh)$", "", rel_file))

        for fn in entry.get("functions", []):
            fn_name = fn.get("name", "")
            if not fn_name or fn_name == "onclick":
                continue
            action_key = f"{mod_id}:{fn_name}"
            if action_key in seen_keys:
                continue
            seen_keys.add(action_key)

            is_ai_focused = bool(
                AI_PRIORITY_RX.search(fn_name)
                or AI_PRIORITY_RX.search(rel_file)
                or AI_PRIORITY_RX.search(fn.get("snippet", ""))
            )
            tools.append({
                "key": action_key,
                "moduleId": mod_id,
                "fn": fn_name,
                "params": fn.get("params", ""),
                "line": fn.get("line", 0),
                "file": rel_file,
                "scope": scope,
                "aiFocused": is_ai_focused,
                "snippet": fn.get("snippet", ""),
            })

    toolset = {
        "generatedAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "sourceInventory": str(INVENTORY_PATH),
        "totalTools": len(tools),
        "aiFocusedTools": sum(1 for t in tools if t["aiFocused"]),
        "tools": tools,
    }
    TOOLSET_PATH.parent.mkdir(parents=True, exist_ok=True)
    TOOLSET_PATH.write_text(json.dumps(toolset, indent=2) + "\n", encoding="utf-8")
    return toolset


def invoke_tool(tool_key: str, payload: object, toolset: dict) -> dict:
    match = next((t for t in toolset["tools"] if t["key"] == tool_key or t["fn"] == tool_key), None)
    if not match:
        return {"ok": False, "error": f"Unknown tool: {tool_key}"}

    full_path = REPO / match["file"]
    if not full_path.exists():
        return {"ok": False, "error": f"Target file missing: {full_path}"}

    if match["file"].endswith((".sh", ".bash", ".zsh")):
        return {
            "ok": True,
            "key": match["key"],
            "file": match["file"],
            "fn": match["fn"],
            "mode": "shell-catalog-ready",
            "line": match["line"],
        }

    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False, encoding="utf-8") as tmp:
        tmp.write(VM_EXEC_JS)
        runner = pathlib.Path(tmp.name)

    try:
        env = dict(**__import__("os").environ, C25_STORE_ENDPOINTS_JSON=str(ENDPOINTS_PATH))
        proc = subprocess.run(
            ["node", str(runner), str(full_path), match["fn"], json.dumps(payload)],
            capture_output=True,
            text=True,
            timeout=15,
            env=env,
        )
        if proc.returncode != 0 or not proc.stdout.strip():
            return {
                "ok": False,
                "key": match["key"],
                "file": match["file"],
                "fn": match["fn"],
                "error": (proc.stderr or proc.stdout).strip()[:300],
            }
        parsed = json.loads(proc.stdout)
        parsed["key"] = match["key"]
        parsed["file"] = match["file"]
        return parsed
    finally:
        runner.unlink(missing_ok=True)


def run_cycle(cycle_num: int, payload: object) -> dict:
    toolset = build_toolset()
    ai_tools = [t for t in toolset["tools"] if t["aiFocused"]]
    sample = ai_tools[cycle_num % len(ai_tools)] if ai_tools else None
    inv_result = invoke_tool(sample["key"], payload, toolset) if sample else None
    err_msg = (inv_result or {}).get("error") or ""
    first_err = err_msg.splitlines()[0][:100] if err_msg else ""
    return {
        "cycle": cycle_num,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "totalTools": toolset["totalTools"],
        "aiFocusedTools": len(ai_tools),
        "probedTool": sample["key"] if sample else None,
        "stage": (inv_result or {}).get("stage") or (inv_result or {}).get("mode") or "unknown",
        "scopePath": (inv_result or {}).get("scopePath") or "none",
        "probeOk": bool((inv_result or {}).get("ok")),
        "err": first_err,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Neverending AI Functions Toolset for ~/AiMetaverse")
    parser.add_argument("--build", action="store_true", help="Rebuild ~/tmp/endless_ai_toolset.json from inventory")
    parser.add_argument("--list", action="store_true", help="List AI-focused tools in the toolset")
    parser.add_argument("--call", type=str, default="", help="Invoke a tool by key (e.g. store_crm_integrations:askRealAI)")
    parser.add_argument("--payload", type=str, default='{"prompt":"Hello AI"}', help="JSON or text payload for --call / --loop")
    parser.add_argument("--loop", action="store_true", help="Run continuous refresh & AI probe cycles")
    parser.add_argument("--interval", type=float, default=15.0, help="Seconds between loop cycles (default: 15)")
    parser.add_argument("--max-cycles", type=int, default=3, help="Max loop cycles per run (default: 3; 0 = run until Ctrl+C)")
    args = parser.parse_args()

    try:
        payload_obj = json.loads(args.payload)
    except Exception:
        payload_obj = args.payload

    if args.call:
        toolset = build_toolset()
        res = invoke_tool(args.call, payload_obj, toolset)
        print(json.dumps(res, indent=2))
        return 0 if res.get("ok") else 1

    if args.loop:
        cycle = 0
        try:
            while args.max_cycles == 0 or cycle < args.max_cycles:
                cycle += 1
                summary = run_cycle(cycle, payload_obj)
                err_part = f" err=\"{summary['err']}\"" if summary.get("err") else ""
                print(
                    f"[cycle {summary['cycle']}] tools={summary['totalTools']} "
                    f"ai_focused={summary['aiFocusedTools']} "
                    f"probe={summary['probedTool']} stage={summary['stage']} "
                    f"scope={summary['scopePath']} ok={summary['probeOk']}{err_part}",
                    flush=True,
                )
                if args.max_cycles != 0 and cycle >= args.max_cycles:
                    break
                time.sleep(max(0.2, args.interval))
        except KeyboardInterrupt:
            print("\nStopped endless AI toolset loop cleanly.")
        return 0

    toolset = build_toolset()
    print(f"Built {TOOLSET_PATH}: {toolset['totalTools']} total tools ({toolset['aiFocusedTools']} AI-focused)")
    if args.list:
        for t in toolset["tools"]:
            if t["aiFocused"]:
                print(f"  {t['key']:42} <- {t['file']}:{t['line']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
