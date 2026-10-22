#!/usr/bin/env python3
"""Render Gapineh commercial cover banner (2100x1040) with Pillow + Vazirmatn.
With proper Persian/Arabic shaping via arabic_reshaper + python-bidi."""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math, os, random
import arabic_reshaper
from bidi.algorithm import get_display

W, H = 2100, 1040
OUT_PNG = "/home/user/gapineh/cover_assets/gapineh_cover_final.png"
OUT_JPG = "/home/user/gapineh/cover_assets/gapineh_cover_final.jpg"

FONTS = os.path.expanduser("~/.fonts")

def font(name, size):
    return ImageFont.truetype(os.path.join(FONTS, name), size)

def fa(text):
    """Reshape + bidi for Persian text in Pillow."""
    if not text:
        return text
    reshaped = arabic_reshaper.reshape(text)
    return get_display(reshaped)

def font_fa(name, size):
    return font(name, size)

# --- Fonts (Persian-capable via Vazirmatn) ---
f_title     = font_fa("Vazirmatn-Black.ttf", 248)
f_sub       = font_fa("Vazirmatn-SemiBold.ttf", 58)
f_tag       = font_fa("Vazirmatn-Medium.ttf", 44)
f_en_micro  = font_fa("Vazirmatn-Regular.ttf", 28)
f_chat_hdr  = font_fa("Vazirmatn-Bold.ttf", 30)
f_chat_meta = font_fa("Vazirmatn-Regular.ttf", 22)
f_chat_user = font_fa("Vazirmatn-Medium.ttf", 28)
f_chat_bot  = font_fa("Vazirmatn-Regular.ttf", 26)
f_chat_badge= font_fa("Vazirmatn-SemiBold.ttf", 20)
f_chat_time = font_fa("Vazirmatn-Regular.ttf", 18)
f_ui_label  = font_fa("Vazirmatn-Regular.ttf", 22)
f_small_hdr = font_fa("Vazirmatn-Bold.ttf", 22)
f_small_msg = font_fa("Vazirmatn-Regular.ttf", 18)
f_small_init= font_fa("Vazirmatn-Medium.ttf", 18)

# --- Palette ---
NAVY      = (16, 17, 38)
VIOLET_D  = (33, 25, 75)
PURPLE    = (85, 53, 207)
PURPLE_2  = (99, 72, 235)
LILAC     = (185, 169, 255)
ICE       = (244, 243, 250)
CYAN      = (34, 211, 238)
CYAN_D    = (6, 182, 212)
INK       = (28, 28, 48)
MUTED     = (120, 116, 150)
GREEN     = (65, 210, 120)
AMBER     = (255, 170, 50)

def lerp(a, b, t):
    return tuple(int(a[i] + (b[i]-a[i])*t) for i in range(len(a)))

def vgrad(size, top, bot):
    w,h = size
    img = Image.new("RGBA", size, (0,0,0,0))
    px = img.load()
    for y in range(h):
        t = y/(h-1); c = lerp(top, bot, t)
        for x in range(w):
            px[x,y] = c
    return img

def rgrad(size, center, radius, inner, outer=(0,0,0,0)):
    w,h = size; img = Image.new("RGBA", size, (0,0,0,0)); px = img.load()
    cx,cy = center
    for y in range(h):
        for x in range(w):
            d = math.hypot(x-cx, y-cy)
            if d > radius: continue
            t = d/radius
            a = int(inner[3]*(1-t)**2)
            r_ = int(inner[0]*(1-t)+outer[0]*t)
            g_ = int(inner[1]*(1-t)+outer[1]*t)
            b_ = int(inner[2]*(1-t)+outer[2]*t)
            px[x,y] = (r_,g_,b_,a)
    return img

def rounded_rect_mask(size, radius):
    w,h = size; m = Image.new("L", size, 0); d = ImageDraw.Draw(m)
    d.rounded_rectangle((0,0,w-1,h-1), radius=radius, fill=255)
    return m

