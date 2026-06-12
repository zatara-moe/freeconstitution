/* freeconstitution.org, reading preferences + navigation
 * Text size, dark page, back-to-top, sticky sections.
 * All localStorage, nothing leaves the device.
 */
(function () {
  "use strict";

  /* ---- Reading prefs ---- */
  var KEY = "fc-prefs-v2";
  var defaults = { size: 18, theme: "light" };

  function load() {
    try {
      var raw = localStorage.getItem(KEY);
      return raw ? Object.assign({}, defaults, JSON.parse(raw)) : Object.assign({}, defaults);
    } catch (e) {
      return Object.assign({}, defaults);
    }
  }

  function save(p) {
    try { localStorage.setItem(KEY, JSON.stringify(p)); } catch (e) {}
  }

  function apply(p) {
    document.documentElement.style.setProperty("--reading-size", p.size + "px");
    if (p.theme === "dark") {
      document.documentElement.setAttribute("data-theme", "dark");
    } else {
      document.documentElement.removeAttribute("data-theme");
    }
    var toggle = document.querySelector("[data-theme-toggle]");
    if (toggle) {
      toggle.setAttribute("aria-pressed", p.theme === "dark" ? "true" : "false");
      toggle.textContent = p.theme === "dark" ? "Light page" : "Dark page";
    }
  }

  var prefs = load();
  apply(prefs);

  var bar = document.querySelector("[data-prefs]");
  if (bar) {
    bar.hidden = false;
    var down = bar.querySelector("[data-size-down]");
    var up = bar.querySelector("[data-size-up]");
    var toggle = bar.querySelector("[data-theme-toggle]");
    if (down) down.addEventListener("click", function () {
      prefs.size = Math.max(15, prefs.size - 1);
      apply(prefs); save(prefs);
    });
    if (up) up.addEventListener("click", function () {
      prefs.size = Math.min(26, prefs.size + 1);
      apply(prefs); save(prefs);
    });
    if (toggle) toggle.addEventListener("click", function () {
      prefs.theme = prefs.theme === "dark" ? "light" : "dark";
      apply(prefs); save(prefs);
    });
  }

  /* ---- Back to top ---- */
  var btt = document.querySelector(".back-to-top");
  if (btt) {
    var scrollThreshold = 500;
    var ticking = false;
    function checkScroll() {
      if (window.scrollY > scrollThreshold) {
        btt.classList.add("visible");
      } else {
        btt.classList.remove("visible");
      }
      ticking = false;
    }
    window.addEventListener("scroll", function () {
      if (!ticking) { requestAnimationFrame(checkScroll); ticking = true; }
    }, { passive: true });
    btt.addEventListener("click", function () {
      window.scrollTo({ top: 0, behavior: "smooth" });
    });
    checkScroll();
  }

  /* ---- Sticky section bar ---- */
  var stickyBar = document.querySelector(".sticky-sections");
  var sectionChips = document.querySelector(".section-chips") || document.querySelector(".doc .eyebrow");
  if (stickyBar && sectionChips) {
    var stickyLinks = stickyBar.querySelectorAll("a[data-section]");
    var sectionEls = [];
    stickyLinks.forEach(function (link) {
      var target = document.getElementById(link.getAttribute("data-section"));
      if (target) sectionEls.push({ el: target, link: link });
    });

    var sticking = false;
    function checkSticky() {
      var chipsRect = sectionChips.getBoundingClientRect();
      var shouldStick = chipsRect.bottom < 0;
      if (shouldStick !== sticking) {
        sticking = shouldStick;
        stickyBar.classList.toggle("visible", sticking);
      }
      // Highlight active section
      if (sticking && sectionEls.length) {
        var activeIdx = 0;
        for (var i = sectionEls.length - 1; i >= 0; i--) {
          if (sectionEls[i].el.getBoundingClientRect().top < 120) {
            activeIdx = i;
            break;
          }
        }
        sectionEls.forEach(function (s, idx) {
          s.link.classList.toggle("active", idx === activeIdx);
        });
      }
    }
    var stickyTicking = false;
    window.addEventListener("scroll", function () {
      if (!stickyTicking) {
        requestAnimationFrame(function () { checkSticky(); stickyTicking = false; });
        stickyTicking = true;
      }
    }, { passive: true });
    checkSticky();
  }

  /* ---- Mobile nav active state ---- */
  var mobileNav = document.querySelector(".mobile-nav");
  if (mobileNav) {
    var path = window.location.pathname;
    mobileNav.querySelectorAll("a").forEach(function (a) {
      var href = a.getAttribute("href");
      if (href === "/" && path === "/") {
        a.classList.add("active");
      } else if (href !== "/" && path.startsWith(href.replace(/\/$/, ""))) {
        a.classList.add("active");
      }
    });
  }
})();
