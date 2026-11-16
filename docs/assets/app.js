/* =========================================================
   磐石 AI4S · 页面交互
   主题切换 / 导航 / 课程筛选 / 进度动画 / 滚动显现
   ========================================================= */
(function () {
  'use strict';

  var root = document.documentElement;
  var THEME_KEY = 'ai4s-theme';
  var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ---------- 主题 ---------- */

  function syncThemeUI(theme) {
    var meta = document.querySelector('meta[name="theme-color"]');
    if (meta) meta.setAttribute('content', theme === 'dark' ? '#17130f' : '#f6f1e7');

    document.querySelectorAll('[data-theme-toggle]').forEach(function (btn) {
      var label = theme === 'dark' ? '切换到浅色主题' : '切换到深色主题';
      btn.setAttribute('aria-label', label);
      btn.setAttribute('title', label);
    });
  }

  document.querySelectorAll('[data-theme-toggle]').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var next = root.dataset.theme === 'dark' ? 'light' : 'dark';
      root.dataset.theme = next;
      try { localStorage.setItem(THEME_KEY, next); } catch (e) { /* 忽略隐私模式限制 */ }
      syncThemeUI(next);
    });
  });
  syncThemeUI(root.dataset.theme === 'light' ? 'light' : 'dark');

  /* 系统主题变化时，仅在用户未手动选择过的情况下跟随 */
  var mq = window.matchMedia('(prefers-color-scheme: light)');
  var onSchemeChange = function (event) {
    var saved = null;
    try { saved = localStorage.getItem(THEME_KEY); } catch (e) { /* noop */ }
    if (saved) return;
    var theme = event.matches ? 'light' : 'dark';
    root.dataset.theme = theme;
    syncThemeUI(theme);
  };
  if (typeof mq.addEventListener === 'function') mq.addEventListener('change', onSchemeChange);

  /* ---------- 导航 ---------- */

  var nav = document.querySelector('.nav');
  var menuBtn = document.querySelector('[data-menu-toggle]');
  var toTop = document.querySelector('[data-to-top]');
  var navLinks = Array.prototype.slice.call(document.querySelectorAll('.nav-links a[href^="#"]'));
  var menuLinks = Array.prototype.slice.call(document.querySelectorAll('.nav-links a'));
  var sections = ['path', 'lectures', 'progress', 'notes', 'resources']
    .map(function (id) { return document.getElementById(id); })
    .filter(Boolean);

  function closeMenu() {
    if (!nav || !nav.classList.contains('is-open')) return;
    nav.classList.remove('is-open');
    if (menuBtn) {
      menuBtn.setAttribute('aria-expanded', 'false');
      menuBtn.setAttribute('aria-label', '打开导航菜单');
    }
  }

  if (menuBtn && nav) {
    menuBtn.addEventListener('click', function () {
      var open = nav.classList.toggle('is-open');
      menuBtn.setAttribute('aria-expanded', open ? 'true' : 'false');
      menuBtn.setAttribute('aria-label', open ? '关闭导航菜单' : '打开导航菜单');
    });
    menuLinks.forEach(function (a) { a.addEventListener('click', closeMenu); });
    document.addEventListener('keydown', function (event) {
      if (event.key === 'Escape') closeMenu();
    });
    document.addEventListener('click', function (event) {
      if (!nav.contains(event.target)) closeMenu();
    });
    window.addEventListener('resize', function () {
      if (window.innerWidth > 880) closeMenu();
    });
  }

  function updateActive() {
    if (!sections.length) return;
    var y = window.scrollY + 130;
    var current = null;
    sections.forEach(function (section) {
      if (section.offsetTop <= y) current = section.id;
    });
    navLinks.forEach(function (a) {
      var isActive = a.getAttribute('href') === '#' + current;
      a.classList.toggle('active', isActive);
      if (isActive) a.setAttribute('aria-current', 'location');
      else a.removeAttribute('aria-current');
    });
  }

  var ticking = false;
  function onScroll() {
    if (ticking) return;
    ticking = true;
    window.requestAnimationFrame(function () {
      ticking = false;
      var y = window.scrollY;
      if (nav) nav.classList.toggle('is-scrolled', y > 8);
      if (toTop) toTop.classList.toggle('is-visible', y > 640);
      updateActive();
    });
  }
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  if (toTop) {
    toTop.addEventListener('click', function () {
      window.scrollTo({ top: 0, behavior: reduceMotion ? 'auto' : 'smooth' });
    });
  }

  /* ---------- 课程筛选 ---------- */

  var chips = Array.prototype.slice.call(document.querySelectorAll('[data-filter]'));
  var cards = Array.prototype.slice.call(document.querySelectorAll('.lec'));
  var countEl = document.querySelector('[data-result-count]');

  function applyFilter(filter) {
    chips.forEach(function (chip) {
      chip.setAttribute('aria-pressed', chip.dataset.filter === filter ? 'true' : 'false');
    });
    var visible = 0;
    cards.forEach(function (card) {
      var show = filter === 'all' || card.dataset.track === filter;
      card.hidden = !show;
      if (show) visible += 1;
    });
    if (countEl) {
      countEl.textContent = filter === 'all' ? '共 ' + visible + ' 讲' : visible + ' 讲';
    }
  }

  chips.forEach(function (chip) {
    chip.addEventListener('click', function () {
      applyFilter(chip.dataset.filter);
    });
  });

  document.querySelectorAll('[data-jump-filter]').forEach(function (link) {
    link.addEventListener('click', function () {
      applyFilter(link.dataset.jumpFilter);
    });
  });

  /* ---------- 进度动画 ---------- */

  var ring = document.querySelector('[data-ring]');
  var fills = Array.prototype.slice.call(document.querySelectorAll('[data-fill]'));

  function drawRing() {
    if (!ring) return;
    var pct = Math.max(0, Math.min(100, parseFloat(ring.dataset.ring) || 0));
    var circumference = 2 * Math.PI * 78;
    ring.style.strokeDasharray = circumference;
    ring.style.strokeDashoffset = circumference * (1 - pct / 100);
  }

  if (ring && 'IntersectionObserver' in window && !reduceMotion) {
    var ringObserver = new IntersectionObserver(function (entries) {
      if (entries.some(function (entry) { return entry.isIntersecting; })) {
        drawRing();
        ringObserver.disconnect();
      }
    }, { threshold: 0.35 });
    ringObserver.observe(ring);
  } else {
    drawRing();
  }

  if ('IntersectionObserver' in window && !reduceMotion) {
    var fillObserver = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        var el = entry.target;
        el.style.width = (parseFloat(el.dataset.fill) || 0) + '%';
        fillObserver.unobserve(el);
      });
    }, { threshold: 0.4 });
    fills.forEach(function (el) { fillObserver.observe(el); });
  } else {
    fills.forEach(function (el) { el.style.width = (parseFloat(el.dataset.fill) || 0) + '%'; });
  }

  /* ---------- 滚动显现 ---------- */

  var reveals = Array.prototype.slice.call(document.querySelectorAll('[data-reveal]'));

  function showAllReveals() {
    root.classList.remove('reveal-on');
    reveals.forEach(function (el) { el.classList.add('in'); });
  }

  if ('IntersectionObserver' in window && !reduceMotion) {
    try {
      root.classList.add('reveal-on');

      reveals.forEach(function (el) {
        var siblings = Array.prototype.slice.call(el.parentNode.querySelectorAll(':scope > [data-reveal]'));
        var index = siblings.indexOf(el);
        if (index > 0) el.style.transitionDelay = Math.min(index * 55, 220) + 'ms';
      });

      var revealObserver = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
          if (!entry.isIntersecting) return;
          entry.target.classList.add('in');
          revealObserver.unobserve(entry.target);
        });
      }, { rootMargin: '0px 0px -6% 0px', threshold: 0.06 });

      reveals.forEach(function (el) { revealObserver.observe(el); });
    } catch (err) {
      showAllReveals();
    }
  } else {
    showAllReveals();
  }
})();
