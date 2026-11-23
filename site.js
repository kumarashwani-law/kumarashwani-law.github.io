// Site-wide reader features: dark mode, text size, copy-citation, share, email/RSS follow panel, glossary pop-ups.
// Loaded in <head> (not deferred) so the saved theme and text size apply before the page paints.
(function () {
  var root = document.documentElement;
  var me = document.currentScript && document.currentScript.src;
  var base = me ? me.replace(/site\.js(\?.*)?$/, '') : '/';
  function get(k) { try { return localStorage.getItem(k); } catch (e) { return null; } }
  function set(k, v) { try { localStorage.setItem(k, v); } catch (e) {} }

  // ---- Theme (light / dark), defaulting to the device setting
  var theme = get('ak-theme');
  if (!theme) {
    try { theme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'; }
    catch (e) { theme = 'light'; }
  }
  root.setAttribute('data-theme', theme);

  // ---- Text size (normal / large / larger)
  var SIZES = ['m', 'l', 'xl'];
  var size = get('ak-text');
  if (SIZES.indexOf(size) < 0) size = 'm';
  root.setAttribute('data-text', size);

  function ready(fn) {
    if (document.readyState !== 'loading') fn(); else document.addEventListener('DOMContentLoaded', fn);
  }

  ready(function () {
    // ---- Reader controls in the header
    var bar = document.querySelector('.site-header .wrap');
    if (bar && !bar.querySelector('.reader-tools')) {
      var tools = document.createElement('div');
      tools.className = 'reader-tools';
      tools.innerHTML =
        '<a class="tool-btn" id="site-search" href="' + base + 'search.html" aria-label="Search the site">' +
        '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="M20 20l-4-4"/></svg></a>' +
        '<button type="button" class="tool-btn" id="text-size" aria-label="Change text size">' +
        '<span aria-hidden="true">A</span><span aria-hidden="true" class="big">A</span></button>' +
        '<button type="button" class="tool-btn" id="theme-toggle"></button>';
      bar.appendChild(tools);
      var tbtn = document.getElementById('theme-toggle');
      var sbtn = document.getElementById('text-size');
      function paintTheme() {
        var dark = root.getAttribute('data-theme') === 'dark';
        tbtn.textContent = dark ? '☀' : '☾';
        tbtn.setAttribute('aria-label', dark ? 'Switch to light mode' : 'Switch to dark mode');
        tbtn.setAttribute('title', dark ? 'Light mode' : 'Dark mode');
      }
      function paintSize() {
        var s = root.getAttribute('data-text');
        var name = { m: 'normal', l: 'large', xl: 'larger' }[s];
        sbtn.setAttribute('title', 'Text size: ' + name);
        sbtn.setAttribute('aria-label', 'Text size is ' + name + '. Change text size');
      }
      paintTheme(); paintSize();
      tbtn.addEventListener('click', function () {
        var next = root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
        root.setAttribute('data-theme', next); set('ak-theme', next); paintTheme();
      });
      sbtn.addEventListener('click', function () {
        var i = SIZES.indexOf(root.getAttribute('data-text'));
        var next = SIZES[(i + 1) % SIZES.length];
        root.setAttribute('data-text', next); set('ak-text', next); paintSize();
      });
    }

    // ---- Copy helpers (citation, feed address)
    function copy(text, btn, done) {
      var label = btn.textContent;
      function ok() { btn.textContent = done; setTimeout(function () { btn.textContent = label; }, 2000); }
      try {
        navigator.clipboard.writeText(text).then(ok, function () { fallback(); });
      } catch (e) { fallback(); }
      function fallback() {
        var ta = document.createElement('textarea');
        ta.value = text; ta.setAttribute('readonly', ''); ta.style.position = 'absolute'; ta.style.left = '-9999px';
        document.body.appendChild(ta); ta.select();
        try { document.execCommand('copy'); ok(); } catch (e2) { btn.textContent = 'Copy failed'; }
        ta.remove();
      }
    }
    document.querySelectorAll('[data-copy]').forEach(function (b) {
      b.addEventListener('click', function () { copy(b.getAttribute('data-copy'), b, b.getAttribute('data-done') || 'Copied'); });
    });

    // ---- Cite this: toggle the citation box
    document.querySelectorAll('.cite-toggle').forEach(function (b) {
      var box = document.getElementById(b.getAttribute('aria-controls'));
      if (!box) return;
      b.addEventListener('click', function () {
        var open = b.getAttribute('aria-expanded') === 'true';
        b.setAttribute('aria-expanded', open ? 'false' : 'true');
        box.hidden = open;
      });
    });

    // ---- Follow panels (email / RSS)
    document.querySelectorAll('.follow-toggle').forEach(function (b) {
      var box = document.getElementById(b.getAttribute('aria-controls'));
      if (!box) return;
      b.addEventListener('click', function () {
        var open = b.getAttribute('aria-expanded') === 'true';
        b.setAttribute('aria-expanded', open ? 'false' : 'true');
        box.hidden = open;
      });
    });

    // ---- Print / save as PDF
    document.querySelectorAll('.print-btn').forEach(function (b) {
      b.addEventListener('click', function () { window.print(); });
    });

    // ---- Glossary pop-ups: tap to toggle on touch screens, Escape to close
    var openTerm = null;
    document.querySelectorAll('.gloss').forEach(function (t) {
      t.addEventListener('click', function (e) {
        e.preventDefault();
        if (openTerm && openTerm !== t) openTerm.classList.remove('open');
        t.classList.toggle('open');
        openTerm = t.classList.contains('open') ? t : null;
      });
      t.addEventListener('keydown', function (e) {
        if (e.key === 'Escape') { t.classList.remove('open'); t.blur(); }
        if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); t.click(); }
      });
    });
    document.addEventListener('click', function (e) {
      if (openTerm && !openTerm.contains(e.target)) { openTerm.classList.remove('open'); openTerm = null; }
    });
  });
})();
