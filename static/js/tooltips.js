/* One lifecycle for every chart: mouse hover, touch tap, keyboard and dismissal. */
(function () {
  'use strict';
  var tip, content, active = null, dismissed = null, leaveTimer;
  var pointer = { x: -1, y: -1 }, dismissedAt = null, restoringFocus = false;
  function init() {
    if (tip) return true;
    tip = document.getElementById('tip');
    if (!tip) return false;
    content = tip.querySelector('.tip-content');
    tip.querySelector('.tip-close').addEventListener('click', function () { hide(true); });
    tip.addEventListener('pointerenter', function () { clearTimeout(leaveTimer); });
    tip.addEventListener('pointerleave', leave);
    return true;
  }
  function hide(suppress) {
    clearTimeout(leaveTimer);
    if (!active) return;
    var previous = active;
    active = null;
    if (suppress) { dismissed = previous.el; dismissedAt = { x: pointer.x, y: pointer.y }; }
    tip.classList.remove('on');
    tip.setAttribute('aria-hidden', 'true');
    previous.el.removeAttribute('aria-describedby');
    if (previous.cleanup) previous.cleanup();
    if (tip.contains(document.activeElement)) {
      restoringFocus = true;
      previous.el.focus({ preventScroll: true });
      restoringFocus = false;
    }
  }
  function leave() { clearTimeout(leaveTimer); leaveTimer = setTimeout(function () { hide(false); }, 140); }
  function show(binding, ev) {
    if (!init()) return;
    clearTimeout(leaveTimer);
    if (active && active !== binding) hide(false);
    active = binding;
    var html = binding.render(ev);
    if (content.innerHTML !== html) content.innerHTML = html;
    tip.setAttribute('aria-hidden', 'false');
    tip.classList.add('on');
    binding.el.setAttribute('aria-describedby', 'tip-content');
    var r = tip.getBoundingClientRect(), x = ev.clientX + 14, y = ev.clientY + 14;
    if (x + r.width > innerWidth - 8) x = ev.clientX - r.width - 14;
    if (y + r.height > innerHeight - 8) y = ev.clientY - r.height - 14;
    tip.style.left = Math.max(8, Math.min(x, innerWidth - r.width - 8)) + 'px';
    tip.style.top = Math.max(8, Math.min(y, innerHeight - r.height - 8)) + 'px';
  }
  function bind(el, render, cleanup) {
    var binding = { el: el, render: render, cleanup: cleanup };
    el.setAttribute('data-tip-trigger', '');
    if (!el.hasAttribute('tabindex') && !el.matches('a, button')) el.setAttribute('tabindex', '0');
    function hover(ev) {
      // Closing a card can uncover another chart beneath the stationary mouse.
      if (dismissedAt && Math.abs(ev.clientX - dismissedAt.x) < 3 && Math.abs(ev.clientY - dismissedAt.y) < 3) return;
      dismissedAt = null;
      if (ev.pointerType === 'touch' || dismissed === el) return;
      show(binding, ev);
    }
    el.addEventListener('pointerenter', function (ev) {
      if (!dismissedAt || Math.abs(ev.clientX - dismissedAt.x) >= 3 || Math.abs(ev.clientY - dismissedAt.y) >= 3) {
        if (dismissed === el) dismissed = null;
      }
      hover(ev);
    });
    el.addEventListener('pointermove', hover);
    el.addEventListener('pointerleave', function (ev) {
      if (dismissed === el) { dismissed = null; dismissedAt = null; }
      if (ev.pointerType !== 'touch' && active === binding) leave();
    });
    el.addEventListener('pointercancel', function () { hide(true); });
    el.addEventListener('click', function (ev) {
      // Links keep their ordinary navigation; chart taps toggle the details.
      if (el.matches('a')) { hide(true); return; }
      if (active === binding) { hide(true); return; }
      dismissed = null;
      show(binding, ev.detail ? ev : center());
    });
    function center() { var r = el.getBoundingClientRect(); return { clientX: r.left + r.width / 2, clientY: r.top + r.height / 2 }; }
    el.addEventListener('focus', function () {
      if (el.matches(':focus-visible') && !restoringFocus) {
        dismissed = null; dismissedAt = null; show(binding, center());
      }
    });
    el.addEventListener('blur', function (ev) { if (active === binding && (!tip || !tip.contains(ev.relatedTarget))) hide(false); });
  }
  document.addEventListener('pointerdown', function (ev) {
    if (active && !active.el.contains(ev.target) && !tip.contains(ev.target)) hide(true);
  }, true);
  document.addEventListener('pointermove', function (ev) { pointer = { x: ev.clientX, y: ev.clientY }; }, true);
  document.addEventListener('keydown', function (ev) { if (ev.key === 'Escape') hide(true); });
  // Capture also covers horizontal chart scrollers. Scrolling the details stays usable.
  window.addEventListener('scroll', function (ev) { if (!tip || !tip.contains(ev.target)) hide(true); }, true);
  window.addEventListener('resize', function () { hide(true); });
  window.addEventListener('blur', function () { hide(true); });
  document.addEventListener('visibilitychange', function () { if (document.hidden) hide(true); });
  window.ProgramGymTooltip = {
    bind: bind,
    show: function (el, html, ev) { dismissed = null; show({ el: el, render: function () { return html; } }, ev); }
  };
})();
