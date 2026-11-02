/**
 * تست رفتاری DOM صفحهٔ فروش گپینه با jsdom (بدون مرورگر واقعی).
 *
 * این تست جای تست مرورگری را نمی‌گیرد و چیدمان/CSS را ارزیابی نمی‌کند؛
 * فقط رفتار اسکریپت‌ها، وضعیت ARIA و مسیرهای تعاملی را می‌آزماید.
 *
 * پیش‌نیاز:
 *   npm install --no-save jsdom
 * اجرا:
 *   node tools/qa/test_dom.mjs
 */
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { JSDOM, VirtualConsole } from "jsdom";

const here = path.dirname(fileURLToPath(import.meta.url));
const root = process.env.GAPINEH_ROOT
  ? path.resolve(process.env.GAPINEH_ROOT)
  : path.resolve(here, "../..");

let failures = 0;
let checks = 0;

function check(name, condition, detail = "") {
  checks += 1;
  if (condition) {
    console.log(`  ✓ ${name}`);
  } else {
    failures += 1;
    console.error(`  ✗ ${name}${detail ? " — " + detail : ""}`);
  }
}

function buildDom({ configOverride } = {}) {
  let html = fs.readFileSync(path.join(root, "index.html"), "utf8");
  const config = fs.readFileSync(path.join(root, "assets/js/config.js"), "utf8");
  const app = fs.readFileSync(path.join(root, "assets/js/app.js"), "utf8");

  const patchedConfig = configOverride
    ? config.replace(
        /window\.GAPINEH_CONFIG\s*=\s*\{/,
        `window.GAPINEH_CONFIG = Object.assign({`
      ).replace(/^\};\s*$/m, `}, ${JSON.stringify(configOverride)});`)
    : config;

  html = html
    .replace('<script src="assets/js/config.js" defer></script>', `<script>${patchedConfig}</script>`)
    .replace('<script src="assets/js/app.js" defer></script>', `<script>${app}</script>`);

  const errors = [];
  const virtualConsole = new VirtualConsole();
  virtualConsole.on("jsdomError", (err) => errors.push(err.message));
  virtualConsole.on("error", (msg) => errors.push(String(msg)));

  const dom = new JSDOM(html, {
    runScripts: "dangerously",
    pretendToBeVisual: true,
    url: "https://etehadwp.com/gapineh/",
    virtualConsole
  });

  return { dom, errors };
}

const wait = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

/* ---------------------------------------------------------------- */
console.log("\n۱) بارگذاری و سلامت اسکریپت‌ها");
const { dom, errors } = buildDom();
const { window } = dom;
const doc = window.document;
await wait(50);

check("بدون خطای اجرای اسکریپت", errors.length === 0, errors.join(" | "));
check("عنوان صفحه فارسی است", doc.title.includes("گپینه"));
check("config در window موجود است", Boolean(window.GAPINEH_CONFIG));

/* ---------------------------------------------------------------- */
console.log("\n۲) تب‌های پیش‌نمایش");
const tabs = [...doc.querySelectorAll('[role="tab"]')];
const panels = [...doc.querySelectorAll('[role="tabpanel"]')];
check("سه تب تعریف شده", tabs.length === 3, String(tabs.length));
check("سه پنل تعریف شده", panels.length === 3, String(panels.length));
check("در ابتدا فقط پنل اول باز است", !panels[0].hidden && panels[1].hidden && panels[2].hidden);
check("aria-selected اولیه درست است", tabs[0].getAttribute("aria-selected") === "true" && tabs[1].getAttribute("aria-selected") === "false");

tabs[1].dispatchEvent(new window.MouseEvent("click", { bubbles: true }));
check("کلیک تب دوم، پنل دوم را باز می‌کند", !panels[1].hidden && panels[0].hidden);
check("کلیک تب دوم، aria-selected را جابه‌جا می‌کند", tabs[1].getAttribute("aria-selected") === "true" && tabs[0].getAttribute("aria-selected") === "false");

// پیمایش کلید در RTL: ArrowRight باید به تب قبلی برود
tabs[1].dispatchEvent(new window.KeyboardEvent("keydown", { key: "ArrowRight", bubbles: true }));
check("ArrowRight در RTL به تب قبلی می‌رود", tabs[0].getAttribute("aria-selected") === "true");
tabs[0].dispatchEvent(new window.KeyboardEvent("keydown", { key: "End", bubbles: true }));
check("کلید End به آخرین تب می‌رود", tabs[2].getAttribute("aria-selected") === "true" && !panels[2].hidden);
check("تب غیرفعال tabindex=-1 دارد", tabs[0].tabIndex === -1 && tabs[2].tabIndex === 0);

/* ---------------------------------------------------------------- */
console.log("\n۳) منوی موبایل");
const navToggle = doc.getElementById("navToggle");
const nav = doc.getElementById("primaryNav");
check("منو در ابتدا بسته است", !nav.classList.contains("is-open") && navToggle.getAttribute("aria-expanded") === "false");
navToggle.dispatchEvent(new window.MouseEvent("click", { bubbles: true }));
check("کلیک دکمه، منو را باز می‌کند", nav.classList.contains("is-open") && navToggle.getAttribute("aria-expanded") === "true");
doc.dispatchEvent(new window.KeyboardEvent("keydown", { key: "Escape", bubbles: true }));
check("Escape منو را می‌بندد", !nav.classList.contains("is-open") && navToggle.getAttribute("aria-expanded") === "false");

