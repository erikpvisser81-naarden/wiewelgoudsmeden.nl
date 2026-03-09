/* Wiewel Goudsmeden — Analytics + Cookie Consent v1.1 (Lighthouse optimized) */
(function() {
  'use strict';

  var GA_ID = 'G-XXXXXXXXXX'; // TODO: fill in GA4 Measurement ID
  var STORAGE_KEY = 'wg_cookie_consent';

  // --- Cookie Consent ---
  function getConsent() { try { return localStorage.getItem(STORAGE_KEY); } catch(e) { return null; } }

  function showBanner() {
    var b = document.getElementById('cookieBanner');
    if (b) b.classList.add('visible');
  }

  function hideBanner() {
    var b = document.getElementById('cookieBanner');
    if (b) b.classList.remove('visible');
  }

  function acceptCookies() {
    try { localStorage.setItem(STORAGE_KEY, 'accepted'); } catch(e) {}
    hideBanner();
    loadGA4();
    wgTrack('consent_accepted');
  }

  function declineCookies() {
    try { localStorage.setItem(STORAGE_KEY, 'declined'); } catch(e) {}
    hideBanner();
  }

  // Expose to buttons
  window.acceptCookies = acceptCookies;
  window.declineCookies = declineCookies;

  // --- GA4 Loading ---
  var ga4Loaded = false;
  var eventQueue = [];

  function loadGA4() {
    if (ga4Loaded || GA_ID === 'G-XXXXXXXXXX') return;
    ga4Loaded = true;
    var s = document.createElement('script');
    s.src = 'https://www.googletagmanager.com/gtag/js?id=' + GA_ID;
    s.async = true;
    document.head.appendChild(s);
    window.dataLayer = window.dataLayer || [];
    function gtag() { window.dataLayer.push(arguments); }
    window.gtag = gtag;
    gtag('js', new Date());
    gtag('config', GA_ID, { anonymize_ip: true });
    // Flush queued events
    eventQueue.forEach(function(e) { gtag('event', e.name, e.params); });
    eventQueue = [];
  }

  // --- Public tracking API ---
  function wgTrack(eventName, params) {
    params = params || {};
    if (ga4Loaded && window.gtag) {
      window.gtag('event', eventName, params);
    } else {
      eventQueue.push({ name: eventName, params: params });
    }
  }
  window.wgTrack = wgTrack;

  // --- Smart header (hide on scroll down, show on scroll up) ---
  function initSmartHeader() {
    var header = document.querySelector('.header');
    if (!header) return;
    var catNav = document.querySelector('.cat-nav-wrap');
    var lastY = 0;
    window.addEventListener('scroll', function() {
      var y = window.scrollY;
      if (y < 60) { header.classList.remove('header-hidden'); }
      else if (y > lastY + 10) { header.classList.add('header-hidden'); }
      else if (y < lastY - 10) { header.classList.remove('header-hidden'); }
      lastY = y;
      if (catNav) {
        catNav.classList.toggle('nav-top-0', header.classList.contains('header-hidden'));
      }
    }, { passive: true });
  }

  // --- FAQ toggle ---
  function initFAQ() {
    document.querySelectorAll('.faq-item__q').forEach(function(btn) {
      btn.addEventListener('click', function() {
        var expanded = btn.getAttribute('aria-expanded') === 'true';
        btn.setAttribute('aria-expanded', !expanded);
        var answer = btn.nextElementSibling;
        if (!expanded) {
          answer.style.maxHeight = answer.scrollHeight + 'px';
          wgTrack('faq_expand', { question: btn.textContent.trim().substring(0, 60) });
        } else {
          answer.style.maxHeight = '0';
        }
      });
    });
  }

  // --- Mobile menu ---
  function initMobileMenu() {
    var burger = document.querySelector('.header__burger');
    var nav = document.querySelector('.mobile-nav');
    if (!burger || !nav) return;
    function closeMenu() {
      nav.classList.remove('open');
      burger.classList.remove('is-open');
      burger.setAttribute('aria-expanded', 'false');
      document.body.style.overflow = '';
    }
    burger.addEventListener('click', function() {
      var isOpen = nav.classList.toggle('open');
      burger.classList.toggle('is-open', isOpen);
      burger.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
      document.body.style.overflow = isOpen ? 'hidden' : '';
    });
    nav.querySelectorAll('a').forEach(function(a) {
      a.addEventListener('click', closeMenu);
    });
  }

  // --- Init ---
  function initCritical() {
    var consent = getConsent();
    if (!consent) { showBanner(); }
    else if (consent === 'accepted') { loadGA4(); }
    initSmartHeader();
    initMobileMenu();
  }

  function initDeferred() {
    initFAQ();
  }

  function scheduleDeferred(fn) {
    if ('requestIdleCallback' in window) {
      requestIdleCallback(fn);
    } else {
      setTimeout(fn, 200);
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function() {
      initCritical();
      scheduleDeferred(initDeferred);
    });
  } else {
    initCritical();
    scheduleDeferred(initDeferred);
  }
})();
