#!/usr/bin/env python3
"""
ساخت تصاویر برند گپینه: og-cover.png، apple-touch-icon.png، favicon-32.png

پیش‌نیاز (فقط برای اجرای دوباره؛ خروجی‌ها در مخزن ذخیره شده‌اند):
    python3 -m venv .venv && .venv/bin/pip install pillow arabic-reshaper python-bidi
    python3 tools/make_brand_assets.py /path/to/vazirmatn/fonts/ttf

فونت Vazirmatn با مجوز OFL از مخزن rastikerdar/vazirmatn گرفته می‌شود.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import arabic_reshaper
from bidi.algorithm import get_display
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent.parent
IMG = ROOT / "assets" / "img"
FONT_DIR = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("/tmp/vazirmatn-33.003/fonts/ttf")

NAVY = (15, 23, 42)
MUTED = (71, 85, 105)
CYAN_700 = (14, 116, 144)
CYAN_500 = (6, 182, 212)
INDIGO = (79, 70, 229)
WHITE = (255, 255, 255)


def shape(text: str) -> str:
    return get_display(arabic_reshaper.reshape(text))


def font(name: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT_DIR / name), size)


def rtl(draw: ImageDraw.ImageDraw, xy_right: tuple[int, int], text: str, f, fill, spacing_hint: int = 0):
    """نوشتن متن راست‌چین: xy_right نقطهٔ بالا-راست متن است."""
    x, y = xy_right
    out = shape(text)
    w = draw.textlength(out, font=f)
    draw.text((x - w, y), out, font=f, fill=fill)
    return w


def rounded(draw, box, radius, fill, outline=None, width=1):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def make_og() -> None:
    W, H = 1200, 630
    base = Image.new("RGB", (W, H), (248, 250, 252))
    d = ImageDraw.Draw(base)

    # گرادیان ملایم پس‌زمینه
    for y in range(H):
        t = y / H
        r = int(240 + (238 - 240) * t)
        g = int(253 + (242 - 253) * t)
        b = int(255 + (255 - 255) * t)
        d.line([(0, y), (W, y)], fill=(r, g, b))

    # لکه‌های نوری محدود (بدون نئون)
    glow = Image.new("RGB", (W, H), (248, 250, 252))
    gd = ImageDraw.Draw(glow)
    gd.ellipse((620, -260, 1240, 260), fill=(207, 250, 254))
    gd.ellipse((-220, 330, 420, 860), fill=(224, 231, 255))
    glow = glow.filter(ImageFilter.GaussianBlur(90))
    base = Image.blend(base, glow, 0.55)
    d = ImageDraw.Draw(base)

    # خط تزئینی بالای صفحه
    d.rectangle((0, 0, W, 6), fill=(14, 116, 144))

    # ---- کارت پیش‌نمایش گفتگو (سمت چپ) ----
    card = (72, 104, 496, 560)
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle((card[0] + 8, card[1] + 22, card[2] + 8, card[3] + 22), 34, fill=(15, 23, 42, 38))
    shadow = shadow.filter(ImageFilter.GaussianBlur(26))
    base = Image.alpha_composite(base.convert("RGBA"), shadow).convert("RGB")
    d = ImageDraw.Draw(base)

    rounded(d, card, 34, WHITE, (226, 232, 240), 2)

    # هدر کارت
    rounded(d, (card[0] + 2, card[1] + 2, card[2] - 2, card[1] + 92), 32, (241, 245, 249))
    d.rectangle((card[0] + 2, card[1] + 60, card[2] - 2, card[1] + 92), fill=(241, 245, 249))
    d.ellipse((card[0] + 30, card[1] + 24, card[0] + 74, card[1] + 68), fill=CYAN_500)
    d.ellipse((card[0] + 44, card[1] + 40, card[0] + 60, card[1] + 56), fill=WHITE)
    rtl(d, (card[2] - 26, card[1] + 24), "گپینه", font("Vazirmatn-Bold.ttf", 26), NAVY)
    rtl(d, (card[2] - 26, card[1] + 58), "پاسخ‌گویی آنلاین", font("Vazirmatn-Regular.ttf", 18), MUTED)

    # پیام بازدیدکننده
    bubble_v = (card[0] + 118, card[1] + 112, card[2] - 26, card[1] + 178)
    rounded(d, bubble_v, 20, (14, 116, 144))
    rtl(d, (bubble_v[2] - 18, bubble_v[1] + 12), "برای این محصول", font("Vazirmatn-Medium.ttf", 20), WHITE)
    rtl(d, (bubble_v[2] - 18, bubble_v[1] + 40), "گارانتی دارید؟", font("Vazirmatn-Medium.ttf", 20), WHITE)

    # پاسخ دستیار
    bubble_a = (card[0] + 26, card[1] + 192, card[2] - 96, card[1] + 316)
    rounded(d, bubble_a, 20, (248, 250, 252), (226, 232, 240), 2)
    rtl(d, (bubble_a[2] - 16, bubble_a[1] + 14), "بله، شرایط گارانتی", font("Vazirmatn-Regular.ttf", 19), NAVY)
    rtl(d, (bubble_a[2] - 16, bubble_a[1] + 44), "در صفحهٔ گارانتی", font("Vazirmatn-Regular.ttf", 19), NAVY)
    rtl(d, (bubble_a[2] - 16, bubble_a[1] + 74), "و بازگشت آمده است.", font("Vazirmatn-Regular.ttf", 19), NAVY)

    # برچسب منبع
    src = (card[0] + 26, card[1] + 330, card[2] - 26, card[1] + 376)
    rounded(d, src, 14, (236, 254, 255), (165, 243, 252), 2)
    d.ellipse((src[0] + 18, src[1] + 14, src[0] + 32, src[1] + 28), fill=CYAN_700)
    rtl(d, (src[2] - 16, src[1] + 6), "منبع: گارانتی و بازگشت", font("Vazirmatn-Medium.ttf", 18), CYAN_700)

    # دکمهٔ انتقال به اپراتور
    btn = (card[0] + 26, card[1] + 392, card[2] - 26, card[1] + 446)
    rounded(d, btn, 16, (241, 245, 249))
    rtl(d, (card[2] - 46, card[1] + 406), "گفتگو با اپراتور انسانی", font("Vazirmatn-SemiBold.ttf", 19), NAVY)

    # ---- متن راست ----
    right = 1128
    max_w = right - 540

    def fit(text: str, fname: str, size: int, max_width: int):
        while size > 22:
            f = font(fname, size)
            if d.textlength(shape(text), font=f) <= max_width:
                return f, size
            size -= 1
        return font(fname, size), size

    # قرص نسخه
    pill_text = "افزونهٔ وردپرس · نسخهٔ ۱.۰.۰"
    pf = font("Vazirmatn-Medium.ttf", 20)
    pw = d.textlength(shape(pill_text), font=pf)
    pill = (right - pw - 44, 126, right, 174)
    rounded(d, pill, 24, (236, 254, 255), (165, 243, 252), 2)
    rtl(d, (right - 22, 136), pill_text, pf, CYAN_700)

    headline = [
        ("چت هوشمند و پشتیبانی انسانی", "Vazirmatn-Bold.ttf"),
        ("در یک افزونهٔ وردپرس", "Vazirmatn-Bold.ttf"),
    ]
    y = 214
    for line, fname in headline:
        f, size = fit(line, fname, 46, max_w)
        rtl(d, (right, y), line, f, NAVY)
        y += int(size * 1.42)

    y += 14
    sub = [
        ("پاسخ از دانش سایت، همراه با منبع؛",
         "و اپراتور انسانی در همان مکالمه."),
    ][0]
    for line in sub:
        f, _ = fit(line, "Vazirmatn-Regular.ttf", 26, max_w)
        rtl(d, (right, y), line, f, MUTED)
        y += 44

    # پابرگ برند
    d.line([(right - 460, 520), (right, 520)], fill=(203, 213, 225), width=1)
    rtl(d, (right, 540), "گپینه · Gapineh", font("Vazirmatn-Bold.ttf", 25), NAVY)
    rtl(d, (right, 578), "محصول اتحاد وردپرس · etehadwp.com", font("Vazirmatn-Regular.ttf", 19), MUTED)

    base.save(IMG / "og-cover.png", optimize=True)
    print("og-cover.png", (IMG / "og-cover.png").stat().st_size)


def make_icons() -> None:
    size = 1024
    icon = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(icon)
    d.rounded_rectangle((0, 0, size, size), 288, fill=CYAN_500)
    # حباب
    d.rounded_rectangle((300, 250, 724, 690), 110, fill=WHITE)
    d.polygon([(350, 660), (350, 780), (480, 690)], fill=WHITE)
    d.ellipse((392, 430, 448, 486), fill=CYAN_700)
    d.ellipse((576, 430, 632, 486), fill=CYAN_700)
    d.arc((430, 470, 594, 590), 20, 160, fill=CYAN_700, width=22)

    icon.resize((180, 180), Image.LANCZOS).save(IMG / "apple-touch-icon.png", optimize=True)
    icon.resize((64, 64), Image.LANCZOS).save(IMG / "favicon-64.png", optimize=True)
    icon.resize((32, 32), Image.LANCZOS).save(IMG / "favicon-32.png", optimize=True)
    print("icons done")


if __name__ == "__main__":
    make_og()
    make_icons()