def tsize(draw, text, fnt):
    b = draw.textbbox((0,0), text, font=fnt)
    return b[2]-b[0], b[3]-b[1]

def wrap_logical(draw, logical_text, fnt, max_w, pad_x):
    """Wrap logical (unshaped, non-bidi) Persian text by measuring the shaped/bidi
    version of each candidate line, then return a list of logical-line strings.
    Caller must fa() each line for display."""
    max_inner = max_w - pad_x*2
    tokens = logical_text.split(" ")
    lines_logical = []
    cur = []
    for tok in tokens:
        test_tokens = cur + [tok]
        test_line = " ".join(test_tokens)
        test_disp = fa(test_line)
        tw, _ = tsize(draw, test_disp, fnt)
        if tw > max_inner and cur:
            lines_logical.append(" ".join(cur)); cur = [tok]
        else:
            cur = test_tokens
    if cur: lines_logical.append(" ".join(cur))
    return lines_logical

# ---- Build canvas ----
img = vgrad((W,H), NAVY + (255,), VIOLET_D + (255,))

# Dot grid
ovr = Image.new("RGBA", (W,H), (0,0,0,0)); dov = ImageDraw.Draw(ovr)
random.seed(7)
for y in range(0,H,44):
    for x in range(0,W,44):
        cx = abs(x-W*0.3)/W; cy = abs(y-H*0.5)/H
        a = int(18*(1-min(1,cx*1.2))*(1-min(1,cy*0.8)))
        if a > 2:
            dov.ellipse((x-1,y-1,x+1,y+1), fill=(255,255,255,a))
img = Image.alpha_composite(img, ovr)

# Radial glows
for (cx,cy,r,ic) in [
    (1550, 350, 900, (120,90,255,90)),
    (1750, 900, 700, (34,211,238,50)),
    (300, 800, 800, (85,53,207,70)),
]:
    img = Image.alpha_composite(img, rgrad((W,H),(cx,cy),r,ic))

# Noise
noise = Image.new("RGBA", (W,H), (0,0,0,0)); random.seed(3); npx=noise.load()
for y in range(0,H,2):
    for x in range(0,W,2):
        v = random.randint(0,16)
        npx[x,y]=(255,255,255,v)
img = Image.alpha_composite(img, noise.filter(ImageFilter.GaussianBlur(0.4)))

draw = ImageDraw.Draw(img)

