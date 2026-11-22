#!/usr/bin/env python3
import argparse
import html.parser
import json
import pathlib
import re
import subprocess
import sys
import tempfile

REPO = pathlib.Path.home() / "AiMetaverse"
STORE_DIR = REPO / "store"
DEFAULT_INVENTORY = pathlib.Path.home() / "tmp" / "store_ai_inventory.json"
DEFAULT_REPORT = pathlib.Path.home() / "tmp" / "store_ai_harness_report.json"

AI_KW_RX = re.compile(
    r"\b(?:ai|llm|gpt|claude|gemini|mistral|ollama|llama|embedding|embeddings|vector|"
    r"prompt|systemPrompt|completion|completions|chat|agent|agents|inference|model|"
    r"models|voice|tts|stt|speech|lipsync|avatar|vision|imageGen|generateImage|"
    r"summarize|translate|transcribe|classify|rag|token|tokens|stream|openai|"
    r"anthropic|huggingface|hf_)\b",
    re.IGNORECASE,
)

FUNC_PATTERNS = [
    re.compile(r"(?:export\s+)?(?:async\s+)?function\s+([A-Za-z_$][A-Za-z0-9_$]*)\s*\(([^)]*)\)"),
    re.compile(r"(?:const|let|var)\s+([A-Za-z_$][A-Za-z0-9_$]*)\s*=\s*(?:async\s*)?\(([^)]*)\)\s*=>"),
    re.compile(r"(?:const|let|var)\s+([A-Za-z_$][A-Za-z0-9_$]*)\s*=\s*(?:async\s*)?function\s*\(([^)]*)\)"),
    re.compile(r"(?:window|globalThis)\.([A-Za-z_$][A-Za-z0-9_$]*)\s*=\s*(?:async\s*)?(?:function|\([^)]*\)\s*=>)"),
]


