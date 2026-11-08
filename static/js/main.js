/* LearnMate AI – main.js */

'use strict';

// ── Sidebar toggle (mobile) ──────────────────────────────────────
(function () {
  const sidebar = document.getElementById('sidebar');
  const toggleBtn = document.getElementById('sidebarToggle');
  if (!sidebar || !toggleBtn) return;

  // Create overlay dynamically
  const overlay = document.createElement('div');
  overlay.className = 'lm-sidebar-overlay';
  document.body.appendChild(overlay);

  function openSidebar() {
    sidebar.classList.add('open');
    overlay.classList.add('open');
    document.body.style.overflow = 'hidden';
  }

  function closeSidebar() {
    sidebar.classList.remove('open');
    overlay.classList.remove('open');
    document.body.style.overflow = '';
  }

  toggleBtn.addEventListener('click', openSidebar);
  overlay.addEventListener('click', closeSidebar);
})();


// ── Auto-dismiss flash alerts ────────────────────────────────────
(function () {
  document.querySelectorAll('.lm-alert').forEach(function (el) {
    setTimeout(function () {
      const bsAlert = bootstrap.Alert.getOrCreateInstance(el);
      if (bsAlert) bsAlert.close();
    }, 5000);
  });
})();


// ── Onboarding: radio goal deduplication ─────────────────────────
// When a preset radio is selected, clear the custom text input and vice versa
(function () {
  const radios = document.querySelectorAll('input[name="career_goal"][type="radio"]');
  const textInput = document.querySelector('input[name="career_goal"][type="text"]');
  if (!radios.length || !textInput) return;

  radios.forEach(function (r) {
    r.addEventListener('change', function () {
      textInput.value = '';
    });
  });

  textInput.addEventListener('input', function () {
    radios.forEach(function (r) { r.checked = false; });
  });
})();


// ── Active nav highlight helper ───────────────────────────────────
(function () {
  const path = window.location.pathname;
  document.querySelectorAll('.lm-nav-link').forEach(function (link) {
    if (link.getAttribute('href') === path) {
      link.classList.add('active');
    }
  });
})();
