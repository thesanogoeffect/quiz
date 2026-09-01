// The LLM explanations are stored as small HTML fragments and rendered with
// v-html. They are first-party data, but they are generated from
// student-submitted question text, so nothing in the pipeline guarantees the
// markup is safe. Parse it and keep only a tiny allowlist of formatting tags -
// no attributes at all, which rules out event handlers, javascript: URLs and
// embedded resources.

const ALLOWED_TAGS = new Set([
  "P",
  "BR",
  "B",
  "STRONG",
  "I",
  "EM",
  "U",
  "UL",
  "OL",
  "LI",
  "DIV",
  "SPAN",
  "H3",
  "H4",
  "CODE",
  "SUB",
  "SUP",
]);

// Dropped entirely, contents included - unwrapping these would splash their
// source text into the page.
const DROP_ENTIRELY = new Set([
  "SCRIPT",
  "STYLE",
  "IFRAME",
  "OBJECT",
  "EMBED",
  "NOSCRIPT",
  "TEMPLATE",
  "SVG",
  "MATH",
  "LINK",
  "META",
  "BASE",
  "FORM",
]);

const HTML_NS = "http://www.w3.org/1999/xhtml";

function sanitizeNode(node) {
  // Snapshot: the loop removes and reparents children as it goes.
  for (const child of Array.from(node.childNodes)) {
    if (child.nodeType === Node.TEXT_NODE) continue;

    if (child.nodeType !== Node.ELEMENT_NODE) {
      child.remove(); // comments, processing instructions
      continue;
    }

    // Foreign content (SVG, MathML) goes entirely. It is never legitimate here,
    // and it is where mXSS lives: `tagName` is only upper-cased for HTML
    // elements, so an SVG-namespaced <script> would slip past a tagName check.
    if (child.namespaceURI !== HTML_NS) {
      child.remove();
      continue;
    }

    // localName is namespace-independent; upper-case it ourselves.
    const name = child.localName.toUpperCase();

    if (DROP_ENTIRELY.has(name)) {
      child.remove();
      continue;
    }

    // Clean the subtree first, so anything promoted by an unwrap below has
    // already been sanitised.
    sanitizeNode(child);

    if (ALLOWED_TAGS.has(name)) {
      for (const attr of Array.from(child.attributes)) {
        child.removeAttribute(attr.name);
      }
    } else {
      // Unknown but harmless wrapper: keep the text, drop the tag.
      const parent = child.parentNode;
      while (child.firstChild) parent.insertBefore(child.firstChild, child);
      child.remove();
    }
  }
}

// The generator sometimes emits `<pSome text</p>` (a missing `>`). The parser
// reads that as a tag named `pSome` and swallows the whole sentence into
// attributes, so the text vanishes. scripts/fix_l3_html.py repairs the export;
// this repairs anything that slips through a future pipeline run.
//
// It only fires when a matching close tag follows, so ordinary prose - "a<bC",
// "p<i" in a formula - is left alone.
const MISSING_GT = /<(p|div|li|ul|ol|b|i)([A-Z][^<>]{0,600}?)<\/\1>/g;

export function sanitizeHtml(dirty) {
  const input = String(dirty ?? "").replace(MISSING_GT, "<$1>$2</$1>");
  if (!input) return "";

  // No DOM available (prerender / tests) - fall back to text only.
  if (typeof document === "undefined") {
    return input.replace(/<[^>]*>/g, "");
  }

  // <template> parses without executing scripts or fetching resources.
  const template = document.createElement("template");
  template.innerHTML = input;
  sanitizeNode(template.content);
  return template.innerHTML;
}