class InlineScriptExtractor(html.parser.HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._in_script = False
        self._has_src = False
        self._buf: list[str] = []
        self.blocks: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() == "script":
            attr_map = {k.lower(): v for k, v in attrs if k}
            self._in_script = True
            self._has_src = bool(attr_map.get("src"))
            self._buf = []

    def handle_data(self, data: str) -> None:
        if self._in_script and not self._has_src:
            self._buf.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "script" and self._in_script:
            if not self._has_src:
                joined = "".join(self._buf).strip()
                if joined:
                    self.blocks.append(joined)
            self._in_script = False
            self._has_src = False
            self._buf = []


def extract_inline_js(html_text: str) -> str:
    parser = InlineScriptExtractor()
    try:
        parser.feed(html_text)
    except Exception:
        pass
    return "\n\n".join(parser.blocks)


def extract_ai_functions_from_js(js_text: str) -> list[dict]:
    lines = js_text.splitlines()
    funcs = []
    seen = set()
    for idx, line in enumerate(lines, start=1):
        ctx = "\n".join(lines[max(0, idx - 2):min(len(lines), idx + 3)])
        for rx in FUNC_PATTERNS:
            for m in rx.finditer(line):
                name = m.group(1)
                if name and name not in seen and (AI_KW_RX.search(name) or AI_KW_RX.search(ctx)):
                    seen.add(name)
                    funcs.append({"name": name, "line": idx})
    return funcs


NODE_HARNESS_RUNNER = r"""
const fs = require("fs");
const vm = require("vm");

const targetFile = process.argv[2];
const funcNames = JSON.parse(process.argv[3] || "[]");

const code = fs.readFileSync(targetFile, "utf8");
const storageData = new Map();

const mockFetch = async (url, init = {}) => ({
  ok: true,
  status: 200,
  headers: { get: () => "application/json" },
  json: async () => ({
    ok: true,
    mock: true,
    url: String(url),
    method: init.method || "GET",
    choices: [{ message: { content: "[harness-mock-response]" } }],
    response: "[harness-mock-response]",
    data: [],
  }),
  text: async () => "[harness-mock-text]",
});

const mockElement = () => ({
  value: "test prompt",
  textContent: "",
  innerHTML: "",
  style: {},
  dataset: {},
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
  querySelector: () => mockElement(),
  querySelectorAll: () => [],
});

const sandbox = {
  console: {
    log: () => {},
    warn: () => {},
    error: () => {},
    info: () => {},
    debug: () => {},
  },
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
    getItem: (k) => (storageData.has(k) ? storageData.get(k) : null),
    setItem: (k, v) => storageData.set(k, String(v)),
    removeItem: (k) => storageData.delete(k),
    clear: () => storageData.clear(),
  },
  sessionStorage: {
    getItem: () => null,
    setItem: () => {},
    removeItem: () => {},
    clear: () => {},
  },
  navigator: { userAgent: "c25-ai-harness/1.0", clipboard: { writeText: async () => {} } },
  location: { href: "https://constellation25.github.io/AiMetaverse/", pathname: "/AiMetaverse/" },
  document: {
    readyState: "complete",
    body: mockElement(),
    head: mockElement(),
    documentElement: mockElement(),
    createElement: () => mockElement(),
    getElementById: () => mockElement(),
    querySelector: () => mockElement(),
    querySelectorAll: () => [],
    addEventListener() {},
    removeEventListener() {},
  },
};
sandbox.window = sandbox;
sandbox.globalThis = sandbox;
sandbox.self = sandbox;

const exportsObj = {};
sandbox.module = { exports: exportsObj };
sandbox.exports = exportsObj;

const context = vm.createContext(sandbox);
const result = {
  file: targetFile,
  scriptCompiled: false,
  compileError: null,
  functionsTested: [],
};

try {
  const normalized = code
    .replace(/^\s*import\s+.*?;\s*$/gm, "")
    .replace(/^\s*export\s+default\s+/gm, "module.exports = ")
    .replace(/^\s*export\s+(?=(?:async\s+)?(?:function|const|let|var|class)\b)/gm, "");

  vm.runInContext(normalized, context, { filename: targetFile, timeout: 5000 });
  result.scriptCompiled = true;
} catch (err) {
  const msg = (err && (err.message || err.stack)) || String(err) || "VM evaluation failed";
  result.compileError = String(msg).split("\n")[0];
  process.stdout.write(JSON.stringify(result));
  process.exit(0);
}

const samplePayloads = [
  { prompt: "Hello AI", text: "Hello AI", input: "Sample input", query: "test query", model: "default" },
  "Sample AI prompt",
  {},
];

for (const fnName of funcNames) {
  const candidate =
    typeof context[fnName] === "function"
      ? context[fnName]
      : typeof context.module.exports?.[fnName] === "function"
        ? context.module.exports[fnName]
        : typeof context.window?.[fnName] === "function"
          ? context.window[fnName]
          : null;

  if (!candidate) {
    result.functionsTested.push({
      name: fnName,
      status: "not_in_scope",
      detail: "Function not bound in evaluated top-level or export scope",
    });
    continue;
  }

  let outcome = null;
  for (const payload of samplePayloads) {
    try {
      let out = candidate(payload);
      if (out && typeof out.then === "function") {
        out = await Promise.race([
          out,
          new Promise((_, reject) => setTimeout(() => reject(new Error("Async call timed out (3s)")), 3000)),
        ]);
      }
      const preview =
        out === undefined
          ? "undefined"
          : typeof out === "string"
            ? out.slice(0, 120)
            : JSON.stringify(out)?.slice(0, 160);
      outcome = {
        name: fnName,
        status: "passed",
        outputType: typeof out,
        preview,
      };
      break;
    } catch (err) {
      outcome = {
        name: fnName,
        status: "errored",
        error: (err && err.message) || String(err) || "Function threw error",
      };
    }
  }
  result.functionsTested.push(outcome);
}

process.stdout.write(JSON.stringify(result));
"""


def build_inventory() -> list[dict]:
    items = []
    if not STORE_DIR.exists():
        return items
    for path in sorted(STORE_DIR.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in {".js", ".mjs", ".json", ".html"}:
            continue
        rel = path.relative_to(REPO).as_posix()
        text = path.read_text(encoding="utf-8", errors="replace")
        if not AI_KW_RX.search(text):
            continue
        lines = text.splitlines()
        minified = path.suffix.lower() == ".js" and (
            (len(lines) <= 25 and len(text) > 50_000) or any(len(ln) > 4000 for ln in lines[:10])
        )
        scan_src = extract_inline_js(text) if path.suffix.lower() == ".html" else text
        funcs = [] if minified else extract_ai_functions_from_js(scan_src)
        items.append({
            "file": rel,
            "bytes": path.stat().st_size,
            "minified": minified,
            "ai_functions": funcs,
        })
    return items


def main() -> int:
    parser = argparse.ArgumentParser(description="Test discovered AI functions inside ~/AiMetaverse/store")
    parser.add_argument("--inventory", type=pathlib.Path, default=DEFAULT_INVENTORY)
    parser.add_argument("--report", type=pathlib.Path, default=DEFAULT_REPORT)
    args = parser.parse_args()

    inventory = build_inventory()

    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False, encoding="utf-8") as tmp:
        tmp.write(NODE_HARNESS_RUNNER)
        runner_path = pathlib.Path(tmp.name)

    temp_js_files: list[pathlib.Path] = []
    results = []
    try:
        for item in inventory:
            rel = item["file"]
            full_path = REPO / rel
            if not full_path.exists():
                continue

            if full_path.suffix.lower() == ".json":
                try:
                    json.loads(full_path.read_text(encoding="utf-8", errors="replace"))
                    results.append({"file": rel, "kind": "json", "status": "valid_json"})
                except Exception as exc:
                    results.append({"file": rel, "kind": "json", "status": "invalid_json", "error": str(exc)})
                continue

            if full_path.suffix.lower() == ".html":
                inline_js = extract_inline_js(full_path.read_text(encoding="utf-8", errors="replace"))
                if not inline_js.strip():
                    results.append({"file": rel, "kind": "html-inline", "status": "no_inline_script"})
                    continue
                with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False, encoding="utf-8") as htmp:
                    htmp.write(inline_js)
                    eval_path = pathlib.Path(htmp.name)
                temp_js_files.append(eval_path)
                fn_names = [f["name"] for f in item.get("ai_functions", [])]
                proc = subprocess.run(
                    ["node", str(runner_path), str(eval_path), json.dumps(fn_names)],
                    capture_output=True,
                    text=True,
                    timeout=20,
                )
                if proc.returncode != 0 or not proc.stdout.strip():
                    results.append({
                        "file": rel,
                        "kind": "html-inline",
                        "status": "runner_error",
                        "detail": (proc.stderr or proc.stdout).strip()[:300],
                    })
                    continue
                parsed = json.loads(proc.stdout)
                parsed["file"] = rel
                parsed["kind"] = "html-inline"
                results.append(parsed)
                continue

            if item.get("minified"):
                syn = subprocess.run(
                    ["node", "--check", str(full_path)],
                    capture_output=True,
                    text=True,
                    timeout=15,
                )
                results.append({
                    "file": rel,
                    "kind": "minified-bundle",
                    "status": "syntax_ok" if syn.returncode == 0 else "syntax_error",
                    "detail": syn.stderr.strip() or f"{item.get('bytes', 0)} bytes",
                })
                continue

            fn_names = [f["name"] for f in item.get("ai_functions", [])]
            proc = subprocess.run(
                ["node", str(runner_path), str(full_path), json.dumps(fn_names)],
                capture_output=True,
                text=True,
                timeout=20,
            )
            if proc.returncode != 0 or not proc.stdout.strip():
                results.append({
                    "file": rel,
                    "kind": "js-module",
                    "status": "runner_error",
                    "detail": (proc.stderr or proc.stdout).strip()[:300],
                })
                continue

            parsed = json.loads(proc.stdout)
            parsed["kind"] = "js-module"
            results.append(parsed)
    finally:
        runner_path.unlink(missing_ok=True)
        for p in temp_js_files:
            p.unlink(missing_ok=True)

    args.report.parent.mkdir(parents=True, exist_ok=True)
    report = {
        "store_dir": str(STORE_DIR),
        "files_evaluated": len(results),
        "results": results,
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    passed_fns = 0
    errored_fns = 0
    for r in results:
        kind = r.get("kind")
        if kind in {"js-module", "html-inline"}:
            fns = r.get("functionsTested", [])
            ok_count = sum(1 for f in fns if f.get("status") == "passed")
            err_count = sum(1 for f in fns if f.get("status") == "errored")
            passed_fns += ok_count
            errored_fns += err_count
            comp = "OK" if r.get("scriptCompiled") else f"ERR ({r.get('compileError')})"
            print(f"[{kind.upper()}] {r['file']} -> compile={comp} | fns_tested={len(fns)} (passed={ok_count}, errored={err_count})")
            for f in fns:
                if f.get("status") == "passed":
                    print(f"     PASS {f['name']} ({f.get('outputType')}): {f.get('preview')}")
                elif f.get("status") == "errored":
                    print(f"     ERR  {f['name']}: {f.get('error')}")
        else:
            print(f"[{kind.upper()}] {r['file']} -> {r.get('status')} {r.get('detail', '')}".strip())

    print(f"\nSummary: {len(results)} files evaluated | {passed_fns} AI function calls passed | {errored_fns} errored")
    print(f"Report saved to: {args.report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
