# AI Education & Prompt Hub (`ai-education-hub.html` / `ai-education-hub/`)

Constellation25 | AI Education & Prompt Hub — the subpage the
**"Learn AI Programming & Development — Get certified"** tile opens.

## 🚀 How to Use This Tool

1. **Save the file:** source document at `store/ai-education-hub.html`; generated,
   site-integrated page is `ai-education-hub.html` (+ folder copy
   `ai-education-hub/index.html`) — fully self-contained (inlined Tailwind runtime with
   the `c25` palette, scoped CSS, clipboard polyfill; FA icons optional via CDN).
2. **Open in browser:** double-click the file, or visit
   `https:///ai-education-hub/` once deployed, to
   launch the interactive dashboard.
3. **Explore the 4 modules** (tab bar relocated from the stripped nav to the page top):
   - **Quiz Cards:** click any flashcard to flip it and reveal the answer; use the top
     filters to focus on Termux, Prompting, or Certifications.
   - **Prompt Library:** use the search bar or category tags to find specific prompts;
     click the copy icon in the top-right of any card to instantly copy the prompt to
     your clipboard (works even without the async clipboard API).
   - **Certifications:** a clean, categorized breakdown of the exact paths (Beginner,
     Intermediate, Advanced) — IBM/DataCamp/Codecademy → HuggingFace/Azure/AWS →
     MIT/NVIDIA/Stanford — plus the "three serious projects" portfolio strategy.
   - **Open Source:** quick-reference table of the best GitHub curriculums (Microsoft
     GenAI for Beginners, Labonne LLM course, AI Agents for Beginners, Made With ML)
     and production boilerplates (full-stack AI agent template, FastAPI+LangGraph,
     awesome-llm-apps, Multi-Agent-RAG).

## ✅ Why This Fits Your Vision

- **Zero cost:** runs entirely in your browser. No subscriptions, no paywalls.
- **Action-oriented:** the prompt library isn't just theory; it's copy-paste ready for
  your Termux/Ollama workflows.
- **Scalable:** add more questions to the `quizData` array or more prompts to the
  `promptData` array in `store/ai-education-hub.html` to build out the full
  "1000+ Prompt Library" over time — regenerate with `python3 gen_pages.py`.

## Ecosystem wiring

- Embedded copy scoped under `.edu-embed`; all tab/filter/search queries re-scoped so
  they cannot touch the host page's own tabs; store nav/footer stripped (site shell
  provides both); implicit `window.event` in `filterPrompts` replaced with an explicit
  element argument; `innerText` normalised to `textContent`.
- Opened from: home tile *Learn AI Programming & Development*, site-map chip
  *AI Education & Prompt Hub*, footer link; the native `education.html` page keeps the
  knowledge-cloud overview and links deeper into this hub.
