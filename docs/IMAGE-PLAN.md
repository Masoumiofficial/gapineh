# نقشهٔ تصاویر — گپینه

قاعدهٔ حاکم: **تصویرسازی هوش مصنوعی هرگز جای اسکرین‌شات واقعی پنل را نمی‌گیرد.**
در این پروژه هر تصویر در یکی از دو دسته است:

- **مفهومی/ماکت کد** — با HTML/CSS ساخته شده، برچسب «ماکت مفهومی» دارد و داده‌های
  داخلش نمونه است. این‌ها تصویر فایل نیستند؛ متن و CSS هستند، پس با تغییر محصول
  به‌روزرسانی‌شان آسان است.
- **اسکرین‌شات واقعی** — باید از افزونهٔ نصب‌شده گرفته شود. تا آماده‌نشدن، قاب آن
  خالی می‌ماند.

## ۱. تصاویر موجود در مخزن

| فایل | کاربرد | ابعاد | نسبت | alt | lazy |
| --- | --- | --- | --- | --- | --- |
| `assets/img/brand-mark.svg` | لوگوی هدر و فوتر | برداری | ۱:۱ | تزئینی (`alt=""`؛ نام برند در متن کنارش هست) | ندارد (SVG کوچک) |
| `assets/img/favicon.svg` | فاوآیکون مدرن | برداری | ۱:۱ | — | — |
| `assets/img/favicon-32.png` | فاوآیکون جایگزین | ۳۲×۳۲ | ۱:۱ | — | — |
| `assets/img/apple-touch-icon.png` | آیکون iOS | ۱۸۰×۱۸۰ | ۱:۱ | — | — |
| `assets/img/og-cover.png` | تصویر Open Graph/Twitter (فقط متا) | ۱۲۰۰×۶۳۰ | ۱.۹:۱ | متن `og:image:alt` دارد | در صفحه نمایش داده نمی‌شود |
| `assets/fonts/vazirmatn-persian.woff2` | فونت متغیر (OFL) | ~۶۳KB | — | — | preload |

تصویر قهرمان صفحه، **تصویر فایل نیست**؛ یک ماکت CSS است (ویجت + اینباکس) با
`role="img"` و `aria-label` توصیفی، همراه کپشن «ماکت مفهومی؛ تصویر واقعی پنل نیست».

## ۲. اسکرین‌شات‌های واقعی موردنیاز (اقدام مالک محصول)

سه قاب در بخش «تصاویر محصول» رزرو شده‌اند. برای فعال‌کردن هر قاب:

1. افزونه را روی یک نصب آزمایشی وردپرس فعال کنید، تنظیمات را کامل کنید و دادهٔ
   واقعی (مکالمهٔ تستی) بسازید.
2. تصویر را با عرض حداکثر ۱۶۰۰px بگیرید (۳۲۴۰px برای Retina یا `srcset` اختیاری).
3. بخش‌های حساس را پاک کنید: کلید API، توکن تلگرام، شمارهٔ مشتری واقعی، ایمیل.
   اگر کلید در تصویر دیده می‌شود، همان بخش را با یک مستطیل هم‌رنگ پس‌زمینه بپوشانید.
4. فایل را با نام دقیق زیر در `assets/img/screenshots/` بگذارید:

| # | نام فایل | بخش مقصد | چه چیزی باید دیده شود | اندازهٔ پیشنهادی | alt پیشنهادی | کپشن | اولویت |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ۱ | `screenshots/inbox.png` | بخش ۱۲ — تصاویر محصول | فهرست گفت‌وگوها + پنل پاسخ اپراتور + دکمه‌های «پیشنهاد پاسخ» و «خلاصهٔ مکالمه» | ۱۲۸۰×۸۰۰ (یا ۱۶۰۰×۱۰۰۰) | «صندوق مکالمات گپینه در پیشخوان وردپرس؛ فهرست گفت‌وگوها و پنل پاسخ اپراتور» | صندوق مکالمات با شمارندهٔ خوانده‌نشده و واگذاری | بالا |
| ۲ | `screenshots/widget.png` | بخش ۱۲ | ویجت باز روی یک برگهٔ واقعی سایت، پاسخ با برچسب منبع | ۱۲۸۰×۸۰۰ | «ویجت گفت‌وگوی گپینه روی یک صفحهٔ وردپرس، با پاسخ همراه لینک منبع» | ویجت روی سایت | بالا |
| ۳ | `screenshots/settings.png` | بخش ۱۲ | تب «دستیار و دانش» و تب «اتصال» با مقادیر پوشانده‌شده | ۱۲۸۰×۸۰۰ | «تنظیمات گپینه در پیشخوان وردپرس؛ گروه‌های اتصال هوش مصنوعی، دانش سایت و امنیت داده» | تنظیمات و دانش سایت | متوسط |