navToggle.dispatchEvent(new window.MouseEvent("click", { bubbles: true }));
nav.querySelector("a").dispatchEvent(new window.MouseEvent("click", { bubbles: true }));
check("کلیک روی لینک منو را می‌بندد", !nav.classList.contains("is-open"));

/* ---------------------------------------------------------------- */
console.log("\n۴) گفت‌وگوی نمونه (آفلاین)");
const log = doc.getElementById("chatLog");
const form = doc.getElementById("chatForm");
const input = doc.getElementById("chatInput");
const before = log.children.length;

input.value = "پاسخ‌ها از کجا می‌آید؟";
form.dispatchEvent(new window.Event("submit", { bubbles: true, cancelable: true }));
check("پیام کاربر اضافه شد", log.querySelectorAll(".bubble--out").length === 1);
check("ورودی پس از ارسال خالی شد", input.value === "");
check("نشانگر «در حال نوشتن» نمایش داده شد", Boolean(log.querySelector(".bubble--typing")));

await wait(900);
const bubbles = log.querySelectorAll(".bubble--in");
check("پاسخ نمایشی اضافه شد", bubbles.length >= 2, String(bubbles.length));
check("نشانگر تایپ حذف شد", !log.querySelector(".bubble--typing"));
check("برچسب منبع نمایش داده شد", Boolean(log.querySelector(".source-chip")));
check("پاسخ به پرسش نامرتبط، پیام صادقانه می‌دهد", await (async () => {
  input.value = "هوا فردا چطور است؟";
  form.dispatchEvent(new window.Event("submit", { bubbles: true, cancelable: true }));
  await wait(900);
  const last = [...log.querySelectorAll(".bubble--in")].pop();
  return last.textContent.includes("پاسخ را نمی‌دانم");
})());
check("هیچ درخواست شبکه‌ای (fetch) در صفحه نیست", !fs.readFileSync(path.join(root, "assets/js/app.js"), "utf8").includes("fetch("));

/* ---------------------------------------------------------------- */
console.log("\n۵) پیکربندی تجاری — وضعیت پیش‌فرض (بدون قیمت/لینک)");
const disabled = doc.querySelector("[data-purchase]");
check("دکمهٔ خرید غیرفعال است، نه لینک ساختگی", disabled && disabled.tagName !== "A" && disabled.getAttribute("aria-disabled") === "true");
check("وضعیت قیمت «در انتظار اعلام» است", doc.body.textContent.includes("در انتظار اعلام مالک محصول"));
check("هیچ لینک خریدی به بازارگاه ساخته نشده", !doc.querySelector('[data-purchase-block] a[href*="rtl-theme"]'));

/* ---------------------------------------------------------------- */
console.log("\n۶) پیکربندی تجاری — با قیمت و لینک معتبر");
{
  const second = buildDom({
    configOverride: {
      purchaseUrl: "https://www.rtl-theme.com/gapineh/",
      price: "۱٬۴۹۰٬۰۰۰ تومان",
      support: "۶ ماه پشتیبانی"
    }
  });
  await wait(60);
  const d2 = second.dom.window.document;
  const buy = d2.querySelector('[data-purchase-block] a[href="https://www.rtl-theme.com/gapineh/"]');
  check("لینک خرید معتبر ساخته می‌شود", Boolean(buy));
  check("لینک خرید rel=noopener دارد", buy && buy.getAttribute("rel") === "noopener");
  check("قیمت در بلوک قیمت درج شد", d2.querySelector(".purchase__price b").textContent.includes("تومان"));
  check("شرط پشتیبانی جای‌گذاری شد", d2.body.textContent.includes("۶ ماه پشتیبانی"));
  check("نشان «در انتظار» برای قیمت برداشته شد", !d2.querySelector('[data-config="price"]') || !d2.querySelector('[data-config="price"]').classList.contains("pending"));
  check("با پیکربندی معتبر، خطای اسکریپت رخ نمی‌دهد", second.errors.length === 0, second.errors.join(" | "));
  second.dom.window.close();
}

/* ---------------------------------------------------------------- */
console.log("\n۷) پیکربندی تجاری — لینک نامعتبر رد می‌شود");
{
  const third = buildDom({ configOverride: { purchaseUrl: "javascript:alert(1)" } });
  await wait(60);
  const d3 = third.dom.window.document;
  check(
    "لینک نامعتبر ساخته نمی‌شود",
    !d3.querySelector('[data-purchase-block] a[href^="javascript"]') &&
      ![...d3.querySelectorAll("[data-purchase-block] a")].some((a) =>
        a.getAttribute("href").includes("alert")
      )
  );
  check("دکمهٔ غیرفعال باقی می‌ماند", Boolean(d3.querySelector("[data-purchase]")));
  third.dom.window.close();
}

/* ---------------------------------------------------------------- */
console.log("\n۸) منابع و ارجاع‌های داخلی");
const localRefs = new Set();
doc.querySelectorAll("[src], link[href]").forEach((el) => {
  const v = el.getAttribute("src") || el.getAttribute("href");
  if (v && !/^(https?:|data:|#)/.test(v)) localRefs.add(v);
});
for (const ref of localRefs) {
  check(`فایل موجود است: ${ref}`, fs.existsSync(path.join(root, ref)));
}

/* ---------------------------------------------------------------- */
console.log(`\nخلاصه: ${checks - failures}/${checks} بررسی موفق`);
dom.window.close();
process.exit(failures ? 1 : 0);
