#!/usr/bin/env python3
"""
check_sketch.py - static checks for a generative p5.js piece (.html viewer or .js sketch).

Part of the generative-art-p5js skill. Standard library only.

Usage:
    python3 check_sketch.py piece.html            # readable report
    python3 check_sketch.py piece.js --json       # machine-readable
    python3 check_sketch.py piece.html --strict   # exit 1 if any "error" is found

It reads source only. It cannot prove determinism (that needs a run: same seed, two
renders, compare), it flags the usual causes of broken reproducibility and a few
hosting and performance problems. A clean result is evidence, not proof.
"""

import argparse
import json
import os
import re
import sys
from urllib.parse import urlparse

ERROR, WARNING, NOTE = "error", "warning", "note"
ALLOWED_SCRIPT_HOSTS = {"cdnjs.cloudflare.com", "cdn.jsdelivr.net", "cdn.tailwindcss.com", "code.jquery.com"}
ALLOWED_STYLE_HOSTS = {"fonts.googleapis.com"}
MAX_BYTES = 16 * 1024 * 1024
findings = []


def add(sev, rule, msg, line=None, snippet=None):
    findings.append({"severity": sev, "rule": rule, "message": msg, "line": line,
                     "snippet": (snippet or "").strip()[:110] or None})


def line_of(text, pos):
    return text.count("\n", 0, pos) + 1


def mask_comments(text):
    def blank(m):
        return re.sub(r"[^\n]", " ", m.group(0))
    text = re.sub(r"<!--.*?-->", blank, text, flags=re.S)
    text = re.sub(r"/\*.*?\*/", blank, text, flags=re.S)
    text = re.sub(r"(?<![:\"'\\])//[^\n]*", blank, text)
    return text


