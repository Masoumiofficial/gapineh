#!/usr/bin/env python3
"""
ساخت JSON-LD بخش پرسش‌های متداول از متن قابل مشاهدهٔ همان صفحه.

دلیل وجود: سیاست موتورهای جست‌وجو این است که دادهٔ ساختاریافته با محتوای
قابل مشاهده هم‌خوان باشد. به‌جای نگه‌داشتن دو نسخهٔ دستی، پاسخ‌ها از خود
`index.html` استخراج و جای‌گذاری می‌شوند.

اجرا (پس از هر تغییر متن FAQ):
    python3 tools/build_faq_jsonld.py
نیازمندی: html5lib  →  python3 -m pip install --user html5lib
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HTML_PATH = ROOT / "index.html"
START = "<!-- FAQ-JSONLD:START -->"
END = "<!-- FAQ-JSONLD:END -->"
NS = "{http://www.w3.org/1999/xhtml}"


def main() -> int:
    try:
        import html5lib
    except ImportError:
        print("html5lib نصب نیست:  python3 -m pip install --user html5lib")
        return 2

    html = HTML_PATH.read_text(encoding="utf-8")
    if START not in html or END not in html:
        print("نشانگرهای FAQ-JSONLD در index.html پیدا نشد.")
        return 1

    doc = html5lib.HTMLParser().parse(html)
    pairs: list[dict[str, str]] = []
    for el in doc.iter():
        if not isinstance(el.tag, str) or el.tag.replace(NS, "") != "details":
            continue
        if "faq__item" not in (el.get("class") or ""):
            continue
        summary = next((c for c in el if str(c.tag).endswith("summary")), None)
        body = next(
            (c for c in el if "faq__body" in (c.get("class") or "")),
            None,
        )
        if summary is None or body is None:
            continue
        name = re.sub(r"\s+", " ", "".join(summary.itertext())).strip()
        text = re.sub(r"\s+", " ", "".join(body.itertext())).strip()
        if name and text:
            pairs.append({"q": name, "a": text})

    if not pairs:
        print("هیچ پرسشی پیدا نشد.")
        return 1

    data = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "@id": "https://etehadwp.com/gapineh/#faq",
        "mainEntity": [
            {
                "@type": "Question",
                "name": pair["q"],
                "acceptedAnswer": {"@type": "Answer", "text": pair["a"]},
            }
            for pair in pairs
        ],
    }

    block = (
        START
        + '\n  <script type="application/ld+json">\n'
        + json.dumps(data, ensure_ascii=False, indent=2)
        + "\n  </script>\n  "
        + END
    )

    prefix, rest = html.split(START, 1)
    _, suffix = rest.split(END, 1)
    HTML_PATH.write_text(prefix + block + suffix, encoding="utf-8")
    print(f"{len(pairs)} پرسش در JSON-LD نوشته شد.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
