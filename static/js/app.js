/* freeconstitution.org app script.
 * Display settings, search, word definitions, quick checks, progress,
 * paths, offline situation cards, memorize. Everything stays on this
 * device (localStorage). No tracking, no third parties.
 */
(function () {
  "use strict";
  var d = document, html = d.documentElement;
  var $ = function (s, r) { return (r || d).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || d).querySelectorAll(s)); };
  function get(k, def) { try { var v = localStorage.getItem(k); return v ? JSON.parse(v) : def; } catch (e) { return def; } }
  function put(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) {} }
  function esc(s) { return String(s).replace(/[&<>"']/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]; }); }
  var PAGE = d.body.getAttribute("data-page") || location.pathname;

  /* ---------- Display settings ---------- */
  var DEF = { size: "m", spacing: "normal", font: "hyper", theme: "", depth: "standard", focus: false };
  var prefs = Object.assign({}, DEF, get("fc-display", {}));
  function applyPrefs() {
    ["size", "spacing", "font", "theme", "depth"].forEach(function (k) {
      if (prefs[k]) html.setAttribute("data-" + k, prefs[k]); else html.removeAttribute("data-" + k);
    });
    if (prefs.focus) html.setAttribute("data-focus", "on"); else html.removeAttribute("data-focus");
    $$(".focus-exit").forEach(function (b) { b.hidden = !prefs.focus; });
    $$("[data-toggle-focus]").forEach(function (b) {
      if (!b.classList.contains("focus-exit")) b.lastChild.textContent = prefs.focus ? " Turn off focus" : " Turn on focus";
    });
    var deep = prefs.depth === "deep";
    $$("details[data-deep-open]").forEach(function (x) { if (deep) x.open = true; });
    if (deep) $$("[data-compare]").forEach(function (c) { setOrig(c, true); });
  }
  function savePrefs() { put("fc-display", prefs); applyPrefs(); }
  var form = $("[data-display-form]");
  if (form) {
    ["size", "spacing", "font", "theme", "depth"].forEach(function (k) {
      var cur = prefs[k] || (k === "theme" ? (matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light") : DEF[k]);
      var r = form.querySelector('input[name="' + k + '"][value="' + cur + '"]');
      if (r) r.checked = true;
    });
    form.addEventListener("change", function (e) {
      if (e.target.name) { prefs[e.target.name] = e.target.value; savePrefs(); }
    });
  }
  $$("[data-toggle-focus]").forEach(function (b) {
    b.addEventListener("click", function () { prefs.focus = !prefs.focus; savePrefs(); if (prefs.focus) closeAll(); });
  });
  applyPrefs();

  /* ---------- Dialogs ---------- */
  var dispDlg = $("#display-dialog"), searchDlg = $("#search-dialog");
  function openDlg(dl) {
    if (!dl) return;
    closeAll();
    if (dl.showModal) dl.showModal(); else dl.setAttribute("open", "");
  }
  function closeAll() { $$("dialog[open]").forEach(function (x) { x.close ? x.close() : x.removeAttribute("open"); }); }
  $$("[data-open-display]").forEach(function (b) { b.addEventListener("click", function () { openDlg(dispDlg); }); });
  $$("[data-open-search]").forEach(function (b) { b.addEventListener("click", function () { openSearch(); }); });
  $$("dialog [data-close]").forEach(function (b) { b.addEventListener("click", closeAll); });
  $$("dialog").forEach(function (dl) {
    dl.addEventListener("click", function (e) { if (e.target === dl) closeAll(); });
  });

  /* ---------- Keyboard ---------- */
  d.addEventListener("keydown", function (e) {
    var t = e.target, typing = t && (t.tagName === "INPUT" || t.tagName === "TEXTAREA" || t.isContentEditable);
    if (e.metaKey || e.ctrlKey || e.altKey) return;
    if (e.key === "Escape") { hidePop(); closeScreen(); return; }
    if (typing) return;
    var k = e.key.toLowerCase();
    if (e.key === "/") { e.preventDefault(); openSearch(); }
    else if (k === "d") { openDlg(dispDlg); }
    else if (k === "t") {
      var order = ["light", "sepia", "dark"], cur = prefs.theme || (matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
      prefs.theme = order[(order.indexOf(cur) + 1) % 3]; savePrefs();
      var r = form && form.querySelector('input[name="theme"][value="' + prefs.theme + '"]'); if (r) r.checked = true;
    }
    else if (k === "g") { prefs.focus = !prefs.focus; savePrefs(); }
  });

  /* ---------- Search ---------- */
  var INDEX = null, loading = null;
  var ICON = {};
  function loadIndex() {
    if (INDEX) return Promise.resolve(INDEX);
    if (!loading) loading = fetch("/search-index.json").then(function (r) { return r.json(); }).then(function (j) { INDEX = j; return j; });
    return loading;
  }
  function openSearch() {
    openDlg(searchDlg);
    var inp = searchDlg && searchDlg.querySelector("[data-search-input]");
    if (inp) { inp.focus(); inp.select(); if (!inp.value) showHints(searchDlg.querySelector("[data-search-results]")); }
    loadIndex();
  }
  function showHints(box) {
    if (!box) return;
    var tips = ["phone search", "remain silent", "vote", "speech at school", "warrant", "citizen", "protest", "president"];
    box.innerHTML = '<p class="sr-group">Try</p>' + tips.map(function (t) { return '<a class="sr" href="#" data-try="' + t + '"><span><span class="sr-t">' + t + "</span></span></a>"; }).join("");
  }
  var SYN = { cops: "police", cop: "police", officer: "police", ice: "immigration", phone: "phone", vote: "vote", voting: "vote", gun: "arms", guns: "arms", speech: "speech", lawyer: "lawyer", attorney: "lawyer", silent: "silent", search: "search", searched: "search", school: "school", boss: "work", job: "work", work: "work" };
  function score(q) {
    var toks = q.toLowerCase().replace(/[^a-z0-9\s]/g, " ").split(/\s+/).filter(function (t) { return t.length > 1; });
    if (!toks.length) return [];
    toks = toks.map(function (t) { return SYN[t] || t; });
    var out = [];
    INDEX.forEach(function (it) {
      var t = it.t.toLowerCase(), s = (it.s || "").toLowerCase(), x = it.x || "", total = 0, all = true;
      toks.forEach(function (tok) {
        var sc = 0, stem = tok.length > 4 ? tok.replace(/(ing|ed|es|s)$/, "") : tok;
        if (t.indexOf(stem) > -1) sc += 8;
        if (s.indexOf(stem) > -1) sc += 3;
        if (x.indexOf(stem) > -1) sc += 1 + Math.min(3, x.split(stem).length - 2);
        if (!sc) all = false;
        total += sc;
      });
      if (all && total) {
        if (it.k === "Situation") total += 3;
        out.push([total, it]);
      }
    });
    out.sort(function (a, b) { return b[0] - a[0]; });
    return out.slice(0, 14).map(function (x) { return x[1]; });
  }
  function render(box, q) {
    if (!q.trim()) { showHints(box); return; }
    var res = score(q);
    if (!res.length) { box.innerHTML = '<p class="sr-empty">No matches for "' + esc(q) + '". Try a simpler word, like "police" or "vote".</p>'; return; }
    box.innerHTML = res.map(function (it) {
      return '<a class="sr" href="' + it.u + '"><svg class="ic" viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="3"/></svg><span><span class="sr-k">' + esc(it.k) + '</span><span class="sr-t">' + esc(it.t) + '</span><span class="sr-s">' + esc(it.s || "") + "</span></span></a>";
    }).join("");
  }
  $$("[data-search-input]").forEach(function (inp) {
    var box = inp.closest("dialog, section").querySelector("[data-search-results]");
    var run = function () { loadIndex().then(function () { render(box, inp.value); }); };
    inp.addEventListener("input", run);
    inp.addEventListener("keydown", function (e) {
      if (e.key === "Enter") { var first = box.querySelector(".sr:not([data-try])"); if (first) location.href = first.getAttribute("href"); }
    });
    box.addEventListener("click", function (e) {
      var a = e.target.closest("[data-try]");
      if (a) { e.preventDefault(); inp.value = a.getAttribute("data-try"); run(); inp.focus(); }
    });
    if (inp.hasAttribute("data-search-inline")) {
      var q = new URLSearchParams(location.search).get("q");
      if (q) { inp.value = q; run(); } else showHints(box);
    }
  });

  /* ---------- Show the original ---------- */
  function setOrig(c, on) {
    c.classList.toggle("show-orig", on);
    var b = c.parentNode.querySelector("[data-orig-toggle]");
    if (b) { b.setAttribute("aria-expanded", on ? "true" : "false"); b.querySelector("span").textContent = on ? "Hide the original" : "Show the original"; }
  }
  $$("[data-orig-toggle]").forEach(function (b) {
    b.hidden = false;
    b.addEventListener("click", function () {
      var c = b.parentNode.querySelector("[data-compare]");
      setOrig(c, !c.classList.contains("show-orig"));
    });
  });

  /* ---------- Quick check ---------- */
  $$(".qc").forEach(function (fs) {
    var ans = +fs.getAttribute("data-answer");
    $$(".qc-opt", fs).forEach(function (b) {
      b.addEventListener("click", function () {
        var i = +b.getAttribute("data-i");
        $$(".qc-opt", fs).forEach(function (o) {
          o.disabled = true;
          if (+o.getAttribute("data-i") === ans) o.classList.add("right");
        });
        if (i !== ans) b.classList.add("wrong");
        var why = $(".qc-why", fs);
        why.hidden = false;
        why.insertAdjacentHTML("afterbegin", "<strong>" + (i === ans ? "Right. " : "Not quite. ") + "</strong>");
      });
    });
  });

  /* ---------- Word definitions ---------- */
  var pop = $("#term-pop"), popFor = null;
  function hidePop() { if (pop) { pop.hidden = true; popFor = null; } }
  function showPop(a) {
    if (!pop) return;
    $(".term-def", pop).textContent = a.getAttribute("data-def");
    var more = $(".term-more", pop);
    more.href = a.getAttribute("href");
    pop.hidden = false;
    var r = a.getBoundingClientRect(), pw = pop.offsetWidth;
    var left = Math.max(12, Math.min(window.scrollX + r.left, window.scrollX + document.documentElement.clientWidth - pw - 12));
    pop.style.left = left + "px";
    pop.style.top = (window.scrollY + r.bottom + 8) + "px";
    popFor = a;
  }
  d.addEventListener("click", function (e) {
    var a = e.target.closest("a.term");
    if (a) { e.preventDefault(); if (popFor === a) hidePop(); else showPop(a); return; }
    if (pop && !pop.hidden && !e.target.closest("#term-pop")) hidePop();
    if (e.target.closest(".term-close")) hidePop();
  });

  /* ---------- Progress (this device only) ---------- */
  var prog = get("fc-progress", { read: {}, last: null });
  prog.read = prog.read || {};
  function markRead(url) {
    if (prog.read[url]) return;
    prog.read[url] = 1; put("fc-progress", prog); paintProgress();
  }
  function paintProgress() {
    $$("[data-progress-url]").forEach(function (el) { el.classList.toggle("is-read", !!prog.read[el.getAttribute("data-progress-url")]); });
    $$(".sec-progress a").forEach(function (a) { a.classList.toggle("is-read", !!prog.read[a.getAttribute("href")]); });
    var flag = $("[data-read-flag]"); if (flag) flag.hidden = !prog.read[PAGE];
    $$("[data-progress-count]").forEach(function (el) {
      var pre = el.getAttribute("data-prefix"), of = +el.getAttribute("data-of");
      var n = Object.keys(prog.read).filter(function (u) { return u.indexOf(pre) === 0 && u.split("/").length === 4; }).length;
      if (n) { el.hidden = false; el.textContent = "You've read " + n + " of " + of + "."; }
    });
    paintPathProgress();
  }
  var isDoc = !!$(".doc-head") && !d.body.classList.contains("is-home");
  if (isDoc) {
    prog.last = { u: PAGE, t: d.body.getAttribute("data-page-title") || d.title };
    put("fc-progress", prog);
    var end = $("#page-end");
    if (end && "IntersectionObserver" in window) {
      var seen = Date.now();
      var io = new IntersectionObserver(function (es) {
        es.forEach(function (en) { if (en.isIntersecting && Date.now() - seen > 4000) { markRead(PAGE); io.disconnect(); } });
      });
      setTimeout(function () { io.observe(end); }, 4000);
    }
  }
  var resume = $("#resume");
  if (resume && prog.last && prog.last.u && prog.last.u !== "/") {
    resume.hidden = false;
    resume.innerHTML = '<a class="resume-card" href="' + esc(prog.last.u) + '"><svg class="ic" viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg><span><small>Pick up where you left off</small><strong>' + esc(prog.last.t) + "</strong></span></a>";
  }

  /* ---------- Paths ---------- */
  var PATHS = null;
  function loadPaths() {
    if (PATHS) return Promise.resolve(PATHS);
    return fetch("/paths.json").then(function (r) { return r.json(); }).then(function (j) { PATHS = j; return j; });
  }
  function paintPathProgress() {
    var cards = $$("[data-path-card]"), done = $("[data-path-done]");
    if (!cards.length && !done) return;
    loadPaths().then(function (P) {
      cards.forEach(function (c) {
        var p = P[c.getAttribute("data-path-card")]; if (!p) return;
        var n = p.s.filter(function (s) { return prog.read[s.h]; }).length;
        var el = $("[data-path-prog]", c); if (el) el.textContent = n ? " · " + n + " of " + p.s.length + " done" : "";
      });
      if (done) {
        var slug = PAGE.split("/")[2], p = P[slug];
        if (p) done.hidden = !p.s.every(function (s) { return prog.read[s.h]; });
      }
    });
  }
  var params = new URLSearchParams(location.search);
  if (params.get("path")) {
    try { sessionStorage.setItem("fc-path", params.get("path")); } catch (e) {}
    params.delete("path");
    var qs = params.toString();
    history.replaceState(null, "", location.pathname + (qs ? "?" + qs : "") + location.hash);
  }
  var curPath = null; try { curPath = sessionStorage.getItem("fc-path"); } catch (e) {}
  if (curPath) {
    loadPaths().then(function (P) {
      var p = P[curPath]; if (!p) return;
      var i = -1; p.s.forEach(function (s, j) { if (s.h === PAGE) i = j; });
      if (i < 0) return;
      var bar = $("#path-bar"), next = p.s[i + 1];
      var nextHtml = next ? '<a href="' + next.h + '">Next: ' + esc(next.l) + ' <svg class="ic" viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg></a>'
                          : '<a href="/paths/' + curPath + '/">Finish the path</a>';
      bar.innerHTML = '<div class="path-bar-in"><span class="pb-text"><small>Step ' + (i + 1) + " of " + p.s.length + "</small>" + esc(p.t) + "</span>" + nextHtml +
        '<button type="button" class="pb-x" aria-label="Leave this path"><svg class="ic" viewBox="0 0 24 24" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18"/></svg></button></div>';
      bar.hidden = false; d.body.classList.add("has-path-bar");
      $(".pb-x", bar).addEventListener("click", function () {
        try { sessionStorage.removeItem("fc-path"); } catch (e) {}
        bar.hidden = true; d.body.classList.remove("has-path-bar");
      });
      if (next) $("a", bar).addEventListener("click", function () { markRead(PAGE); });
    });
  }
  paintProgress();

  /* ---------- Situation cards ---------- */
  var screen = $("[data-screen-mode]");
  function closeScreen() { if (screen && !screen.hidden) { screen.hidden = true; html.style.overflow = ""; } }
  $$("[data-show-screen]").forEach(function (b) {
    b.addEventListener("click", function () {
      screen.hidden = false; html.style.overflow = "hidden";
      $("[data-screen-close]", screen).focus();
      if (screen.requestFullscreen) screen.requestFullscreen().catch(function () {});
    });
  });
  if (screen) $("[data-screen-close]", screen).addEventListener("click", function () {
    if (d.fullscreenElement) d.exitFullscreen().catch(function () {});
    closeScreen();
  });
  $$("[data-save-offline]").forEach(function (b) {
    var st = $("[data-save-status]");
    if (!("serviceWorker" in navigator) || !window.caches) { b.hidden = true; return; }
    b.addEventListener("click", function () {
      navigator.serviceWorker.ready.then(function () {
        return caches.keys().then(function (ks) {
          var name = ks.filter(function (k) { return k.indexOf("fc-") === 0; })[0] || "fc-saved";
          return caches.open(name).then(function (c) { return c.add(location.pathname); });
        });
      }).then(function () {
        st.hidden = false; st.textContent = "Saved. This card will open on this phone even without internet.";
      }).catch(function () {
        st.hidden = false; st.textContent = "Couldn't save right now. Try again with a connection.";
      });
    });
  });
  $$("[data-print-wallet]").forEach(function (b) {
    b.addEventListener("click", function () {
      d.body.classList.add("print-wallet");
      window.print();
      setTimeout(function () { d.body.classList.remove("print-wallet"); }, 500);
    });
  });

  /* ---------- Memorize ---------- */
  var memData = $("#mem-data");
  if (memData) {
    var MEM = {}; JSON.parse(memData.textContent).forEach(function (m) { MEM[m.slug] = m; });
    $$("[data-mem]").forEach(function (box) {
      var m = MEM[box.getAttribute("data-mem")], stage = $("[data-stage]", box);
      function mode(name) {
        $$(".seg-btn", box).forEach(function (b) { var on = b.getAttribute("data-mode") === name; b.classList.toggle("on", on); b.setAttribute("aria-selected", on); });
        if (name === "read") stage.innerHTML = "<p>" + esc(m.chunks.join(" ")) + "</p>";
        if (name === "letters") {
          var words = m.chunks.join(" ").split(/\s+/);
          stage.innerHTML = '<p class="hint">Say each word. Tap a letter to check it.</p><p>' + words.map(function (w) {
            var first = w.match(/[A-Za-z]/); var lead = first ? w.slice(0, w.indexOf(first[0]) + 1) : w;
            return '<button type="button" class="fl" data-w="' + esc(w) + '">' + esc(lead) + "</button>";
          }).join(" ") + '</p><p><button type="button" class="seg-btn" data-reveal>Show all</button></p>';
          $$(".fl", stage).forEach(function (b) { b.addEventListener("click", function () { b.textContent = b.getAttribute("data-w"); b.classList.add("shown"); }); });
          $("[data-reveal]", stage).addEventListener("click", function () { $$(".fl", stage).forEach(function (b) { b.textContent = b.getAttribute("data-w"); b.classList.add("shown"); }); });
        }
        if (name === "order") {
          var idx = m.chunks.map(function (_, i) { return i; });
          for (var i = idx.length - 1; i > 0; i--) { var j = Math.floor(Math.random() * (i + 1)); var t = idx[i]; idx[i] = idx[j]; idx[j] = t; }
          if (idx.every(function (v, i) { return v === i; }) && idx.length > 1) idx.reverse();
          var want = 0;
          stage.innerHTML = '<p class="hint">Tap the pieces in the right order.</p><div class="mem-built" aria-live="polite"></div><div class="mem-chips">' +
            idx.map(function (i) { return '<button type="button" class="mem-chip" data-i="' + i + '">' + esc(m.chunks[i]) + "</button>"; }).join("") + "</div>";
          var built = $(".mem-built", stage);
          $$(".mem-chip", stage).forEach(function (c) {
            c.addEventListener("click", function () {
              if (+c.getAttribute("data-i") === want) {
                built.insertAdjacentHTML("beforeend", "<span>" + esc(m.chunks[want]) + "</span> ");
                c.remove(); want++;
                if (want === m.chunks.length) built.insertAdjacentHTML("afterend", '<p class="mem-done">You got it in order.</p>');
              } else { c.classList.remove("bad"); void c.offsetWidth; c.classList.add("bad"); }
            });
          });
        }
      }
      $$(".seg-btn", box).forEach(function (b) { b.addEventListener("click", function () { mode(b.getAttribute("data-mode")); }); });
    });
  }

  /* ---------- Timeline filter ---------- */
  $$('input[name="tlk"]').forEach(function (r) {
    r.addEventListener("change", function () {
      var v = r.value;
      $$(".tl-item").forEach(function (li) { li.hidden = v !== "all" && li.getAttribute("data-kind") !== v; });
      $$(".tl-era").forEach(function (s) { s.hidden = !$$(".tl-item", s).some(function (li) { return !li.hidden; }); });
    });
  });

  /* ---------- Nav state, back to top ---------- */
  $$(".mobile-nav a, .site-nav a").forEach(function (a) {
    var h = a.getAttribute("href");
    if ((h === "/" && PAGE === "/") || (h !== "/" && PAGE.indexOf(h) === 0)) { a.classList.add("on"); a.setAttribute("aria-current", "page"); }
  });
  var btt = $(".back-to-top");
  if (btt) {
    var tick = false;
    window.addEventListener("scroll", function () {
      if (tick) return; tick = true;
      requestAnimationFrame(function () { btt.classList.toggle("visible", window.scrollY > 700); tick = false; });
    }, { passive: true });
    btt.addEventListener("click", function () { window.scrollTo({ top: 0 }); $("#main").focus({ preventScroll: true }); });
  }

  /* ---------- Offline support ---------- */
  if ("serviceWorker" in navigator && location.protocol === "https:") {
    window.addEventListener("load", function () { navigator.serviceWorker.register("/sw.js").catch(function () {}); });
  }
})();
