/* C25 Client-Side Route Normalizer & Link Guard */
(() => {
  const BASE_PREFIX = "/AiMetaverse/";
  const KNOWN_SLUGS = new Set([
    "why-ai", "enterprise", "tools", "labs", "education", "worlds",
    "contact", "shop", "voice-lipsync", "avatar-create", "twin-studio",
    "prompter", "ai-education", "ai-education-hub", "metaverse-directory",
    "vr-hub", "metaverse-toolkit", "ai4reelz", "faceforge", "webstudio",
    "app-builder", "commz", "vstore", "crm", "bitbucks", "mars",
    "records", "avatar", "metabox", "developers", "apikonnect",
    "devzone", "communities", "news", "signup", "signin", "privacy", "terms"
  ]);

  function c25NormalizeHref(rawHref, currentPathname = window.location.pathname) {
    if (!rawHref || /^(#|mailto:|tel:|javascript:|data:|https?:)/i.test(rawHref.trim())) {
      return rawHref;
    }
    const trimmed = rawHref.trim();
    if (trimmed.startsWith("/")) {
      return trimmed;
    }
    const cleaned = trimmed.replace(/^(?:\.\/|\.\.\/)+/, "");
    const parts = cleaned.split("/").filter(Boolean);
    if (!parts.length) return rawHref;

    // <slug>/<slug>.html -> /AiMetaverse/<slug>/index.html
    if (parts.length === 2 && parts[1].endsWith(".html") && parts[1].slice(0, -5) === parts[0]) {
      return `${BASE_PREFIX}${parts[0]}/index.html`;
    }

    // Known slug relative link -> /AiMetaverse/<cleaned>
    if (KNOWN_SLUGS.has(parts[0])) {
      return `${BASE_PREFIX}${cleaned}`;
    }

    // Prevent double-nesting when already inside /AiMetaverse/<slug>/
    if (currentPathname.startsWith(BASE_PREFIX) && parts.includes("index.html")) {
      const targetSlug = parts[parts.length - 2];
      if (KNOWN_SLUGS.has(targetSlug)) {
        return `${BASE_PREFIX}${targetSlug}/index.html`;
      }
    }
    return rawHref;
  }

  function healAnchors() {
    document.querySelectorAll("a[href]").forEach((anchor) => {
      const original = anchor.getAttribute("href");
      const healed = c25NormalizeHref(original);
      if (healed && healed !== original) {
        anchor.setAttribute("href", healed);
        anchor.setAttribute("data-c25-healed-from", original);
      }
    });
  }

  window.c25NormalizeHref = c25NormalizeHref;
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", healAnchors, { once: true });
  } else {
    healAnchors();
  }
})();
