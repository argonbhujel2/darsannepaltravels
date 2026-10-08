/* Multi-step enquiry form */
(function () {
  'use strict';

  const form = document.getElementById('enquiry-form');
  if (!form) return;

  const steps = form.querySelectorAll('.enquiry-step');
  const progress = document.getElementById('enquiry-progress');
  let current = 0;

  function showStep(n) {
    steps.forEach((s, i) => {
      s.style.display = i === n ? 'block' : 'none';
    });
    current = n;
    if (progress) {
      const pct = ((n + 1) / steps.length) * 100;
      progress.style.width = pct + '%';
      progress.setAttribute('aria-valuenow', n + 1);
    }
    // Update step indicators
    document.querySelectorAll('.step-indicator').forEach((el, i) => {
      el.classList.toggle('active', i <= n);
      el.classList.toggle('current', i === n);
    });
  }

  function validateStep(n) {
    const step = steps[n];
    if (!step) return true;
    const required = step.querySelectorAll('[required]');
    let ok = true;
    required.forEach(field => {
      if (!field.value.trim()) {
        field.classList.add('error');
        ok = false;
      } else {
        field.classList.remove('error');
      }
    });
    return ok;
  }

  form.querySelectorAll('[data-next]').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      if (validateStep(current) && current < steps.length - 1) {
        showStep(current + 1);
        window.scrollTo({ top: form.offsetTop - 80, behavior: 'smooth' });
      }
    });
  });

  form.querySelectorAll('[data-prev]').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      if (current > 0) {
        showStep(current - 1);
        window.scrollTo({ top: form.offsetTop - 80, behavior: 'smooth' });
      }
    });
  });

  form.addEventListener('submit', function () {
    const btn = form.querySelector('[type="submit"]');
    if (btn) {
      btn.disabled = true;
      btn.textContent = 'Submitting...';
    }
  });

  showStep(0);
})();
