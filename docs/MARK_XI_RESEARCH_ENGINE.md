# J.A.R.V.I.S. MARK XI — BROWSER RESEARCH & REPORTING ENGINE

**Module:** `backend/app/tools/browser_research.py`  
**Components:** Async HTTPX, BeautifulSoup4, ReportLab, SSRF Security Guard  
**Target Version:** MARK XI  

---

## 1. Multi-Source Search & Aggregation

The research engine queries search engines asynchronously without requiring third-party API keys:
- Dispatches queries to DuckDuckGo HTML endpoint with standard browser user-agent headers.
- Extracts search result titles, snippets, and redirect targets.
- Falls back to structured authoritative references (Wikipedia, official docs) if search engines throttle.

---

## 2. DOM Parsing & Article Extraction

`fetch_page_content(url, max_chars=4000)`:
1. Strips non-content boilerplate: `<script>`, `<style>`, `<nav>`, `<footer>`, `<header>`, `<aside>`, `<noscript>`, `<svg>`, and `<form>`.
2. Targets semantic content tags (`<article>`, `<main>`, `<p>`, `<h1>`-`<h3>`, `<li>`).
3. Discards cookie banners, GDPR disclaimers, and newsletter popups.
4. Returns clean, structured text paragraphs ready for Gemini synthesis.

---

## 3. Server-Side Request Forgery (SSRF) Guard

To prevent exploitation via malicious redirect URLs or internal service probing:
- Evaluates scheme: only `http` and `https` permitted.
- Hostname checks: blocks `localhost`, `127.0.0.1`, `::1`, and `0.0.0.0`.
- DNS Resolution: Resolves hostname to IP addresses via `socket.getaddrinfo`.
- IP Policy: Validates against `ipaddress.ip_address`. Rejects private networks (`10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`), loopbacks (`127.0.0.0/8`), link-local / cloud metadata endpoints (`169.254.0.0/16`), multicast, and reserved IP ranges.
- Logs and safely denies requests violating SSRF policy with HTTP 403.

---

## 4. Verified ReportLab PDF Generation

Generates executive-ready PDF dossiers:
- High-contrast visual styling: Navy `#0f172a`, Cyan `#0891b2`, Charcoal `#1e293b`.
- Metadata card: Prepared for Rohan, compilation timestamp, source count.
- Structured executive summary paragraphs synthesized from extracted pages.
- Authoritative Bibliography Table: Source document title, reference ID, and clickable hyperlinks with blue color styling.
