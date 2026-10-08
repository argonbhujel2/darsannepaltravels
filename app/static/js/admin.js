/* Admin panel JS */
(function () {
  'use strict';

  // Password show/hide
  document.querySelectorAll('[data-toggle-password]').forEach(btn => {
    btn.addEventListener('click', () => {
      const input = document.getElementById(btn.dataset.togglePassword);
      if (!input) return;
      const isPass = input.type === 'password';
      input.type = isPass ? 'text' : 'password';
      btn.textContent = isPass ? 'Hide' : 'Show';
    });
  });

  // Confirm delete
  document.querySelectorAll('[data-confirm]').forEach(el => {
    el.addEventListener('click', (e) => {
      if (!confirm(el.dataset.confirm || 'Are you sure?')) {
        e.preventDefault();
      }
    });
  });

  // Admin sidebar toggle
  const toggle = document.getElementById('admin-sidebar-toggle');
  const sidebar = document.querySelector('.admin-sidebar');
  if (toggle && sidebar) {
    toggle.addEventListener('click', () => sidebar.classList.toggle('open'));
  }

  // Auto-slug from title
  const titleInput = document.getElementById('title');
  const slugInput = document.getElementById('slug');
  if (titleInput && slugInput && !slugInput.value) {
    titleInput.addEventListener('input', () => {
      if (slugInput.dataset.manual) return;
      slugInput.value = titleInput.value
        .toLowerCase()
        .replace(/[^\w\s-]/g, '')
        .replace(/[\s_]+/g, '-')
        .replace(/-+/g, '-')
        .trim();
    });
    slugInput.addEventListener('input', () => { slugInput.dataset.manual = '1'; });
  }
})();