def check(path):
    size = os.path.getsize(path)
    raw = open(path, "r", encoding="utf-8", errors="replace").read()
    is_html = path.lower().endswith((".html", ".htm"))
    text = mask_comments(raw)
    low = text.lower()

    if size > MAX_BYTES:
        add(ERROR, "file-size", f"{size / 1024 / 1024:.1f} MB; hosted pages must stay under 16 MB.")

    # ---- determinism -----------------------------------------------------
    for m in re.finditer(r"Math\.random\s*\(", text):
        ln = text[text.rfind("\n", 0, m.start()) + 1: text.find("\n", m.start())]
        if "seed" not in ln.lower():
            add(ERROR, "math-random",
                "Math.random() is not seeded, so the art changes on every load. Use random() after randomSeed().",
                line_of(text, m.start()), ln)
    if not re.search(r"\brandomSeed\s*\(", text):
        add(ERROR, "no-random-seed", "No randomSeed() call. Seed the generator so a seed reproduces the piece.")
    if re.search(r"\bnoise\s*\(", text) and not re.search(r"\bnoiseSeed\s*\(", text):
        add(ERROR, "no-noise-seed", "noise() is used but noiseSeed() is never called.")
    for pat, what in ((r"\bnew\s+Date\s*\(", "new Date()"), (r"\bDate\.now\s*\(", "Date.now()"),
                      (r"\bperformance\.now\s*\(", "performance.now()"), (r"\bmillis\s*\(", "millis()")):
        for m in re.finditer(pat, text):
            add(WARNING, "time-dependent",
                f"{what} makes output depend on wall-clock time. Fine for UI only; never feed it into the art.",
                line_of(text, m.start()))
            break
    if re.search(r"\bframeCount\b", text) and re.search(r"\b(randomSeed|noiseSeed)\b", text):
        add(WARNING, "frame-count",
            "frameCount keeps counting across reseeds, so one seed can render different frames. Use your own counter reset in initializeSystem().")

    # ---- viewer structure (html only) -------------------------------------
    if is_html:
        need_ids = ["seed-input"]
        need_funcs = ["initializeSystem", "previousSeed", "nextSeed", "randomSeedAndUpdate", "resetParameters"]
        for i in need_ids:
            if f'id="{i}"' not in text and f"id='{i}'" not in text:
                add(ERROR, "missing-seed-input", f"Missing the #{i} control. Seed controls are required.")
        for f in need_funcs:
            if not re.search(rf"function\s+{f}\s*\(|{f}\s*=\s*(async\s*)?(\(|function)", text):
                add(ERROR, "missing-function", f"Missing required function {f}().")
        if not re.search(r"\bsetup\s*\(", text) or not re.search(r"createCanvas\s*\(", text):
            add(ERROR, "no-canvas", "No setup() with createCanvas().")
        if not re.search(r"<html\b[^>]*\blang\s*=", text, re.I):
            add(WARNING, "html-lang", "Missing lang attribute on <html>.")
        if not re.search(r'<meta\b[^>]*name\s*=\s*["\']viewport["\']', text, re.I):
            add(WARNING, "viewport", "Missing viewport meta tag.")
        if not re.search(r"<title\b[^>]*>[^<]+</title>", text, re.I):
            add(WARNING, "title", "Missing or empty <title>.")
        if "aria-label" not in low:
            add(NOTE, "canvas-label", "No aria-label on the canvas; give it a short description.")
        if not re.search(r"saveCanvas\s*\(", text):
            add(NOTE, "no-export", "No saveCanvas() export. People usually want the PNG.")
        if re.search(r"\bdraw\s*\(", text) and "prefers-reduced-motion" not in low:
            add(WARNING, "reduced-motion", "Animated piece with no prefers-reduced-motion handling.")

        # network / hosting
        p5_found = False
        for m in re.finditer(r"<script\b[^>]*\bsrc\s*=\s*[\"']((?:https?:)?//[^\"']+)[\"']", text, re.I):
            src = m.group(1)
            host = urlparse(src if src.startswith("http") else "https:" + src).hostname or ""
            if "p5" in src.lower():
                p5_found = True
                if not re.search(r"p5(\.js)?[/@]\d+\.\d+", src):
                    add(WARNING, "p5-unpinned", "p5.js URL has no exact pinned version.", line_of(text, m.start()), src)
            if host not in ALLOWED_SCRIPT_HOSTS:
                add(ERROR, "script-host", f"Script from '{host}' is blocked in hosted pages.", line_of(text, m.start()), src)
        if not p5_found and not re.search(r"<script\b[^>]*>[^<]*(?:p5|class\s+p5)\b", text):
            add(ERROR, "no-p5", "p5.js is not loaded from an allowed CDN (use cdnjs.cloudflare.com with a pinned version).")
        for m in re.finditer(r"<link\b[^>]*\bhref\s*=\s*[\"']((?:https?:)?//[^\"']+)[\"'][^>]*>", text, re.I):
            host = urlparse(m.group(1) if m.group(1).startswith("http") else "https:" + m.group(1)).hostname or ""
            if "stylesheet" in m.group(0).lower() and host not in ALLOWED_STYLE_HOSTS:
                add(ERROR, "style-host", f"Stylesheet from '{host}' is blocked in hosted pages.", line_of(text, m.start()))
        for m in re.finditer(r"<img\b[^>]*\bsrc\s*=\s*[\"'](https?:)?//", text, re.I):
            add(ERROR, "remote-image", "Remote image will not load in hosted pages.", line_of(text, m.start()))
            break
        for m in re.finditer(r"(loadImage|loadFont|loadJSON|loadStrings|loadTable|fetch)\s*\(\s*[\"']https?://", text):
            add(ERROR, "remote-asset", f"{m.group(1)}() from an external host is blocked in hosted pages. Generate or embed the data.",
                line_of(text, m.start()))
            break

    # ---- performance & safety ---------------------------------------------
    for m in re.finditer(r"createCanvas\s*\(\s*(\d+)\s*,\s*(\d+)", text):
        w, h = int(m.group(1)), int(m.group(2))
        if w * h > 2400 * 2400:
            add(WARNING, "big-canvas", f"{w}x{h} canvas is heavy; 1000 to 1600 px square is plenty, CSS scales it.",
                line_of(text, m.start()), m.group(0))
    if re.search(r"\bcreateCanvas\s*\(", text) and not re.search(r"\bpixelDensity\s*\(", text):
        add(WARNING, "pixel-density", "No pixelDensity() call. On high-DPI screens p5 renders up to 4x the pixels; call pixelDensity(1) unless you need it.")
    for m in re.finditer(r"\b(alert|prompt|confirm)\s*\(", text):
        add(WARNING, "blocking-dialog", f"{m.group(1)}() blocks the page and may not work in embedded views.", line_of(text, m.start()))
        break
    if re.search(r"\b(localStorage|sessionStorage)\b", text) and not re.search(r"\btry\s*\{", text):
        add(WARNING, "storage-try", "Browser storage used without try/catch.")
    if re.search(r"\bbackground\s*\(\s*(0|255)\s*\)", text):
        add(NOTE, "flat-background", "Pure black or white background(). A tinted background almost always looks better.")
    if re.search(r"\bloadPixels\s*\(|\bget\s*\(\s*\)|\.get\s*\(\s*\)", text) and re.search(r"\bdraw\s*\(", text):
        add(NOTE, "pixel-readback", "Reading pixels (loadPixels/get) is slow; avoid it every frame.")
    return size


def main():
    ap = argparse.ArgumentParser(description="Static checks for a generative p5.js piece.")
    ap.add_argument("file")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--strict", action="store_true", help="exit 1 if any error is found")
    a = ap.parse_args()
    if not os.path.isfile(a.file):
        print(f"error: file not found: {a.file}", file=sys.stderr)
        sys.exit(2)
    size = check(a.file)
    order = {ERROR: 0, WARNING: 1, NOTE: 2}
    findings.sort(key=lambda f: (order[f["severity"]], f["line"] or 10**9))
    counts = {s: sum(1 for f in findings if f["severity"] == s) for s in (ERROR, WARNING, NOTE)}
    if a.json:
        print(json.dumps({"file": a.file, "bytes": size, "counts": counts, "findings": findings}, indent=2))
    else:
        print(f"check_sketch: {a.file} ({size / 1024:.1f} KB)")
        print(f"  {counts[ERROR]} error(s), {counts[WARNING]} warning(s), {counts[NOTE]} note(s)\n")
        tag = {ERROR: "ERROR  ", WARNING: "WARNING", NOTE: "NOTE   "}
        for f in findings:
            where = f"line {f['line']}" if f["line"] else "file"
            print(f"[{tag[f['severity']]}] {f['rule']} ({where}): {f['message']}")
            if f["snippet"]:
                print(f"           > {f['snippet']}")
        if not findings:
            print("No findings. Evidence, not proof: render the same seed twice and compare to confirm determinism.")
        print("\nStatic source checks only.")
    sys.exit(1 if (a.strict and counts[ERROR]) else 0)


if __name__ == "__main__":
    main()
