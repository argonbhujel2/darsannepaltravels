/* Darshan Nepal Travel — Main JS */
(function () {
  'use strict';

  // Navbar scroll
  const navbar = document.getElementById('navbar');
  if (navbar) {
    const onScroll = () => {
      if (window.scrollY > 60) {
        navbar.classList.add('scrolled');
        navbar.classList.remove('transparent');
      } else {
        navbar.classList.add('transparent');
        navbar.classList.remove('scrolled');
      }
    };
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
  }

  // Mobile menu
  const hamburger = document.getElementById('hamburger');
  const mobileNav = document.getElementById('mobile-nav');
  const overlay = document.getElementById('mobile-nav-overlay');

  function closeMobile() {
    if (hamburger) hamburger.classList.remove('open');
    if (mobileNav) mobileNav.classList.remove('open');
    if (overlay) overlay.classList.remove('open');
    document.body.style.overflow = '';
  }

  if (hamburger && mobileNav) {
    hamburger.addEventListener('click', () => {
      const open = mobileNav.classList.toggle('open');
      hamburger.classList.toggle('open', open);
      if (overlay) overlay.classList.toggle('open', open);
      document.body.style.overflow = open ? 'hidden' : '';
    });
    if (overlay) overlay.addEventListener('click', closeMobile);
    mobileNav.querySelectorAll('a').forEach(a => a.addEventListener('click', closeMobile));
  }

  // Scroll reveal (all variants)
  const reveals = document.querySelectorAll('.reveal, .reveal-left, .reveal-right, .reveal-scale');
  if (reveals.length && 'IntersectionObserver' in window) {
    const io = new IntersectionObserver((entries) => {
      entries.forEach(e => {
        if (e.isIntersecting) {
          e.target.classList.add('visible');
          io.unobserve(e.target);
        }
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });
    reveals.forEach(el => io.observe(el));
  } else {
    reveals.forEach(el => el.classList.add('visible'));
  }

  // Smart search
  const searchForm = document.getElementById('smart-search-form');
  if (searchForm) {
    searchForm.addEventListener('submit', function (e) {
      const dest = document.getElementById('search-destination');
      const type = document.getElementById('search-type');
      const params = new URLSearchParams();
      if (dest && dest.value) params.set('destination', dest.value);
      if (type && type.value) params.set('type', type.value);
      const date = document.getElementById('search-date');
      if (date && date.value) params.set('date', date.value);
      const guests = document.getElementById('search-guests');
      if (guests && guests.value) params.set('guests', guests.value);
      window.location.href = '/packages/?' + params.toString();
      e.preventDefault();
    });
  }

  // Accordion
  document.querySelectorAll('[data-accordion]').forEach(btn => {
    btn.addEventListener('click', () => {
      const panel = btn.nextElementSibling;
      if (!panel) return;
      const open = panel.classList.toggle('open');
      btn.setAttribute('aria-expanded', open);
      panel.style.maxHeight = open ? panel.scrollHeight + 'px' : '0';
    });
  });

  // Parallax-lite on hero (reduced motion safe)
  const heroBg = document.querySelector('.hero-bg');
  if (heroBg && !window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    window.addEventListener('scroll', () => {
      const y = window.scrollY;
      if (y < window.innerHeight) {
        heroBg.style.transform = 'translateY(' + (y * 0.25) + 'px) scale(1.05)';
      }
    }, { passive: true });
  }
})();
