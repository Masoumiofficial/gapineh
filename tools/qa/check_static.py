#!/usr/bin/env python3
"""
QA استاتیک صفحهٔ فروش گپینه (بدون مرورگر).

بررسی‌ها:
  • ساختار HTML با html5lib (خطای تجزیه، تگ‌های باز‌مانده)
  • شناسهٔ تکراری، ارجاع‌های aria-controls / aria-labelledby / for / href داخلی
  • alt تصاویر، ابعاد تصاویر، lazy-loading تصاویر پایین صفحه
  • سلسله‌مراتب تیترها و یکتایی H1
  • وجود هدف فایل‌های محلی (CSS/JS/فونت/تصویر)
  • اعتبار JSON-LD و هم‌خوانی پرسش‌های FAQ با متن قابل مشاهده
  • متادیتای SEO (title/description/canonical/OG/Twitter)
  • تجزیهٔ CSS با tinycss2 و بررسی ارجاع فونت
  • نسبت کنتراست رنگ‌های اصلی با WCAG AA

اجرا:  python3 tools/qa/check_static.py
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HTML_PATH = ROOT / "index.html"

errors: list[str] = []
warnings: list[str] = []
notes: list[str] = []


def err(msg: str) -> None:
    errors.append(msg)


def warn(msg: str) -> None:
    warnings.append(msg)


def ok(msg: str) -> None:
    notes.append(msg)


def luminance(hex_color: str) -> float:
    hex_color = hex_color.lstrip("#")
    if len(hex_color) == 3:
        hex_color = "".join(c * 2 for c in hex_color)
    r, g, b = (int(hex_color[i : i + 2], 16) / 255 for i in (0, 2, 4))
    chan = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in (r, g, b)]
    return 0.2126 * chan[0] + 0.7152 * chan[1] + 0.0722 * chan[2]


def contrast(fg: str, bg: str) -> float:
    l1, l2 = luminance(fg), luminance(bg)
    hi, lo = max(l1, l2), min(l1, l2)
    return (hi + 0.05) / (lo + 0.05)


def main() -> int:
    if not HTML_PATH.exists():
        err("index.html پیدا نشد")
        return 1

    html = HTML_PATH.read_text(encoding="utf-8")

    # ---------- ۰) پیش‌نیازها ----------
    try:
        import html5lib  # noqa: F401
        import tinycss2  # noqa: F401
    except ImportError as exc:
        print("پیش‌نیاز تست نصب نیست:", exc)
        print("اجرا کنید:  python3 -m pip install --user html5lib tinycss2")
        return 2

    # ---------- ۱) تجزیه HTML ----------
    try:
        import html5lib

        parser = html5lib.HTMLParser(strict=False)
        doc = parser.parse(html)
        if parser.errors:
            for pos, code, data in parser.errors[:20]:
                warn(f"html5lib: {code} / {data}")
        ok("HTML با html5lib تجزیه شد")
    except Exception as exc:  # pragma: no cover
        err(f"تجزیه HTML شکست خورد: {exc}")
        return 1

    # html5lib namespace
    ns = "{http://www.w3.org/1999/xhtml}"

    def tag(el) -> str:
        t = el.tag
        return t.replace(ns, "") if isinstance(t, str) else ""

    # ---------- ۲) شناسه‌ها و ارجاع‌ها ----------
    ids = [(el.get("id"), tag(el)) for el in doc.iter() if el.get("id")]
    seen: dict[str, int] = {}
    for ident, _ in ids:
        seen[ident] = seen.get(ident, 0) + 1
    dups = [k for k, v in seen.items() if v > 1]
    if dups:
        err(f"شناسهٔ تکراری: {', '.join(dups)}")
    else:
        ok(f"{len(seen)} شناسهٔ یکتا")

    id_set = set(seen)

    for el in doc.iter():
        for attr in ("aria-controls", "aria-labelledby", "aria-describedby", "for"):
            val = el.get(attr)
            if not val:
                continue
            for ref in val.split():
                if ref not in id_set:
                    err(f"<{tag(el)}> {attr} به شناسهٔ ناموجود «{ref}» اشاره می‌کند")

    # ---------- ۳) لینک‌ها ----------
    internal, external = 0, 0
    for el in doc.iter():
        if tag(el) != "a":
            continue
        href = (el.get("href") or "").strip()
        if not href:
            err("لینک بدون href")
            continue
        if href.startswith("#"):
            internal += 1
            if href != "#" and href[1:] not in id_set:
                err(f"لنگر داخلی بدون مقصد: {href}")
        elif href.startswith("http"):
            external += 1
            if not re.match(r"^https://[\w.-]+(:\d+)?(/[^\s]*)?$", href):
                warn(f"نشانی خارجی غیرمعمول: {href}")
        elif href.startswith("mailto:") or href.startswith("tel:"):
            continue
        else:
            local = (ROOT / href.split("#")[0]).resolve()
            if not local.exists():
                err(f"فایل محلی وجود ندارد: {href}")
    ok(f"{internal} لنگر داخلی، {external} لینک خارجی")

    # لینک‌های ناامن و target=_blank بدون rel
    for el in doc.iter():
        if tag(el) != "a":
            continue
        href = (el.get("href") or "").strip()
        if href.startswith("http://"):
            err(f"لینک غیر HTTPS (ریسک محتوای مختلط): {href}")
        if el.get("target") == "_blank" and "noopener" not in (el.get("rel") or ""):
            err(f"target=_blank بدون rel=noopener: {href}")

    # ---------- ۴) تصاویر ----------
    imgs = [el for el in doc.iter() if tag(el) == "img"]
    for img in imgs:
        src = img.get("src") or ""
        if not src:
            err("تصویر بدون src")
            continue
        if not (ROOT / src).exists():
            err(f"تصویر وجود ندارد: {src}")
        decoded = img.get("decoding")
        if decoded != "async":
            warn(f"تصویر بدون decoding=async: {src}")
        if not (img.get("width") and img.get("height")):
            err(f"تصویر بدون width/height (خطر CLS): {src}")
        if img.get("hidden") is None:
            # تصاویر خارج از قاب اسکرین‌شات باید alt داشته باشند
            if img.get("alt") is None:
                err(f"تصویر بدون alt: {src}")
            elif img.get("alt") == "":
                # alt خالی فقط برای تصویر تزئینی مجاز است
                if "brand-mark" not in src:
                    warn(f"alt خالی برای تصویر غیرتزئینی: {src}")
    ok(f"{len(imgs)} تصویر بررسی شد")

    # ---------- ۵) تیترها ----------
    headings = [(tag(el), "".join(el.itertext()).strip()) for el in doc.iter() if re.fullmatch(r"h[1-6]", tag(el))]
    h1s = [h for h in headings if h[0] == "h1"]
    if len(h1s) != 1:
        err(f"تعداد H1 باید ۱ باشد، اکنون {len(h1s)}")
    else:
        ok(f"H1 یکتا: «{h1s[0][1][:60]}…»")

    levels = [int(h[0][1]) for h in headings]
    for prev, cur in zip(levels, levels[1:]):
        if cur - prev > 1:
            warn(f"پرش سطح تیتر: h{prev} → h{cur}")
    ok(f"{len(headings)} تیتر با ترتیب بررسی‌شده")

    # ---------- ۶) متادیتا ----------
    def meta_content(name: str, attr: str = "name") -> str | None:
        for el in doc.iter():
            if tag(el) == "meta" and el.get(attr) == name:
                return el.get("content") or ""
        return None

    title = None
    for el in doc.iter():
        if tag(el) == "title":
            title = "".join(el.itertext()).strip()
    if not title or not (25 <= len(title) <= 75):
        warn(f"طول عنوان صفحه نامتعارف است: {len(title or '')}")
    else:
        ok(f"عنوان ({len(title)} نویسه)")

    desc = meta_content("description")
    if not desc or not (110 <= len(desc) <= 175):
        warn(f"طول متا دیسکریپشن نامتعارف است: {len(desc or '')}")
    else:
        ok(f"متا دیسکریپشن ({len(desc)} نویسه)")

    canonical = None
    for el in doc.iter():
        if tag(el) == "link" and el.get("rel") == "canonical":
            canonical = el.get("href")
    if not canonical:
        err("canonical ندارد")
    elif not re.match(r"^https://[\w.-]+/", canonical):
        warn(f"canonical مشکوک: {canonical}")

    for prop in ("og:title", "og:description", "og:image", "og:url", "og:type"):
        if not meta_content(prop, "property"):
            err(f"متای Open Graph ندارد: {prop}")
    if not meta_content("twitter:card"):
        warn("متای Twitter card ندارد")

    html_el = next((el for el in doc.iter() if tag(el) == "html"), None)
    if html_el is None or html_el.get("lang") != "fa" or html_el.get("dir") != "rtl":
        err("html باید lang=fa و dir=rtl باشد")
    else:
        ok("lang=fa و dir=rtl")

    # ---------- ۷) JSON-LD ----------
    ld_blocks = []
    for el in doc.iter():
        if tag(el) == "script" and (el.get("type") or "").startswith("application/ld+json"):
            try:
                ld_blocks.append(json.loads("".join(el.itertext())))
            except json.JSONDecodeError as exc:
                err(f"JSON-LD نامعتبر: {exc}")
    if not ld_blocks:
        warn("JSON-LD ندارد")

    visible = " ".join("".join(el.itertext()) for el in doc.iter() if tag(el) in {"p", "summary", "div", "span", "h3"})
    faq_questions = []
    for block in ld_blocks:
        graph = block.get("@graph", [block])
        for node in graph:
            if node.get("@type") == "FAQPage":
                for q in node.get("mainEntity", []):
                    faq_questions.append(q.get("name", ""))
    faq_answers = []
    for block in ld_blocks:
        graph = block.get("@graph", [block])
        for node in graph:
            if node.get("@type") == "FAQPage":
                for q in node.get("mainEntity", []):
                    ans = (q.get("acceptedAnswer") or {}).get("text", "")
                    if ans:
                        faq_answers.append((q.get("name", ""), ans))

    if faq_questions:
        missing = [q for q in faq_questions if q and q[:18] not in visible]
        if missing:
            err(f"پرسش‌های JSON-LD در متن دیده نمی‌شوند: {missing}")

        flat = re.sub(r"\s+", " ", visible)
        drift = [name for name, ans in faq_answers if re.sub(r"\s+", " ", ans)[:60] not in flat]
        if drift:
            err(f"پاسخ‌های JSON-LD با متن صفحه هم‌خوان نیستند ({len(drift)} مورد)؛ tools/build_faq_jsonld.py را اجرا کنید")
        else:
            ok(f"{len(faq_questions)} پرسش و {len(faq_answers)} پاسخ FAQ با متن صفحه هم‌خوان است")

    for block in ld_blocks:
        text = json.dumps(block, ensure_ascii=False)
        for bad in ('"aggregateRating"', '"review"', '"price"', '"offers"'):
            if bad in text:
                err(f"دادهٔ ساختاریافته شامل {bad} است؛ اطلاعات تجاری تأیید نشده")

    # ---------- ۸) دسترس‌پذیری پایه ----------
    for el in doc.iter():
        if tag(el) == "button" and not el.get("type"):
            warn("دکمه بدون type")
    for el in doc.iter():
        if tag(el) == "input":
            if not el.get("id"):
                warn("ورودی بدون id")
                continue
            has_label = any(
                l.get("for") == el.get("id") for l in doc.iter() if tag(l) == "label"
            )
            if not has_label and not el.get("aria-label"):
                err(f"ورودی بدون برچسب: {el.get('id')}")
        if tag(el) == "table" and el.get("class") == "compare":
            heads = [t for t in el.iter() if tag(t) == "th" and t.get("scope") == "col"]
            rows = [t for t in el.iter() if tag(t) == "th" and t.get("scope") == "row"]
            if len(heads) != 4:
                warn(f"جدول مقایسه {len(heads)} تیتر ستون دارد")
            ok(f"جدول مقایسه: {len(heads)} ستون، {len(rows)} ردیف")

    # ---------- ۹) CSS ----------
    css_path = ROOT / "assets/css/main.css"
    css = css_path.read_text(encoding="utf-8")
    try:
        import tinycss2

        rules = tinycss2.parse_stylesheet(css, skip_comments=True, skip_whitespace=True)
        bad = [r for r in rules if r.type == "error"]
        if bad:
            for b in bad[:10]:
                err(f"خطای CSS: {b.message} در خط {b.source_line}")
        ok(f"CSS تجزیه شد: {len(rules)} قاعده")

        for m in re.finditer(r'url\("([^"]+)"\)', css):
            ref = m.group(1)
            if ref.startswith("data:"):
                continue
            target = (css_path.parent / ref).resolve()
            if not target.exists():
                err(f"فایل ارجاع‌شده در CSS وجود ندارد: {ref}")
    except Exception as exc:  # pragma: no cover
        err(f"تجزیه CSS شکست خورد: {exc}")

    # ---------- ۱۰) کنتراست ----------
    pairs = [
        ("متن اصلی روی سفید", "#334155", "#ffffff", 4.5),
        ("متن راهنما روی سفید", "#4b5b70", "#ffffff", 4.5),
        ("متن کوچک روی سفید", "#64748b", "#ffffff", 4.5),
        ("تیتر روی سفید", "#0b1220", "#ffffff", 4.5),
        ("متن برند روی سفید", "#0e7490", "#ffffff", 4.5),
        ("برند تیره روی سفید", "#0a5b71", "#ffffff", 4.5),
        ("دکمهٔ اصلی (سفید/برند)", "#ffffff", "#0b5c74", 4.5),
        ("برچسب برند", "#0a5b71", "#ecfeff", 4.5),
        ("هشدار", "#7c2d12", "#fff7ed", 4.5),
        ("متن فوتر", "#94a3b8", "#070d18", 4.5),
        ("لینک فوتر", "#a9b8cc", "#070d18", 4.5),
        ("متن روی بخش تیره", "#cbd5e1", "#0b1220", 4.5),
        ("متن ملایم روی بخش تیره", "#b6c4d6", "#0b1220", 4.5),
        ("متن کارت روی تیره", "#a9b8cc", "#0b1220", 4.5),
        ("نشان «نیازمند تأیید»", "#7c2d12", "#fff7ed", 4.5),
        ("حلقهٔ فوکوس", "#0e7490", "#ffffff", 3.0),
        ("سلول «ندارد» جدول", "#64748b", "#ffffff", 4.5),
        ("سلول «وابسته» جدول", "#92400e", "#ffffff", 4.5),
        ("کپشن ماکت", "#4b5b70", "#f7fbfd", 4.5),
    ]
    for label, fg, bg, minimum in pairs:
        ratio = contrast(fg, bg)
        if ratio < minimum:
            err(f"کنتراست {label}: {ratio:.2f} < {minimum}")
        else:
            notes.append(f"کنتراست {label}: {ratio:.2f}")

    # ---------- گزارش ----------
    print("== یادداشت‌ها ==")
    for n in notes:
        print("  ✓", n)
    print("\n== هشدارها ==")
    if warnings:
        for w in warnings:
            print("  !", w)
    else:
        print("  (هیچ)")
    print("\n== خطاها ==")
    if errors:
        for e in errors:
            print("  ✗", e)
    else:
        print("  (هیچ)")

    print(f"\nخلاصه: {len(errors)} خطا، {len(warnings)} هشدار")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
