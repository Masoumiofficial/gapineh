# راهنمای استقرار روی هاست

صفحه یک **سایت استاتیک تک‌صفحه‌ای** است: HTML + CSS + JS + فونت + تصویر.
هیچ مرحلهٔ build، Node.js یا پایگاه‌داده لازم نیست. فایل `gapineh.1.0.0.zip`
هم بخشی از صفحه نیست و نباید روی وب‌سرور عمومی قرار بگیرد.

## ۱. فایل‌هایی که باید آپلود شوند

```
index.html
assets/
  css/main.css
  js/app.js
  js/config.js          ← اطلاعات تجاری را اینجا کامل کنید
  fonts/vazirmatn-persian.woff2
  img/brand-mark.svg
  img/favicon.svg
  img/favicon-32.png
  img/apple-touch-icon.png
  img/og-cover.png
  img/screenshots/      ← پس از تهیهٔ اسکرین‌شات‌های واقعی
```

**آپلود نکنید:** `docs/`، `tools/`، `gapineh.1.0.0.zip`، `.git/`.

## ۲. مسیر مقصد و نشانی

- مسیر پیشنهادی (همان مسیر فعلی): `public_html/gapineh/`
- نشانی نهایی: `https://etehadwp.com/gapineh/`
- تمام مسیرهای داخل صفحه **نسبی** هستند، پس در زیرمسیر یا زیردامنه هم کار می‌کنند.

اگر دامنه یا مسیر تغییر کرد، این سه مورد را هم‌زمان اصلاح کنید:

1. `<link rel="canonical">`
2. `og:url`
3. `og:image` و `twitter:image` (باید **مطلق** و با HTTPS باشند)

## ۳. تعارض با وردپرس (مهم)

اگر `/gapineh/` روی همان نصبی است که وردپرس در ریشهٔ آن است:

- وردپرس فقط مسیرهایی را می‌گیرد که فایل واقعی نداشته باشند؛ پوشهٔ واقعی
  `gapineh/` با `index.html` معمولاً بدون مشکل سرو می‌شود.
- اگر هاست شما `.html` را در `DirectoryIndex` ندارد، در `.htaccess` همان پوشه بگذارید:

```apache
DirectoryIndex index.html index.php
```

- اگر روی نصب وردپرس، قالب یا افزونهٔ سئو نشانی `/gapineh/` را با یک برگه
  بازنویسی می‌کند، دو گزینه دارید: پوشه را به مسیر دیگری منتقل کنید و canonical را
  به‌روز کنید، یا همان محتوا را به‌صورت قالب برگهٔ سفارشی منتشر کنید
  (در این حالت هدر/فوتر وردپرس را حذف کنید تا ساختار صفحه تکراری نشود).

## ۴. کش و فشرده‌سازی (نمونهٔ Apache)

```apache
# assets/.htaccess
<IfModule mod_mime.c>
  AddType font/woff2 .woff2
  AddType image/svg+xml .svg
</IfModule>

<IfModule mod_deflate.c>
  AddOutputFilterByType DEFLATE text/html text/css application/javascript image/svg+xml
</IfModule>

<IfModule mod_expires.c>
  ExpiresActive On
  ExpiresByType text/html "access plus 0 seconds"
  ExpiresByType text/css "access plus 1 year"
  ExpiresByType application/javascript "access plus 1 year"
  ExpiresByType font/woff2 "access plus 1 year"
  ExpiresByType image/png "access plus 1 month"
  ExpiresByType image/svg+xml "access plus 1 month"
</IfModule>

<IfModule mod_headers.c>
  Header always set X-Content-Type-Options "nosniff"
  Header always set Referrer-Policy "strict-origin-when-cross-origin"
</IfModule>
```

اگر assets را با کش یک‌ساله سرو می‌کنید، پس از هر تغییر نام فایل را عوض کنید
یا پارامتر نسخه اضافه کنید (`main.css?v=2`). نام فونت هم اگر تغییر کرد، به‌روز شود.

نمونهٔ Nginx:

```nginx
location /gapineh/ {
    try_files $uri $uri/ /gapineh/index.html;
    add_header Cache-Control "no-cache";
}
location ~* ^/gapineh/assets/ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

## ۵. اقدامات پس از آپلود (چک‌لیست واقعی، نه فرضی)

1. `https://<دامنه>/gapineh/` را در پنجرهٔ خصوصی باز کنید؛ باید **بدون** خطای ۴۰۴
   و بدون پیام «JavaScript لازم است» کامل نمایش داده شود.
2. در تب Network بررسی کنید: هیچ درخواست ۴۰۴ (خصوصاً فونت و تصویر) و هیچ درخواست
   به دامنهٔ سوم نباشد.
3. در تب Console هیچ خطای قرمز نباشد. (تست DOM در این مخزن خطای اسکریپت را پوشش
   می‌دهد، اما خطاهای شبکه/امنیتی فقط در مرورگر دیده می‌شوند.)
4. عرض ۳۶۰px، ۷۶۸px و ۱۴۴۰px را با ابزار ریسپانسیو بررسی کنید.
5. راهبری با کلید Tab: پرش به محتوا → منو → دکمهٔ پیش‌نمایش → تب‌ها → FAQ → خرید.
   در موبایل، منو باید با Enter باز و با Escape بسته شود و فوکوس به دکمه برگردد.
6. Lighthouse (بدون تنظیمات خاص) اجرا و نتیجه را ثبت کنید؛ اگر اجرا نشد، عددی
   گزارش نکنید.
7. `https://validator.schema.org/` و Rich Results Test برای JSON-LD.
8. لینک‌های خارجی (`guide.html`، `etehadwp.com`، بازارگاه) را یک‌بار دستی باز کنید.

## ۶. بازگردانی نسخهٔ قبلی

پیش از جایگزینی، از پوشهٔ فعلی `gapineh/` یک کپی با تاریخ بگیرید
(مثلاً `gapineh-backup-1405-07-29/`). بازگردانی = جایگزینی همان پوشه؛
هیچ وابستگی سروری یا پایگاه‌داده‌ای درگیر نیست.
