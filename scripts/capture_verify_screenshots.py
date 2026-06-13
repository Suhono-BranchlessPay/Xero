"""Capture Xero verify page screenshots for M3+M4 docs."""

from __future__ import annotations

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "docs", "screenshots")

SHOTS = [
    ("m3m4-inv-0003.png", "https://branchlesspay.com/verify/f90bae2f-7e1a-47cb-bb0f-515cee0edf12"),
    ("m3m4-inv-0002.png", "https://branchlesspay.com/verify/21309f86-e1c1-4010-91f7-61ff853bab38"),
    ("m3m4-inv-updated.png", "https://branchlesspay.com/verify/6c005b64-9c0f-49cf-9cf6-804db5630801"),
    ("m3m4-inv-0001.png", "https://branchlesspay.com/verify/85c80ab2-5014-4d87-a5ed-62eb4851e244"),
]


def main() -> int:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("Install playwright: pip install playwright && playwright install chromium")
        return 1

    os.makedirs(OUT_DIR, exist_ok=True)
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page(viewport={"width": 1280, "height": 1600})
        for filename, url in SHOTS:
            path = os.path.join(OUT_DIR, filename)
            print("Screenshot", url, "->", filename)
            page.goto(url, wait_until="networkidle", timeout=60000)
            page.wait_for_timeout(2000)
            page.screenshot(path=path, full_page=True)
        browser.close()
    print("Saved to", OUT_DIR)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
