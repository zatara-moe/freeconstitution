/* freeconstitution.org — reading preferences
 * Persists user choices in localStorage. No tracking.
 */
(function () {
  "use strict";

  var STORAGE_KEY = "fc-prefs-v1";
  var defaults = {
    size: 17,
    spacing: 1.6,
    font: "default",
    theme: "auto",
    italics: true,
  };

  function load() {
    try {
      var raw = localStorage.getItem(STORAGE_KEY);
      if (!raw) return Object.assign({}, defaults);
      return Object.assign({}, defaults, JSON.parse(raw));
    } catch (e) {
      return Object.assign({}, defaults);
    }
  }

  function save(prefs) {
    try { localStorage.setItem(STORAGE_KEY, JSON.stringify(prefs)); } catch (e) {}
  }

  function apply(prefs) {
    var root = document.documentElement;
    root.style.setProperty("--reading-font-size", prefs.size + "px");
    root.style.setProperty("--reading-line-height", prefs.spacing);
    root.dataset.font = prefs.font;
    root.dataset.italics = prefs.italics ? "on" : "off";
    if (prefs.theme === "auto") {
      root.removeAttribute("data-theme");
    } else {
      root.dataset.theme = prefs.theme;
    }
  }

  function bind(prefs) {
    var size = document.getElementById("pref-size");
    var spacing = document.getElementById("pref-spacing");
    var font = document.getElementById("pref-font");
    var theme = document.getElementById("pref-theme");
    var italics = document.getElementById("pref-italics");
    var reset = document.getElementById("prefs-reset");
    var toggle = document.getElementById("prefs-toggle");
    var panel = document.getElementById("prefs-panel");

    if (size) {
      size.value = prefs.size;
      size.addEventListener("input", function () {
        prefs.size = parseInt(this.value, 10);
        apply(prefs); save(prefs);
      });
    }
    if (spacing) {
      spacing.value = prefs.spacing;
      spacing.addEventListener("input", function () {
        prefs.spacing = parseFloat(this.value);
        apply(prefs); save(prefs);
      });
    }
    if (font) {
      font.value = prefs.font;
      font.addEventListener("change", function () {
        prefs.font = this.value;
        apply(prefs); save(prefs);
      });
    }
    if (theme) {
      theme.value = prefs.theme;
      theme.addEventListener("change", function () {
        prefs.theme = this.value;
        apply(prefs); save(prefs);
      });
    }
    if (italics) {
      italics.checked = prefs.italics;
      italics.addEventListener("change", function () {
        prefs.italics = this.checked;
        apply(prefs); save(prefs);
      });
    }
    if (reset) {
      reset.addEventListener("click", function () {
        prefs = Object.assign({}, defaults);
        apply(prefs); save(prefs);
        if (size) size.value = prefs.size;
        if (spacing) spacing.value = prefs.spacing;
        if (font) font.value = prefs.font;
        if (theme) theme.value = prefs.theme;
        if (italics) italics.checked = prefs.italics;
      });
    }
    if (toggle && panel) {
      toggle.addEventListener("click", function () {
        var open = !panel.hasAttribute("hidden");
        if (open) {
          panel.setAttribute("hidden", "");
          toggle.setAttribute("aria-expanded", "false");
        } else {
          panel.removeAttribute("hidden");
          toggle.setAttribute("aria-expanded", "true");
        }
      });
    }
  }

  var prefs = load();
  apply(prefs);
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", function () { bind(prefs); });
  } else {
    bind(prefs);
  }
})();