ترتیب اولویت: ۱ و ۲ حتماً پیش از انتشار (اثبات قابلیت)، ۳ پس از آن.

5. در `index.html`، بلوک توضیح‌شدهٔ هر قاب را از حالت کامنت خارج کنید (داخل همان
   `<div class="shot__frame" data-shot>` نوشته شده است). با وجود فایل، اسکریپت
   `app.js` به‌طور خودکار تصویر را نمایش می‌دهد و قاب جای‌نگهدار را پنهان می‌کند؛
   اگر فایل نباشد، همان جای‌نگهدار می‌ماند و تصویر شکسته نمایش داده نمی‌شود.

نکته: اسکرین‌شات‌ها با `loading="lazy"` و `width`/`height` ثابت بارگذاری می‌شوند
تا CLS نداشته باشند. تصویر بالای صفحه هیچ‌وقت اسکرین‌شات نیست، پس مشکلی با LCP ندارد.

## ۳. تصاویر مفهومی — پرامپت‌های آماده (اختیاری)

اگر خواستید برای صفحهٔ بازاریابی/شبکه‌های اجتماعی تصویر مفهومی هم داشته باشید،
این پرامپت‌ها با هویت گپینه هم‌خوان‌اند. **هیچ‌کدام نباید در صفحه به‌جای اسکرین‌شات
استفاده شوند** و متن فارسی نباید داخل تصویر تولید شود (تیترها در HTML هستند).

**Image A — ترکیب قهرمان (۱۶:۹، ۱۶۰۰×۹۰۰، فایل: `assets/img/concept-hero.png`)**
> Premium software product marketing visual for a Persian RTL WordPress live-chat
> and AI customer-support plugin. A realistic desktop website mockup with a compact
> floating chat widget and a separate elegant support inbox panel. The interface
> communicates three concepts: AI answers grounded in website content, visible
> source references, and human-agent handoff. Clean SaaS art direction, precise
> spacing, restrained glass effects, professional lighting, realistic UI
> proportions, crisp details. No people, no stock photography, no fabricated
> analytics, no unreadable decorative text, no fake testimonials, no competitor
> branding. Clean negative space for a Persian headline. Wide 16:9.

**Image B — پاسخ با منبع (۴:۳، ۱۲۰۰×۹۰۰، فایل: `concept-answer-sources.png`)**
> Clean product-interface concept illustration for an AI website assistant. A
> Persian right-to-left chat conversation with a concise answer and a clearly
> separated source-reference area. Minimal SaaS dashboard style, realistic browser
> UI, restrained teal-and-slate palette, accessible contrast, subtle borders. No
> invented brand logos, no claims of guaranteed accuracy, no decorative AI brain,
> no neon effects. Conceptual mockup, landscape 4:3.

**Image C — صندوق اپراتور انسانی (۴:۳)**
> Polished conceptual interface visual for a WordPress support inbox: conversation
> list, central chat panel, a human-agent reply state, and a compact conversation
> summary area. Persian RTL layout, realistic spacing, professional support
> software aesthetic, clear hierarchy. No fabricated customer statistics, no fake
> reviews, no external messaging integrations. Conceptual UI mockup, landscape 4:3.

**Image D — تنظیمات وردپرس (۴:۳)**
> Realistic conceptual WordPress plugin settings interface in Persian RTL with
> organized groups for AI provider configuration, widget appearance, working hours,
> notifications, and data retention. Clean admin design, restrained palette,
> accessible form controls. No real API keys, no credentials, no invented
> integrations. Conceptual illustration only, landscape 4:3.

**Image E — جریان داده و حریم خصوصی (۱۶:۹)**
> Minimal technical product diagram for a WordPress live-chat plugin: a visitor, a
> WordPress website, the plugin's conversation-management layer, an external AI
> model provider API, and a human support agent, with clear directional arrows and
> concise grouping. Emphasize that required conversation data may be sent to the
> configured model provider. No claim that all processing is local. No security
> certification badges, no absolute privacy guarantees. Professional vector
> infographic, landscape 16:9.

## ۴. تصمیم‌های عملکردی تصویر

- تصویر Open Graph با اسکریپت محلی ساخته شده است (`tools/make_brand_assets.py`)
  تا متن فارسی درست و قابل بازتولید باشد.
- فونت صفحه به زیرمجموعهٔ فارسی محدود شده (۶۴KB، متغیر ۱۰۰–۹۰۰)؛ هیچ CDN فونتی
  در صفحه نیست تا روی هاست‌های ایران بلاک نشود.
- همهٔ تصاویر صفحه SVG/PNG محلی‌اند؛ هیچ درخواست به دامنهٔ سوم وجود ندارد.
- اگر تصویر تزئینی اضافه کردید که محتوای اطلاعاتی ندارد، `alt=""` بگذارید؛
  برای تصویر محتوایی، alt توصیفی بنویسید و آن را در `docs/EVIDENCE.md` هم ثبت کنید.
