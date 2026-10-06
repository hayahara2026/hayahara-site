/* מכבסת היערה: shared site script */
(function(){
  "use strict";
  var root = document.documentElement;
  root.setAttribute('lang', 'he');
  root.setAttribute('dir', 'rtl');

  var yr = document.getElementById('yr'); if (yr) yr.textContent = new Date().getFullYear();

  function store(k, v){ try{ v === null ? localStorage.removeItem(k) : localStorage.setItem(k, v); }catch(e){} }
  function read(k){ try{ return localStorage.getItem(k); }catch(e){ return null; } }

  /* ---- header shadow on scroll ---- */
  var hdrEl = document.getElementById('hdr');
  var stuck = false;
  var onScroll = function(){
    var y = window.scrollY;
    if (!stuck && y > 48){ stuck = true; hdrEl.classList.add('stuck'); }
    else if (stuck && y < 16){ stuck = false; hdrEl.classList.remove('stuck'); }
  };
  onScroll();
  window.addEventListener('scroll', onScroll, {passive:true});

  /* ---- desktop dropdown ---- */
  document.querySelectorAll('.mainnav .has-sub > button').forEach(function(b){
    b.addEventListener('click', function(e){
      e.stopPropagation();
      var li = b.parentNode, was = li.classList.contains('open');
      document.querySelectorAll('.mainnav li.open').forEach(function(o){
        o.classList.remove('open'); o.querySelector('button').setAttribute('aria-expanded','false');
      });
      if (!was){ li.classList.add('open'); b.setAttribute('aria-expanded','true'); }
    });
  });
  document.addEventListener('click', function(){
    document.querySelectorAll('.mainnav li.open').forEach(function(o){
      o.classList.remove('open'); o.querySelector('button').setAttribute('aria-expanded','false');
    });
  });

  /* ---- mobile menu ---- */
  var burger = document.getElementById('burger'), mobnav = document.getElementById('mobnav');
  burger.addEventListener('click', function(){
    var open = mobnav.classList.toggle('open');
    burger.setAttribute('aria-expanded', open ? 'true' : 'false');
  });
  mobnav.addEventListener('click', function(e){
    if (e.target.tagName === 'A'){ mobnav.classList.remove('open'); burger.setAttribute('aria-expanded','false'); }
  });

  /* ---- lead forms -> WhatsApp ---- */
  document.querySelectorAll('form[data-lead]').forEach(function(f){
    f.addEventListener('submit', function(e){
      e.preventDefault();
      if (!f.reportValidity()) return;
      var lines = ['פנייה מהאתר של מכבסת היערה', ''];
      f.querySelectorAll('input,select,textarea').forEach(function(el){
        var v = (el.value || '').trim();
        if (v) lines.push(el.name + ': ' + v);
      });
      window.open('https://wa.me/972532535393?text=' + encodeURIComponent(lines.join('\n')), '_blank', 'noopener');
    });
  });

  /* ---- accessibility ---- */
  var panel = document.getElementById('a11yPanel'), a11yBtn = document.getElementById('a11yBtn');
  var toggles = ['contrast','gray','links','readable','nomotion'];
  var state = { fs: 1, on: {} };
  try { var saved = JSON.parse(read('hy_a11y') || '{}'); if (saved && typeof saved === 'object'){ state.fs = saved.fs || 1; state.on = saved.on || {}; } } catch(e){}

  function apply(){
    root.style.setProperty('--fs', state.fs);
    toggles.forEach(function(t){ root.classList.toggle('a11y-' + t, !!state.on[t]); });
    panel.querySelectorAll('[data-a11y]').forEach(function(b){
      var k = b.getAttribute('data-a11y');
      if (toggles.indexOf(k) > -1) b.setAttribute('aria-pressed', state.on[k] ? 'true' : 'false');
    });
    store('hy_a11y', JSON.stringify(state));
  }
  apply();

  function openPanel(open){
    panel.classList.toggle('open', open);
    a11yBtn.setAttribute('aria-expanded', open ? 'true' : 'false');
  }
  a11yBtn.addEventListener('click', function(e){ e.stopPropagation(); openPanel(!panel.classList.contains('open')); });
  document.getElementById('a11yClose').addEventListener('click', function(){ openPanel(false); a11yBtn.focus(); });
  panel.addEventListener('click', function(e){ e.stopPropagation(); });
  document.addEventListener('click', function(){ openPanel(false); });

  panel.querySelectorAll('[data-a11y]').forEach(function(b){
    b.addEventListener('click', function(){
      var k = b.getAttribute('data-a11y');
      if (k === 'bigger') state.fs = Math.min(1.5, +(state.fs + 0.1).toFixed(2));
      else if (k === 'smaller') state.fs = Math.max(0.85, +(state.fs - 0.1).toFixed(2));
      else if (k === 'reset'){ state = { fs: 1, on: {} }; }
      else state.on[k] = !state.on[k];
      apply();
    });
  });

  /* ---- Escape closes the accessibility panel ---- */
  document.addEventListener('keydown', function(e){
    if (e.key === 'Escape' && panel.classList.contains('open')){ openPanel(false); a11yBtn.focus(); }
  });

  /* ---- click-to-load map (nothing loads from Google before the click) ---- */
  document.querySelectorAll('[data-map]').forEach(function(btn){
    btn.addEventListener('click', function(){
      var box = btn.parentNode, f = document.createElement('iframe');
      f.src = btn.getAttribute('data-map');
      f.title = btn.getAttribute('data-title') || 'מפה';
      f.loading = 'lazy';
      f.referrerPolicy = 'no-referrer-when-downgrade';
      f.setAttribute('allowfullscreen', '');
      box.innerHTML = '';
      box.appendChild(f);
    });
  });

  /* ---- cookie notice ---- */
  var ck = document.getElementById('cookie');
  if (ck){
    if (!read('hy_cookie')) setTimeout(function(){ ck.classList.add('show'); }, 900);
    var ckClose = function(v){ store('hy_cookie', v); ck.classList.remove('show'); };
    document.getElementById('ckOk').addEventListener('click', function(){ ckClose('all'); });
    document.getElementById('ckNo').addEventListener('click', function(){ ckClose('essential'); });
  }
})();
