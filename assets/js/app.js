/* =========================================================================
   گپینه — رفتار صفحهٔ فروش
   assets/js/app.js

   بدون وابستگی بیرونی. فقط رفتار لازم:
   1) هدر چسبان و حالت اسکرول
   2) منوی موبایل (دسترس‌پذیر، Escape، بازگشت فوکوس)
   3) تب‌های پیش‌نمایش با پیمایش کلید جهت‌دار (RTL)
   4) گفت‌وگوی نمونهٔ آفلاین (بدون درخواست شبکه)
   5) جای‌گذاری اطلاعات تجاری از assets/js/config.js
   6) نمایش تصاویر واقعی در صورت وجود فایل
   ========================================================================= */
(function () {
  "use strict";

  var doc = document;
  var cfg = window.GAPINEH_CONFIG || {};

  /* ---------------------------------------------------------------------
     ۱) هدر
     --------------------------------------------------------------------- */
  var header = doc.getElementById("siteHeader");
  if (header) {
    var onScroll = function () {
      header.classList.toggle("is-scrolled", window.scrollY > 8);
    };
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
  }

  /* ناوبری فعال با IntersectionObserver — بدون حرکت اضافی */
  var navLinks = Array.prototype.slice.call(
    doc.querySelectorAll('.nav a[href^="#"]')
  );
  var sections = navLinks
    .map(function (a) {
      var id = a.getAttribute("href").slice(1);
      var el = id ? doc.getElementById(id) : null;
      return el ? { link: a, el: el } : null;
    })
    .filter(Boolean);

  if ("IntersectionObserver" in window && sections.length) {
    var observer = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (!entry.isIntersecting) return;
          sections.forEach(function (pair) {
            var active = pair.el === entry.target;
            if (active) pair.link.setAttribute("aria-current", "true");
            else pair.link.removeAttribute("aria-current");
          });
        });
      },
      { rootMargin: "-45% 0px -50% 0px", threshold: 0 }
    );
    sections.forEach(function (pair) {
      observer.observe(pair.el);
    });
  }

  /* ---------------------------------------------------------------------
     ۲) منوی موبایل
     --------------------------------------------------------------------- */
  var navToggle = doc.getElementById("navToggle");
  var nav = doc.getElementById("primaryNav");

  if (navToggle && nav) {
    var closeNav = function (restoreFocus) {
      if (!nav.classList.contains("is-open")) return;
      nav.classList.remove("is-open");
      navToggle.setAttribute("aria-expanded", "false");
      if (restoreFocus) navToggle.focus();
    };

    navToggle.addEventListener("click", function () {
      var open = nav.classList.toggle("is-open");
      navToggle.setAttribute("aria-expanded", open ? "true" : "false");
      if (open) {
        var first = nav.querySelector("a");
        if (first) first.focus();
      }
    });

    nav.addEventListener("click", function (event) {
      if (event.target.closest("a")) closeNav(false);
    });

    doc.addEventListener("keydown", function (event) {
      if (event.key === "Escape") closeNav(true);
    });

    doc.addEventListener("click", function (event) {
      if (!nav.classList.contains("is-open")) return;
      if (nav.contains(event.target) || navToggle.contains(event.target)) return;
      closeNav(false);
    });

    window.addEventListener("resize", function () {
      if (window.innerWidth > 1040) closeNav(false);
    });
  }

  /* ---------------------------------------------------------------------
     ۳) تب‌های پیش‌نمایش
     --------------------------------------------------------------------- */
  var tabs = Array.prototype.slice.call(doc.querySelectorAll('[role="tab"]'));

  if (tabs.length) {
    var selectTab = function (tab, focus) {
      tabs.forEach(function (t) {
        var selected = t === tab;
        t.setAttribute("aria-selected", selected ? "true" : "false");
        t.tabIndex = selected ? 0 : -1;
        var panel = doc.getElementById(t.getAttribute("aria-controls"));
        if (panel) panel.hidden = !selected;
      });
      if (focus) tab.focus();
    };

    tabs.forEach(function (tab, index) {
      tab.addEventListener("click", function () {
        selectTab(tab, false);
      });

      tab.addEventListener("keydown", function (event) {
        var rtl = doc.documentElement.dir === "rtl";
        var next = rtl ? index - 1 : index + 1;
        var prev = rtl ? index + 1 : index - 1;
        var target = null;

        if (event.key === "ArrowRight") target = tabs[(next + tabs.length) % tabs.length];
        else if (event.key === "ArrowLeft") target = tabs[(prev + tabs.length) % tabs.length];
        else if (event.key === "Home") target = tabs[0];
        else if (event.key === "End") target = tabs[tabs.length - 1];

        if (target) {
          event.preventDefault();
          selectTab(target, true);
        }
      });
    });
  }

  /* ---------------------------------------------------------------------
     ۴) گفت‌وگوی نمونه — کاملاً آفلاین
     --------------------------------------------------------------------- */
  var log = doc.getElementById("chatLog");
  var form = doc.getElementById("chatForm");
  var input = doc.getElementById("chatInput");
  var starters = doc.getElementById("chatStarters");

  /* پاسخ‌های نوشته‌شده با دست؛ هیچ درخواستی ارسال نمی‌شود. */
  var answers = [
    {
      id: "knowledge",
      keys: ["منبع", "دانش", "محتوا", "سایت", "پاسخ‌ها", "پاسخ ها", "کجا"],
      text:
        "پاسخ‌ها از دانش سایت خودتان می‌آید: نوشته‌ها، برگه‌ها و (در صورت فعال‌بودن) محصولات ایندکس می‌شوند و مدل بر پایهٔ همان تکه‌ها پاسخ می‌سازد. زیر پاسخ، در صورت وجود، لینک صفحهٔ منبع می‌آید.",
      source: "منبع: تنظیمات «دستیار و دانش»"
    },
    {
      id: "human",
      keys: ["اپراتور", "انسان", "پشتیبان", "واگذار"],
      text:
        "بازدیدکننده می‌تواند از داخل ویجت درخواست پشتیبان بدهد. آن پیام به صندوق مکالمات پیشخوان می‌رسد و اپراتور در همان گفت‌وگو پاسخ دستی می‌دهد؛ از آن لحظه مکالمه از هوش مصنوعی جدا می‌شود.",
      source: "منبع: صندوق مکالمات و واگذاری"
    },
    {
      id: "cost",
      keys: ["هزینه", "قیمت", "پول", "توکن", "api", "دلار", "تومان"],
      text:
        "هزینهٔ هوش مصنوعی جزو قیمت افزونه نیست. گپینه با کلید API خودتان کار می‌کند و مصرف مدل را مستقیم به همان سرویس‌دهنده می‌پردازید. ساخت ایندکس معنایی هم مصرف embedding دارد.",
      source: "منبع: بخش «قیمت و خرید»"
    },
    {
      id: "woo",
      keys: ["ووکامرس", "سفارش", "فروشگاه", "محصول"],
      text:
        "با فعال‌بودن ووکامرس، محصولات به ایندکس دانش اضافه می‌شوند و مشتری می‌تواند وضعیت سفارش را بپرسد. وضعیت سفارش فقط پس از تطبیق ایمیل یا شمارهٔ ثبت‌شده روی همان سفارش نمایش داده می‌شود.",
      source: "منبع: امکانات ووکامرس"
    },
    {
      id: "setup",
      keys: ["نصب", "راه‌اندازی", "شروع", "فعال"],
      text:
        "راه‌اندازی چهار گام دارد: نصب و فعال‌سازی، اتصال کلید API و آزمایش اتصال، ساخت ایندکس دانش و تنظیم ویجت، و در پایان آزمایش پاسخ‌ها و اعلان‌ها با «بررسی سلامت».",
      source: "منبع: بخش «راه‌اندازی»"
    },
    {
      id: "privacy",
      keys: ["حریم", "داده", "امنیت", "کلید"],
      text:
        "کلید API فقط روی سرور ذخیره می‌شود و به مرورگر نمی‌رود. مکالمات در پایگاه‌دادهٔ وردپرس شما می‌مانند؛ اما برای تولید پاسخ، متن پرسش و تکه‌های محتوا به سرویس مدل انتخابی شما فرستاده می‌شود.",
      source: "منبع: بخش «حریم خصوصی و محدودیت‌ها»"
    }
  ];

  var normalize = function (text) {
    return (text || "")
      .toLowerCase()
      .replace(/[يى]/g, "ی")
      .replace(/ك/g, "ک")
      .replace(/[\u064B-\u065F\u0670]/g, "");
  };

  var findAnswer = function (question, id) {
    if (id) {
      var byId = answers.filter(function (item) {
        return item.id === id;
      })[0];
      if (byId) return byId;
    }

    var q = normalize(question);
    var best = null;
    answers.forEach(function (item) {
      item.keys.forEach(function (key) {
        if (q.indexOf(normalize(key)) !== -1) {
          best = best || item;
        }
      });
    });
    return best;
  };

  var addBubble = function (text, kind) {
    var el = doc.createElement("div");
    el.className = "bubble bubble--" + kind;
    el.textContent = text;
    if (log) {
      log.appendChild(el);
      log.scrollTop = log.scrollHeight;
    }
    return el;
  };

  var addSource = function (label) {
    var chip = doc.createElement("span");
    chip.className = "source-chip";
    chip.innerHTML =
      '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" ' +
      'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' +
      '<path d="M10 13a5 5 0 0 0 7 0l3-3a5 5 0 0 0-7-7l-1 1"/>' +
      '<path d="M14 11a5 5 0 0 0-7 0l-3 3a5 5 0 0 0 7 7l1-1"/></svg>';
    var span = doc.createElement("span");
    span.textContent = label + " · نمایشی";
    chip.appendChild(document.createTextNode(" "));
    chip.appendChild(span);
    if (log) {
      log.appendChild(chip);
      log.scrollTop = log.scrollHeight;
    }
  };

  var typing = false;

  var respond = function (question, id) {
    if (!log || typing) return;
    var match = findAnswer(question, id);

    typing = true;
    var indicator = doc.createElement("div");
    indicator.className = "bubble bubble--in bubble--typing";
    indicator.innerHTML = '<span class="dots" aria-hidden="true"></span>';
    indicator.appendChild(doc.createTextNode(" در حال نوشتن پاسخ نمایشی"));
    log.appendChild(indicator);
    log.scrollTop = log.scrollHeight;

    var note = match
      ? match
      : {
          text:
            "در این پیش‌نمایش پاسخی برای این پرسش آماده نیست؛ من پاسخ را نمی‌دانم. " +
            "در نسخهٔ واقعی، پاسخ از دانش سایت شما ساخته می‌شود و اگر منبعی پیدا نشود، " +
            "دستیار باید صادقانه بگوید که پاسخ را نمی‌داند.",
          source: null
        };

    window.setTimeout(function () {
      indicator.remove();
      addBubble(note.text, "in");
      if (note.source) addSource(note.source);
      typing = false;
    }, 620);

  };

  if (form && input) {
    form.addEventListener("submit", function (event) {
      event.preventDefault();
      var value = input.value.trim();
      if (!value) {
        input.focus();
        return;
      }
      addBubble(value, "out");
      input.value = "";
      respond(value);
    });
  }

  if (starters) {
    starters.addEventListener("click", function (event) {
      var btn = event.target.closest("button[data-question]");
      if (!btn) return;
      var q = btn.getAttribute("data-question");
      addBubble(q, "out");
      respond(q, btn.getAttribute("data-answer"));
    });
  }

  /* ---------------------------------------------------------------------
     ۵) پیکربندی تجاری
     --------------------------------------------------------------------- */
  var setPending = function (selector, value) {
    if (!value) return;
    var el = doc.querySelector(selector);
    if (!el) return;
    el.textContent = value;
    el.classList.remove("pending");
  };

  var priceEl = doc.querySelector(".purchase__price b");
  if (priceEl && cfg.price) {
    priceEl.textContent = cfg.price;
    var note = doc.querySelector(".purchase__price span");
    if (note) note.textContent = "قیمت اعلام‌شده توسط مالک محصول";
  }

  setPending('[data-config="license-scope"]', cfg.licenseScope);
  setPending('[data-config="delivery"]', cfg.delivery);
  setPending('[data-config="support"]', cfg.support);
  setPending('[data-config="updates"]', cfg.updates);
  setPending('[data-config="refund"]', cfg.refund);
  setPending('[data-config="price"]', cfg.price);

  /* دکمهٔ خرید فقط با نشانی معتبر ساخته می‌شود */
  var purchaseBlock = doc.querySelector("[data-purchase-block]");
  var placeholder = doc.querySelector("[data-purchase]");
  if (
    purchaseBlock &&
    placeholder &&
    typeof cfg.purchaseUrl === "string" &&
    /^https:\/\/[^\s]+$/.test(cfg.purchaseUrl)
  ) {
    var link = doc.createElement("a");
    link.className = "btn btn--primary btn--lg";
    link.href = cfg.purchaseUrl;
    link.rel = "noopener";
    link.textContent = "خرید گپینه";
    placeholder.replaceWith(link);

    var kicker = doc.querySelector(".purchase__kicker");
    if (kicker) {
      kicker.innerHTML =
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" ' +
        'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' +
        '<path d="M20 6 9 17l-5-5"/></svg> مسیر رسمی خرید فعال است';
    }
  }

  /* ---------------------------------------------------------------------
     ۶) تصاویر واقعی محصول
     هر تصویر تا وقتی فایل واقعی بارگذاری نشده مخفی است و قاب آن «جای
     اسکرین‌شات» می‌ماند؛ هیچ تصویر ساختگی جای اسکرین‌شات نمی‌گذارد.
     --------------------------------------------------------------------- */
  Array.prototype.slice.call(doc.querySelectorAll("[data-shot] img")).forEach(
    function (img) {
      var frame = img.closest("[data-shot]");
      if (!frame) return;

      var show = function () {
        if (!img.naturalWidth) return;
        img.hidden = false;
        frame.classList.add("has-image");
      };

      if (img.complete) show();
      img.addEventListener("load", show);
      img.addEventListener("error", function () {
        img.hidden = true;
        frame.classList.remove("has-image");
      });
    }
  );

})();