# --- Brand mark ---
def brand_logo(cx, cy, r, glow=False):
    if glow:
        size_glow = int(r*6)
        glw = Image.new("RGBA", (size_glow, size_glow), (0,0,0,0))
        gd = ImageDraw.Draw(glw)
        for rad, alpha in [(r*3,25),(r*2,50)]:
            gd.ellipse((size_glow//2-rad, size_glow//2-rad, size_glow//2+rad, size_glow//2+rad),
                       fill=(120,100,255,alpha))
        glw = glw.filter(ImageFilter.GaussianBlur(radius=r*0.7))
        img.alpha_composite(glw, (cx-size_glow//2, cy-size_glow//2))
    size = int(r*2)
    sq = Image.new("RGBA",(size,size),(0,0,0,0))
    sd = ImageDraw.Draw(sq)
    for i in range(size):
        t = i/(size-1); c = lerp(CYAN, PURPLE_2, t)
        sd.line((0,i,size,i), fill=c+(255,))
    mask = rounded_rect_mask((size,size), int(r*0.34))
    hl = Image.new("RGBA",(size,size),(0,0,0,0)); hld=ImageDraw.Draw(hl)
    hld.rounded_rectangle((int(-r*0.1), int(-r*0.1), int(r*1.55), int(r*0.8)),
                          radius=int(r*0.4), fill=(255,255,255,55))
    sqc = Image.new("RGBA",(size,size),(0,0,0,0))
    sqc.paste(sq,(0,0),mask); sqc = Image.alpha_composite(sqc, hl)
    img.alpha_composite(sqc, (int(cx-r), int(cy-r)))
    cd = ImageDraw.Draw(img)
    d1x, d1y = cx - r*0.32, cy - r*0.05
    d2x, d2y = cx + r*0.05, cy - r*0.05
    rr = r*0.12
    for dx_,dy_ in [(d1x,d1y),(d2x,d2y)]:
        cd.ellipse((dx_-rr,dy_-rr,dx_+rr,dy_+rr), fill=(255,255,255,240))
    sw = max(3, int(r*0.08))
    cd.arc((cx-r*0.35, cy-r*0.05, cx+r*0.08, cy+r*0.30),
           start=20, end=160, fill=(255,255,255,240), width=sw)
    ax,ay = cx+r*0.48, cy-r*0.45
    cd.ellipse((ax-r*0.07, ay-r*0.07, ax+r*0.07, ay+r*0.07), fill=CYAN_D+(180,))

# ---- Top-right pill + small logo ----
pill_en = "WordPress Plugin · v3.x"
ptw, pth = tsize(draw, pill_en, f_en_micro)
pill_x1 = W - 180
pill_h = pth + 22
pill_w = ptw + 40
pill_x0 = pill_x1 - pill_w
pill_y = 110
draw.rounded_rectangle((pill_x0, pill_y, pill_x1, pill_y+pill_h),
                       radius=pill_h//2, fill=(255,255,255,28),
                       outline=(255,255,255,70), width=2)
draw.text((pill_x1-20, pill_y+10), pill_en, font=f_en_micro, fill=(220,215,255), anchor="rt")
brand_logo(pill_x0 - 50, pill_y + pill_h//2, 28, glow=False)

# ---- Title (RIGHT) ----
title_fa = fa("گپینه")
sub_fa   = fa("چت هوشمند و پشتیبانی آنلاین وردپرس")
tag_fa   = fa("پاسخ هوشمند، پشتیبانی واقعی")

title_x, title_y = W - 180, 220
# title glow
glow_t = Image.new("RGBA",(W,H),(0,0,0,0)); gt=ImageDraw.Draw(glow_t)
bb = draw.textbbox((title_x, title_y), title_fa, font=f_title, anchor="rt")
gt.ellipse((bb[0]-150, bb[1]-100, bb[2]+100, bb[3]+100), fill=(120,90,255,60))
glow_t = glow_t.filter(ImageFilter.GaussianBlur(50))
img = Image.alpha_composite(img, glow_t); draw = ImageDraw.Draw(img)
draw.text((title_x, title_y), title_fa, font=f_title, fill=ICE, anchor="rt")

# Accent bar (cyan -> purple)
bar_w = 130
bar_y = title_y + 280
bar = Image.new("RGBA",(bar_w,10),(0,0,0,0)); bd=ImageDraw.Draw(bar)
for i in range(bar_w):
    t = i/(bar_w-1); c = lerp(CYAN, PURPLE_2, t)
    bd.line((i,0,i,10), fill=c+(230,))
img.alpha_composite(bar, (title_x - bar_w - 4, bar_y))

sub_y = title_y + 320
draw.text((title_x, sub_y), sub_fa, font=f_sub, fill=ICE, anchor="rt")
tag_y = sub_y + 110
draw.text((title_x, tag_y), tag_fa, font=f_tag, fill=LILAC, anchor="rt")

# English wordmark (Gapineh) with subtle divider
f_en_word = font("Vazirmatn-Medium.ttf", 36)
eny = tag_y + 78
draw.line((title_x - 280, eny + 24, title_x - 90, eny + 24), fill=(255,255,255,90), width=2)
draw.text((title_x - 80, eny), "Gapineh", font=f_en_word, fill=(225,222,250), anchor="rt")
draw.text((title_x - 300, eny + 4), "Smart Chat · Live Support", font=f_en_micro, fill=(180,175,215), anchor="rt")

# Feature chips (RTL — lay out from right to left)
def chip(x_right, y, icon_color, label_fa):
    label = fa(label_fa)
    lw, lh = tsize(draw, label, f_ui_label)
    px, py = 18, 12
    chip_h = lh + py*2
    chip_w = lw + px*2 + 28
    x1 = x_right; x0 = x1 - chip_w
    draw.rounded_rectangle((x0,y,x1,y+chip_h), radius=chip_h//2,
                           fill=(255,255,255,22), outline=(255,255,255,55), width=1)
    cx = x0 + 22; cy = y + chip_h//2
    draw.ellipse((cx-6, cy-6, cx+6, cy+6), fill=icon_color)
    draw.text((cx+18, y+py-2), label, font=f_ui_label, fill=(232,230,250), anchor="lt")
    return x0 - 20

chip_y = eny + 70
nx = chip(W-180, chip_y, CYAN, "پاسخ هوشمند بر اساس محتوای سایت")
nx = chip(nx, chip_y, LILAC, "اتصال به اپراتور انسانی")
chip(nx, chip_y, (150,120,255), "یکپارچه با وردپرس")

# Footer micro-text
foot_y = H - 80
draw.text((W-180, foot_y), "Gapineh · Smart Chat & Live Support for WordPress",
          font=f_en_micro, fill=(180,175,210), anchor="rt")
draw.text((180, foot_y), "Premium WordPress Plugin",
          font=f_en_micro, fill=(180,175,210), anchor="lt")

# ============ MAIN CHAT WIDGET ============
MW, MH = 620, 700
widget = Image.new("RGBA",(MW,MH),(0,0,0,0))
wd = ImageDraw.Draw(widget)
# Shadow
shadow = Image.new("RGBA",(MW+100,MH+100),(0,0,0,0)); shd=ImageDraw.Draw(shadow)
shd.rounded_rectangle((50,50,MW+50,MH+50), radius=34, fill=(0,0,0,160))
shadow = shadow.filter(ImageFilter.GaussianBlur(36))
widget_x, widget_y = 180, 180
img.alpha_composite(shadow, (widget_x-50, widget_y-30))

# Card body
body = Image.new("RGBA",(MW,MH),(0,0,0,0))
bd2 = ImageDraw.Draw(body)
header_h = 140
for i in range(MH):
    if i < header_h:
        t = i/max(1,header_h-1); c = lerp(CYAN, PURPLE_2, t*0.85)
        bd2.line((0,i,MW,i), fill=c+(255,))
    else:
        bd2.line((0,i,MW,i), fill=(247,246,252,255))
mask_w = rounded_rect_mask((MW,MH), 34)
widget.paste(body,(0,0),mask_w)
wd = ImageDraw.Draw(widget)

# Header icons (top bar) — X, moon, clock, expand, people on left (in RTL these appear left)
icon_y = 36
icon_xs = [60, 115, 170, 225, 280]
for cx in icon_xs:
    wd.ellipse((cx-13, icon_y-11, cx+13, icon_y+15), outline=(255,255,255,190), width=2)

# Online dot + title on right
lg_r = 38
lg_x = MW - 50 - lg_r
lg_y = header_h//2
# logo bg
wd.rounded_rectangle((lg_x-lg_r, lg_y-lg_r, lg_x+lg_r, lg_y+lg_r), radius=20, fill=(255,255,255,235))
wd.ellipse((lg_x-16, lg_y-8, lg_x-6, lg_y+2), fill=PURPLE_2)
wd.ellipse((lg_x+2, lg_y-8, lg_x+12, lg_y+2), fill=PURPLE_2)
wd.arc((lg_x-14, lg_y-6, lg_x+10, lg_y+14), start=20, end=160, fill=PURPLE_2, width=3)

# Title and subtitle (right aligned)
wd.text((MW-110, 46), fa("گفتگوی آنلاین"), font=f_chat_hdr, fill=ICE, anchor="rt")
wd.text((MW-110, 86), fa("دستیار هوشمند · پشتیبانی آنلاین"), font=f_chat_meta, fill=(235,232,255), anchor="rt")
# Online green dot on left side
st_cx, st_cy = 58, header_h//2 + 4
wd.ellipse((st_cx-15, st_cy-15, st_cx+15, st_cy+15), fill=(65,210,120,70))
wd.ellipse((st_cx-8, st_cy-8, st_cx+8, st_cy+8), fill=GREEN)

# divider
wd.line((24, header_h, MW-24, header_h), fill=(0,0,0,22), width=1)

# Chat bubble helper (Persian already shaped by caller)
def draw_bubble(canvas_img, d, y, logical_text, side, fnt, badge=None, time_text="۱۶:۴۵"):
    pad_x, pad_y = 22, 18
    margin_x = 30
    max_w = MW - 100
    # Wrap in logical space, then shape+display each line
    logical_lines = wrap_logical(d, logical_text, fnt, max_w, pad_x)
    disp_lines = [fa(ln) for ln in logical_lines]
    lh = fnt.size + 14
    badge_h = 36 if badge else 0
    text_h = lh*len(disp_lines) + pad_y*2
    bh = text_h + badge_h

    if side == "user":
        bw = min(max_w, max(tsize(d, ln, fnt)[0] for ln in disp_lines) + pad_x*2)
        x1 = MW - margin_x; x0 = x1 - bw
        bub = Image.new("RGBA",(bw,text_h),(0,0,0,0)); bbd=ImageDraw.Draw(bub)
        for i in range(text_h):
            t=i/max(1,text_h-1); c=lerp(CYAN,PURPLE_2,t); bbd.line((0,i,bw,i),fill=c+(255,))
        mb = rounded_rect_mask((bw,text_h),24)
        canvas_img.paste(bub,(x0,y),mb)
        ty = y + pad_y - 4
        for ln in disp_lines:
            d.text((x1-pad_x, ty), ln, font=fnt, fill=ICE, anchor="rt"); ty += lh
        d.text((x1, y+text_h+6), fa(time_text), font=f_chat_time, fill=MUTED, anchor="rt")
        return y + bh + 18
    else:
        bw = min(max_w, max(tsize(d, ln, fnt)[0] for ln in disp_lines) + pad_x*2)
        x0 = margin_x; x1 = x0 + bw
        d.rounded_rectangle((x0,y,x1,y+text_h), radius=24,
                            fill=(255,255,255,255), outline=(225,222,240,255), width=1)
        ty = y+pad_y-4
        for ln in disp_lines:
            d.text((x0+pad_x, ty), ln, font=fnt, fill=INK, anchor="lt"); ty += lh
        if badge:
            badge_disp = {**badge, "text": fa(badge["text"])}
            bw_b, bh_b = tsize(d, badge_disp["text"], f_chat_badge)
            bx0 = x0 + pad_x
            by = y + text_h + 4
            d.rounded_rectangle((bx0, by, bx0+bw_b+20, by+bh_b+10),
                                radius=(bh_b+10)//2, fill=badge_disp["bg"],
                                outline=badge_disp.get("outline", badge_disp["bg"]), width=1)
            d.text((bx0+10, by+3), badge_disp["text"], font=f_chat_badge, fill=badge_disp["fg"], anchor="lt")
        d.text((x1, y+text_h+6), fa(time_text), font=f_chat_time, fill=MUTED, anchor="lt")
        return y + bh + 18

cy = header_h + 28
cy = draw_bubble(widget, wd, cy,
                 "سلام! من دستیار هوشمند گپینه هستم، بفرمایید چطور می‌تونم کمکتون کنم؟",
                 "bot", f_chat_bot, time_text="۱۶:۴۵")
cy = draw_bubble(widget, wd, cy,
                 "چطور سفارش خودم را پیگیری کنم؟",
                 "user", f_chat_user, time_text="۱۶:۴۵")
cy = draw_bubble(widget, wd, cy,
                 "اطلاعات مربوط به پیگیری سفارش را در راهنمای سایت پیدا کردم. لطفاً از پنل کاربری بخش سفارشات کد رهگیری را وارد کنید.",
                 "bot", f_chat_bot,
                 badge={"text": "پاسخ هوشمند", "bg":(232,228,255), "fg":PURPLE,
                        "outline":(205,200,245)},
                 time_text="۱۶:۴۶")

# human handoff pill
pill_txt = fa("در حال اتصال به اپراتور انسانی...")
pw, ph = tsize(wd, pill_txt, f_chat_meta)
px = (MW - pw)//2 - 12
pill_y2 = cy + 4
wd.rounded_rectangle((px, pill_y2, px+pw+28, pill_y2+ph+12),
                     radius=(ph+12)//2, fill=(255,245,220), outline=(240,210,140))
wd.ellipse((px+12, pill_y2+ph//2, px+22, pill_y2+ph//2+10), fill=AMBER)
wd.text((px+30, pill_y2+5), pill_txt, font=f_chat_meta, fill=(140,90,20), anchor="lt")
cy = pill_y2 + ph + 24

cy = draw_bubble(widget, wd, cy,
                 "سلام، سجاد هستم. شماره سفارش را بفرمایید.",
                 "bot", f_chat_bot,
                 badge={"text": "اپراتور آنلاین", "bg":(220,248,255), "fg":(6,130,160),
                        "outline":(170,230,245)},
                 time_text="۱۶:۴۷")

# Input bar
inp_y = MH - 90
wd.rounded_rectangle((26, inp_y, MW-26, inp_y+60), radius=30,
                     fill=(242,240,250), outline=(220,218,235))
wd.text((48, inp_y+18), fa("پیام خود را بنویسید..."), font=f_chat_meta, fill=MUTED, anchor="lt")
# attach icon (clip)
wd.arc((52, inp_y+20, 68, inp_y+38), start=200, end=20, fill=MUTED, width=2)
# Send
sr = 24; sx = MW-26-20-sr; sy = inp_y+30
wd.ellipse((sx-sr, sy-sr, sx+sr, sy+sr), fill=PURPLE_2)
wd.polygon([(sx-9,sy-8),(sx+9,sy),(sx-9,sy+8)], fill=ICE)

# Paste
img.alpha_composite(widget, (widget_x, widget_y))

# ============ SMALL FLOATING OPERATOR CARD ============
SW, SH = 420, 270
small = Image.new("RGBA",(SW,SH),(0,0,0,0))
sd = ImageDraw.Draw(small)
ssh = Image.new("RGBA",(SW+60,SH+60),(0,0,0,0)); sshd=ImageDraw.Draw(ssh)
sshd.rounded_rectangle((30,30,SW+30,SH+30), radius=30, fill=(0,0,0,150))
ssh = ssh.filter(ImageFilter.GaussianBlur(28))
small_x = widget_x + MW - 50
small_y = widget_y + MH - 260
img.alpha_composite(ssh, (small_x-30, small_y-10))

# card body (white)
sbody = Image.new("RGBA",(SW,SH),(255,255,255,252))
sh_h = 78
# gradient header
for i in range(sh_h):
    t=i/max(1,sh_h-1); c=lerp((40,30,100),(90,60,220),t)
    for xx in range(SW):
        sbody.putpixel((xx,i), c+(255,))
msk_s = rounded_rect_mask((SW,SH),30)
small.paste(sbody,(0,0),msk_s)
sd = ImageDraw.Draw(small)
sd.line((0,sh_h,SW,sh_h), fill=(0,0,0,22))
sd.text((SW-24,22), fa("پشتیبانی آنلاین"), font=f_small_hdr, fill=ICE, anchor="rt")
sd.text((SW-24,50), fa("اپراتور: سجاد"), font=f_chat_meta, fill=(220,215,255), anchor="rt")
ar=22; ax,ay=24+ar, sh_h//2
sd.ellipse((ax-ar,ay-ar,ax+ar,ay+ar), fill=LILAC)
sd.text((ax,ay+2), fa("س"), font=f_small_init, fill=PURPLE, anchor="mm")
sd.ellipse((ax+ar-7,ay+ar-11,ax+ar+3,ay+ar-1), fill=GREEN)

def small_bubble(can, dd, y, logical_text, side, fnt):
    pad_x, pad_y = 12, 10
    max_w = SW - 60
    logical_lines = wrap_logical(dd, logical_text, fnt, max_w, pad_x)
    disp_lines = [fa(ln) for ln in logical_lines]
    lh = fnt.size+8
    bh = lh*len(disp_lines)+pad_y*2
    if side=="user":
        bw = min(max_w, max(tsize(dd,ln,fnt)[0] for ln in disp_lines)+pad_x*2)
        x1=SW-22; x0=x1-bw
        bb=Image.new("RGBA",(bw,bh),(0,0,0,0)); bbd=ImageDraw.Draw(bb)
        for i in range(bh):
            t=i/max(1,bh-1); c=lerp(CYAN,PURPLE_2,t); bbd.line((0,i,bw,i),fill=c+(255,))
        mb=rounded_rect_mask((bw,bh),16)
        can.paste(bb,(x0,y),mb)
        ty=y+pad_y-3
        for ln in disp_lines:
            dd.text((x1-pad_x,ty),ln,font=fnt,fill=ICE,anchor="rt"); ty+=lh
        return y+bh+10
    else:
        bw=min(max_w,max(tsize(dd,ln,fnt)[0] for ln in disp_lines)+pad_x*2)
        x0=22; x1=x0+bw
        dd.rounded_rectangle((x0,y,x1,y+bh),radius=16,
                             fill=(242,240,250),outline=(225,222,240))
        ty=y+pad_y-3
        for ln in disp_lines:
            dd.text((x0+pad_x,ty),ln,font=fnt,fill=INK,anchor="lt"); ty+=lh
        return y+bh+10

cy_s = sh_h + 20
cy_s = small_bubble(small, sd, cy_s, "ممنون از راهنمایی شما 🙏", "user", f_small_msg)
cy_s = small_bubble(small, sd, cy_s, "خواهش می‌کنم، هر سوال دیگری بود در خدمتم.", "bot", f_small_msg)
# typing indicator
ty_y = cy_s + 6
sd.rounded_rectangle((22, ty_y, 88, ty_y+26), radius=13, fill=(242,240,250))
for i,dx in enumerate([14,32,50]):
    sd.ellipse((22+dx, ty_y+9, 22+dx+8, ty_y+17), fill=MUTED)

img.alpha_composite(small, (small_x, small_y))

# Connector flow line
cn = Image.new("RGBA",(W,H),(0,0,0,0)); cnd=ImageDraw.Draw(cn)
pts=[]
for i in range(40):
    t=i/39
    x = (widget_x + MW - 80) - 180*t + 120*math.sin(t*3.14)
    y = (small_y + 80) - 180*t
    pts.append((x,y))
for i in range(len(pts)-1):
    a = int(110*(1 - i/len(pts)))
    cnd.line((pts[i],pts[i+1]), fill=(*CYAN,a), width=3)
cn = cn.filter(ImageFilter.GaussianBlur(2.5))
img = Image.alpha_composite(img, cn)

# Flow dots
random.seed(11)
for i in range(10):
    t=i/9
    x = int((widget_x+MW-80)-180*t+120*math.sin(t*3.14))
    y = int((small_y+80)-180*t)
    r = 4 + (i%2)*2
    col = CYAN if i%3!=2 else LILAC
    d = ImageDraw.Draw(img)
    d.ellipse((x-r,y-r,x+r,y+r), fill=(*col,210))

# Vignette
vig = Image.new("RGBA",(W,H),(0,0,0,0)); vd=ImageDraw.Draw(vig)
for i in range(100):
    t=i/99; a=int(70*(1-t))
    vd.rectangle((i,i,W-i,H-i), outline=(0,0,0,a))
img = Image.alpha_composite(img, vig)

# Save
rgb = img.convert("RGB")
rgb.save(OUT_PNG, "PNG", optimize=True)
rgb.save(OUT_JPG, "JPEG", quality=95, subsampling=0)
print(f"Saved: {OUT_PNG} ({img.size})")
print(f"Saved: {OUT_JPG}")
