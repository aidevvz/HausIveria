/* Iveria Immobilien — gemeinsames Skript für alle Seiten */
(function(){
  "use strict";
  var reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  var fine = matchMedia('(hover: hover) and (pointer: fine)').matches;
  var $ = function(s, r){ return (r||document).querySelector(s); };
  var $$ = function(s, r){ return Array.prototype.slice.call((r||document).querySelectorAll(s)); };
  var page = document.body.getAttribute('data-page') || '';
  var header = $('#siteHeader');
  var wa = $('.wa');

  /* ---------- Aktiver Menüpunkt ---------- */
  $$('.nav a[data-page]').forEach(function(a){ if(a.getAttribute('data-page') === page) a.classList.add('active'); });

  /* ---------- Mobiles Menü ---------- */
  var mb = $('#menuBtn'), nav = $('#nav');
  if(mb && nav){
    mb.addEventListener('click', function(){
      var o = nav.classList.toggle('open');
      mb.setAttribute('aria-expanded', o); mb.textContent = o ? 'Schließen' : 'Menü';
      header.classList.toggle('menu-open', o);
      if(o) header.classList.add('on-dark'); else syncHeader();
    });
    $$('a', nav).forEach(function(a){ a.addEventListener('click', function(){ nav.classList.remove('open'); mb.setAttribute('aria-expanded', false); mb.textContent = 'Menü'; header.classList.remove('menu-open'); }); });
  }

  /* ---------- Cookie-Hinweis ---------- */
  var cb = $('#cookie-banner');
  if(cb){
    var seen = null; try { seen = localStorage.getItem('hi-cookie-consent'); } catch(e){}
    if(!seen) setTimeout(function(){ cb.classList.add('show'); }, 4000);
    var set = function(v){ try { localStorage.setItem('hi-cookie-consent', v); } catch(e){} cb.classList.remove('show'); };
    var ab = $('#cookie-accept'), db = $('#cookie-decline');
    if(ab) ab.addEventListener('click', function(){ set('accepted'); });
    if(db) db.addEventListener('click', function(){ set('declined'); });
  }

  /* ---------- Formulare: Rückmeldung beim Absenden ---------- */
  $$('form[data-form]').forEach(function(f){
    f.addEventListener('submit', function(){ var b = $("button[type='submit']", f); if(b){ b.disabled = true; b.textContent = 'wird gesendet …'; } });
  });

  /* ---------- FAQ weich öffnen ---------- */
  $$('.faq details').forEach(function(d){
    var s = $('summary', d), a = $('.ans', d);
    if(!s || !a) return;
    s.addEventListener('click', function(e){
      if(reduce || !window.gsap) return;
      e.preventDefault();
      if(d.open){ gsap.to(a, {height:0, duration:.45, ease:'power3.inOut', onComplete:function(){ d.open = false; a.style.height = ''; }}); }
      else { d.open = true; gsap.fromTo(a, {height:0}, {height:a.scrollHeight, duration:.6, ease:'expo.out', onComplete:function(){ a.style.height = ''; }}); }
    });
  });

  /* ---------- Cursor und magnetische Knöpfe ---------- */
  var cur = $('#cursor');
  if(cur && fine && !reduce){
    var x=0,y=0,cx=0,cy=0;
    addEventListener('pointermove', function(e){ x=e.clientX; y=e.clientY; }, {passive:true});
    (function loop(){ cx+=(x-cx)*.2; cy+=(y-cy)*.2; cur.style.transform = 'translate('+cx+'px,'+cy+'px) scale('+(cur.classList.contains('on')?1:0)+')'; requestAnimationFrame(loop); })();
    $$('[data-cursor]').forEach(function(el){
      el.addEventListener('pointerenter', function(){ cur.textContent = el.getAttribute('data-cursor'); cur.classList.add('on'); });
      el.addEventListener('pointerleave', function(){ cur.classList.remove('on'); });
    });
  }
  if(fine && !reduce){
    $$('.magnetic').forEach(function(b){
      b.addEventListener('pointermove', function(e){ var r=b.getBoundingClientRect(); b.style.translate=((e.clientX-r.left-r.width/2)*.25)+'px '+((e.clientY-r.top-r.height/2)*.35)+'px'; });
      b.addEventListener('pointerleave', function(){ b.style.transition='translate 600ms cubic-bezier(0.23,1,0.32,1), color 450ms, transform 160ms'; b.style.translate='0 0'; setTimeout(function(){ b.style.transition=''; }, 600); });
    });
  }

  /* ---------- Kopfzeile über dunklen Flächen ---------- */
  var darkAreas = [];
  function syncHeader(){
    if(header.classList.contains('menu-open')) return;
    var y = 40, on = false;
    darkAreas.forEach(function(el){ var r = el.getBoundingClientRect(); if(r.top <= y && r.bottom >= y) on = true; });
    if(header.dataset.forceDark === '1') on = true;
    header.classList.toggle('on-dark', on);
  }
  function syncSolid(){
    var hero = $('.hero, .phero, .ehead');
    var limit = hero ? Math.max(80, hero.getBoundingClientRect().bottom + window.scrollY - 90) : 80;
    if(!header.dataset.lockSolid) header.classList.toggle('solid', window.scrollY > (page==='index' ? limit : 60));
  }
  darkAreas = $$('.dark, .card:nth-child(2)');
  addEventListener('scroll', function(){ syncHeader(); syncSolid(); }, {passive:true});
  syncHeader(); syncSolid();

  /* ---------- Ohne Animation: alles sichtbar ---------- */
  var intro = $('#intro');
  if(reduce || !window.gsap || !window.ScrollTrigger){
    if(intro) intro.remove();
    var hc = $('#hCopy'); if(hc){ hc.style.opacity = 1; hc.classList.add('on'); }
    if(wa) wa.classList.remove('wait');
    $$('.phero').forEach(function(p){ p.classList.add('inverted'); });
    return;
  }
  gsap.registerPlugin(ScrollTrigger);
  // Adressleiste am Handy soll keine Neuberechnung auslösen
  ScrollTrigger.config({ignoreMobileResize:true});

  // Bild in eine eigene Ebene legen: Intro animiert die Ebene, Scrollen das Fenster.
  // So greifen nie zwei Animationen auf dasselbe Element zu.
  function revealLayer(win){ var img = $('img', win); if(!img) return null; var r = document.createElement('div'); r.className = 'reveal-layer'; r.style.cssText = 'position:absolute;inset:0;overflow:hidden'; img.parentNode.insertBefore(r, img); r.appendChild(img); return r; }

  /* ---------- Weiches Scrollen ---------- */
  var lenis = null;
  if(window.Lenis){
    try {
      lenis = new Lenis({lerp:.085});
      lenis.on('scroll', function(){ ScrollTrigger.update(); syncHeader(); syncSolid(); });
      gsap.ticker.add(function(t){ lenis.raf(t*1000); }); gsap.ticker.lagSmoothing(0);
      $$('a[href^="#"]').forEach(function(a){ a.addEventListener('click', function(e){ var id=a.getAttribute('href'); if(id.length<2) return; var el=$(id); if(el){ e.preventDefault(); lenis.scrollTo(el, {duration:1.6}); } }); });
    } catch(e){ lenis = null; }
  }

  /* ---------- Wörter in Zeilenmasken teilen ---------- */
  function split(el){
    if(el.dataset.splitDone) return; el.dataset.splitDone = '1';
    el.innerHTML = el.innerHTML.replace(/(<em>)?([^<\s]+)(<\/em>)?([^<\s]*)/g, function(m,a,w,b,c){
      return '<span style="display:inline-block;overflow:hidden;vertical-align:top;padding-bottom:.08em"><span class="wd" style="display:inline-block">'+(a||'')+w+(b||'')+(c||'')+'</span></span>';
    });
  }
  var mobile = matchMedia('(max-width:600px)').matches;
  var tablet = matchMedia('(max-width:980px)').matches;

  /* ================= Startseite ================= */
  var hero = $('#hero');
  if(hero){
    $$('.h-line .in').forEach(split);
    var firstVisit = true; try { firstVisit = localStorage.getItem('hi-intro-seen') !== 'yes'; localStorage.setItem('hi-intro-seen','yes'); } catch(e){}
    if(lenis) lenis.stop();
    var tl = gsap.timeline({onComplete:function(){ if(intro) intro.remove(); if(lenis) lenis.start(); }});
    if(intro && firstVisit){
      var arch = $('#introArch'), il = $('#introI'), L = arch.getTotalLength();
      gsap.set(arch, {strokeDasharray:L, strokeDashoffset:L}); gsap.set(il, {strokeDasharray:40, strokeDashoffset:40});
      var skip = $('#introSkip');
      if(skip) skip.addEventListener('click', function(){ tl.progress(.62); });
      tl.to(arch, {strokeDashoffset:0, duration:1.2, ease:'power2.inOut'}, .3)
        .to(il, {strokeDashoffset:0, duration:.5, ease:'power2.out'}, '-=.25')
        .from('#introName', {opacity:0, y:8, duration:.6, ease:'power2.out'}, '-=.2')
        .to('#intro > div', {scale:.6, opacity:0, duration:.6, ease:'power2.in'}, '+=.3')
        .to(intro, {opacity:0, duration:.5, ease:'power1.out'}, '-=.15');
    } else if(intro){ intro.remove(); intro = null; }
    var hRev = revealLayer($('#hWin'));
    tl.from(hRev, {clipPath:'inset(100% 0% 0% 0%)', duration:1.5, ease:'expo.inOut'}, intro ? '-=.55' : 0)
      .from(hRev, {scale:1.14, duration:2.2, ease:'expo.out'}, '<')
      .from('.h-line .wd', {yPercent:110, duration:1.3, ease:'expo.out', stagger:.06}, '-=1.1')
      .from(['.site-header','.h-meta'], {opacity:0, y:-10, duration:.9, ease:'power2.out'}, '-=.8');

    var startClip = mobile ? 'inset(33% 12% 21% 12% round 50vw 50vw 0vw 0vw)' : 'inset(29% 34% 17% 34% round 50vw 50vw 0vw 0vw)';
    var ht = gsap.timeline({scrollTrigger:{trigger:hero, start:'top top', end:'+=130%', pin:true, scrub:1,
      onUpdate:function(s){ header.dataset.forceDark = (s.progress>.35 && s.progress<1) ? '1' : ''; syncHeader(); $('#hCopy').classList.toggle('on', s.progress>.75); },
      onLeave:function(){ header.dataset.forceDark=''; header.classList.add('solid'); if(wa) wa.classList.remove('wait'); syncHeader(); },
      onEnterBack:function(){ header.classList.remove('solid'); if(wa) wa.classList.add('wait'); }}});
    ht.fromTo('#hWin', {clipPath:startClip}, {clipPath:'inset(0% 0% 0% 0% round 0vw 0vw 0vw 0vw)', ease:'power2.inOut', duration:1, immediateRender:false}, 0)
      .fromTo('#hWin img', {scale:1.05}, {scale:1, ease:'power2.inOut', duration:1, immediateRender:false}, 0)
      .to('#hWin', {'--shade':1, duration:.6}, .3)
      .to('.h-line', {color:'#FAFAF7', duration:.4, ease:'none'}, .3)
      .to('.h-l1', {y:function(){ return innerHeight*.06; }, duration:1, ease:'power2.inOut'}, 0)
      .to('.h-meta', {opacity:0, duration:.25}, 0)
      .fromTo('#hCopy', {opacity:0, y:30}, {opacity:1, y:0, duration:.35}, .75);
    if(mobile) ht.to('.h-l2', {opacity:0, duration:.3}, .55);
  }

  /* Vier Wände zeichnen das Logo */
  var house = $('#house');
  if(house){
    var ws = $$('.house .w'), ar = $('.house .arch'), ln = $('.house .iline');
    ws.concat([ar, ln]).forEach(function(el){ var L = el.getTotalLength(); gsap.set(el, {strokeDasharray:L, strokeDashoffset:L}); });
    gsap.set('.house .lbl', {opacity:0});
    // Am Handy und Tablet: kein Festhalten, die Zeichnung entsteht beim normalen Scrollen
    var wt = tablet
      ? gsap.timeline({scrollTrigger:{trigger:'#house', start:'top 85%', end:'bottom 45%', scrub:1}})
      : gsap.timeline({scrollTrigger:{trigger:'#walls', start:'center center', end:'+=160%', pin:true, scrub:1}});
    if(!tablet) wt.from('#walls .grid > div:first-child > *', {opacity:0, y:30, stagger:.1, duration:.5});
    else gsap.from('#walls .grid > div:first-child > *', {opacity:0, y:30, stagger:.1, duration:1, ease:'expo.out', scrollTrigger:{trigger:'#walls', start:'top 80%'}});
    wt.to(ws[0], {strokeDashoffset:0, duration:.6}).to('.house .l1', {opacity:1, duration:.3}, '<.2')
      .to(ws[1], {strokeDashoffset:0, duration:.6}).to('.house .l2', {opacity:1, duration:.3}, '<.2')
      .to(ws[2], {strokeDashoffset:0, duration:.6}).to('.house .l3', {opacity:1, duration:.3}, '<.2')
      .to(ar, {strokeDashoffset:0, duration:.8}).to('.house .l4', {opacity:1, duration:.3}, '<.3')
      .to(ln, {strokeDashoffset:0, duration:.5})
      .to('.house .w, .house .arch', {strokeWidth:1.1, duration:.4}, '<');
  }

  /* ================= Unterseiten-Hero ================= */
  $$('.phero').forEach(function(ph){
    var win = $('.ph-window', ph), img = $('img', win), txt = $('.ph-text', ph);
    var h1 = $('h1', ph); if(h1) split(h1);
    var cs = getComputedStyle(win).clipPath;
    var rev = revealLayer(win);
    gsap.timeline({defaults:{ease:'expo.out'}})
      .from(rev, {clipPath:'inset(100% 0% 0% 0%)', duration:1.5, ease:'expo.inOut'})
      .from(rev, {scale:1.2, duration:2.2}, '<')
      .from($$('.wd', ph), {yPercent:110, duration:1.2, stagger:.05}, '-=1.3')
      .from([$('.eyebrow', ph), $('.ph-text p', ph)], {opacity:0, y:16, duration:1, stagger:.1}, '-=1');
    var pt = gsap.timeline({scrollTrigger:{trigger:ph, start:'top top', end:tablet ? '+=60%' : '+=80%', pin:true, scrub:1,
      onUpdate:function(s){ ph.classList.toggle('inverted', s.progress > .78); header.dataset.forceDark = (s.progress>.6 && s.progress<1) ? '1' : ''; syncHeader(); },
      onLeave:function(){ header.dataset.forceDark=''; syncHeader(); }}});
    pt.fromTo(win, {clipPath:cs}, {clipPath:'inset(0% 0% 0% 0% round 0vw 0vw 0vw 0vw)', ease:'power2.inOut', duration:1, immediateRender:false}, 0)
      .fromTo(img, {scale:1.04}, {scale:1, ease:'power2.inOut', duration:1, immediateRender:false}, 0)
      .to(win, {'--shade':1, duration:.4}, .45);
  });

  /* ================= Allgemeine Reveals ================= */
  $$('[data-split]').forEach(function(h){
    split(h);
    gsap.from($$('.wd', h), {yPercent:110, duration:1.2, ease:'expo.out', stagger:.04, scrollTrigger:{trigger:h, start:'top 86%'}});
  });
  $$('[data-rise]').forEach(function(el){
    gsap.from(el, {opacity:0, y:30, duration:1.1, ease:'expo.out', scrollTrigger:{trigger:el, start:'top 88%'}});
  });

  // Bilder öffnen sich von unten, leichte Parallaxe
  $$('.ed-img, .prop .ph').forEach(function(box){
    var img = $('img', box);
    gsap.from(box, {clipPath:'inset(100% 0 0 0)', duration:1.6, ease:'expo.inOut', scrollTrigger:{trigger:box, start:'top 88%'}});
    gsap.from(img, {scale:1.3, duration:2, ease:'expo.out', scrollTrigger:{trigger:box, start:'top 88%'}});
    gsap.fromTo(img, {yPercent:-5}, {yPercent:5, ease:'none', scrollTrigger:{trigger:box, start:'top bottom', end:'bottom top', scrub:true}});
  });
  $$('.prop').forEach(function(p){
    gsap.from($$('.meta, h3, .row, .info', p), {opacity:0, y:20, stagger:.08, duration:1, ease:'expo.out', scrollTrigger:{trigger:p, start:'top 75%'}});
  });

  // Gestapelte Karten
  var cards = $$('.card');
  cards.forEach(function(c, i){
    gsap.fromTo($('.img img', c), {scale:1.25}, {scale:1, ease:'none', scrollTrigger:{trigger:c, start:'top bottom', end:'top 11%', scrub:true}});
    if(i < cards.length-1) gsap.to(c, {scale:.92, opacity:.4, ease:'none', scrollTrigger:{trigger:cards[i+1], start:'top bottom', end:'top 11%', scrub:true}});
  });

  // Zahlen zählen
  $$('.stat b[data-to]').forEach(function(b){
    var to = +b.getAttribute('data-to'), suf = b.getAttribute('data-suf') || '', o = {v:0};
    b.innerHTML = '0' + suf;
    ScrollTrigger.create({trigger:b, start:'top 85%', once:true, onEnter:function(){ gsap.to(o, {v:to, duration:2, ease:'expo.out', onUpdate:function(){ b.innerHTML = Math.round(o.v) + suf; }}); }});
  });
  $$('.sgrid').forEach(function(g){ gsap.from($$('.stat', g), {opacity:0, y:40, stagger:.1, duration:1.2, ease:'expo.out', scrollTrigger:{trigger:g, start:'top 85%'}}); });
  var rs = $$('#regions span');
  if(rs.length) ScrollTrigger.create({trigger:'#regions', start:'top 85%', end:'bottom 45%', scrub:true, onUpdate:function(s){ rs.forEach(function(r,i){ r.classList.toggle('on', s.progress >= i/rs.length + .05); }); }});

  // Ablauf: Linie zeichnet sich
  $$('.steps').forEach(function(st){
    var bar = $('.bar', st);
    if(bar) gsap.fromTo(bar, {scaleX:0}, {scaleX:1, ease:'none', scrollTrigger:{trigger:st, start:'top 80%', end:'bottom 55%', scrub:true}});
    gsap.from($$('li', st), {opacity:0, y:30, stagger:.12, duration:1.1, ease:'expo.out', scrollTrigger:{trigger:st, start:'top 82%'}});
  });
  // Leistungsliste, Werte
  $$('.feats, .vals, .blist').forEach(function(l){ gsap.from(l.children, {opacity:0, y:26, stagger:.08, duration:1, ease:'expo.out', scrollTrigger:{trigger:l, start:'top 82%'}}); });

  // Zitat Wort für Wort
  $$('.quote blockquote').forEach(function(q){
    q.innerHTML = q.textContent.trim().split(/\s+/).map(function(w){ return '<span class="w">'+w+'</span>'; }).join(' ');
    gsap.fromTo($$('.w', q), {opacity:.15}, {opacity:1, stagger:.1, ease:'none', scrollTrigger:{trigger:q, start:'top 78%', end:'bottom 45%', scrub:true}});
  });

  // Bogenlinien zeichnen sich
  $$('.arch-line path').forEach(function(p){ var L = p.getTotalLength(); gsap.fromTo(p, {strokeDasharray:L, strokeDashoffset:L}, {strokeDashoffset:0, duration:1.8, ease:'power2.inOut', scrollTrigger:{trigger:p, start:'top 90%'}}); });

  // Bogentür
  $$('.door').forEach(function(d){
    gsap.from(d, {clipPath:'inset(100% 0 0 0)', duration:1.8, ease:'expo.inOut', scrollTrigger:{trigger:d, start:'top 80%'}});
    gsap.fromTo($('img', d), {yPercent:-6, scale:1.2}, {yPercent:6, scale:1, ease:'none', scrollTrigger:{trigger:d, start:'top bottom', end:'bottom top', scrub:true}});
  });

  // Wortmarke im Fuß
  var wm = $('#wordmark');
  if(wm) gsap.from($$('span', wm), {yPercent:100, opacity:0, stagger:.06, duration:1.4, ease:'expo.out', scrollTrigger:{trigger:wm, start:'top 92%'}});

  addEventListener('load', function(){ ScrollTrigger.refresh(); });
})();
