/*
 * DjangoBlog — transições mágicas (SITE_THEME=magic).
 *
 * - Nevoeiro: ao clicar num link interno, uma névoa cobre a tela; a página nova
 *   já nasce coberta (classe fog-in, definida no <head>) e a névoa se dissolve.
 * - Revelação ao rolar: cards e blocos surgem com um brilho de vela.
 * - Título do post escrito letra por letra.
 * - Lumos/Nox: círculo de luz que se expande a partir do botão.
 * - Parallax suave nas velas do teto.
 * - Trilha: o tema de Harry Potter (blog/static/blog/audio), desligada por padrão.
 *
 * Tudo respeita "Turn effects off" (data-fx="off") e prefers-reduced-motion.
 */
(function () {
    'use strict';

    var root = document.documentElement;
    if (root.getAttribute('data-theme') !== 'magic') { return; }
    window.__trLoaded = true;

    var reduce = !!(window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches);
    function fxOn() { return root.getAttribute('data-fx') !== 'off' && !reduce; }
    function store(key, value) { try { window.localStorage.setItem(key, value); } catch (e) { /* sem armazenamento */ } }
    function read(key) { try { return window.localStorage.getItem(key); } catch (e) { return null; } }
    function flag(value) { try { window.sessionStorage.setItem('djangoblog-fog', value); } catch (e) { /* sem armazenamento */ } }
    function canAnimate() { return typeof Element.prototype.animate === 'function'; }

    /* ---------- Nevoeiro ---------- */
    var veil = document.getElementById('fog-veil');

    function dissolveVeil() {
        if (!veil) { root.classList.remove('fog-in'); return; }
        if (!canAnimate()) { root.classList.remove('fog-in'); return; }
        var a = veil.animate([{ opacity: 1 }, { opacity: 0 }], { duration: 900, easing: 'ease-in-out', fill: 'forwards' });
        a.onfinish = function () {
            a.cancel();
            root.classList.remove('fog-in');
            veil.classList.remove('is-on');
        };
    }

    if (root.classList.contains('fog-in')) {
        window.setTimeout(dissolveVeil, 250);
    }

    window.addEventListener('pageshow', function (e) {
        /* voltar pelo histórico: não deixa a névoa presa na tela */
        if (e.persisted && veil) {
            veil.getAnimations().forEach(function (a) { a.cancel(); });
            veil.classList.remove('is-on');
            root.classList.remove('fog-in');
        }
    });

    function isInternalNavigation(a, e) {
        if (e.defaultPrevented || e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) { return false; }
        if (a.target && a.target !== '_self') { return false; }
        if (a.hasAttribute('download') || a.hasAttribute('data-no-fog')) { return false; }
        if (a.hasAttribute('data-bs-toggle')) { return false; }
        var href = a.getAttribute('href');
        if (!href || href.charAt(0) === '#' || /^(mailto:|tel:|javascript:)/i.test(href)) { return false; }
        if (a.origin !== window.location.origin) { return false; }
        if (a.pathname === window.location.pathname && a.search === window.location.search) { return false; }
        return true;
    }

    document.addEventListener('click', function (e) {
        if (!veil || !fxOn() || !canAnimate()) { return; }
        var a = e.target.closest ? e.target.closest('a[href]') : null;
        if (!a || !isInternalNavigation(a, e)) { return; }
        e.preventDefault();
        var url = a.href;
        veil.classList.add('is-on');
        flag('1');
        var anim = veil.animate([{ opacity: 0 }, { opacity: 1 }], { duration: 650, easing: 'ease-in-out', fill: 'forwards' });
        var go = function () { window.location.href = url; };
        anim.onfinish = go;
        window.setTimeout(go, 1200); /* garantia */
    });

    /* ---------- Revelação ao rolar ---------- */
    (function () {
        if (!root.classList.contains('tr-js') || !('IntersectionObserver' in window)) { return; }
        var items = document.querySelectorAll(
            '.post-card, .comment, .about__card, .about__facts li, .about__cta, .contact__form, .comments__form, .post-detail__block'
        );
        var seen = 0;
        var io = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                if (entry.isIntersecting) {
                    entry.target.classList.add('tr-in');
                    io.unobserve(entry.target);
                }
            });
        }, { threshold: 0.12 });
        Array.prototype.forEach.call(items, function (el) {
            el.classList.add('tr-reveal');
            el.style.setProperty('--tr-d', ((seen++ % 3) * 0.12) + 's');
            io.observe(el);
        });
    })();

    /* ---------- Título que se escreve ---------- */
    (function () {
        var h = document.querySelector('[data-typewrite]');
        if (!h || !fxOn()) { return; }
        var text = h.textContent.replace(/\s+/g, ' ').trim();
        h.setAttribute('aria-label', text);
        h.textContent = '';
        var letters = [];
        text.split(' ').forEach(function (word, i, all) {
            var w = document.createElement('span');
            w.className = 'tw-word';
            w.setAttribute('aria-hidden', 'true');
            word.split('').forEach(function (c) {
                var s = document.createElement('span');
                s.className = 'tw-ch';
                s.textContent = c;
                w.appendChild(s);
                letters.push(s);
            });
            h.appendChild(w);
            if (i < all.length - 1) { h.appendChild(document.createTextNode(' ')); }
        });
        var i = 0;
        var start = root.classList.contains('fog-in') ? 900 : 150;
        window.setTimeout(function () {
            var timer = window.setInterval(function () {
                if (i < letters.length) { letters[i++].classList.add('is-on'); }
                else { window.clearInterval(timer); h.classList.add('tw-done'); }
            }, 48);
        }, start);
    })();

    /* ---------- Lumos / Nox em círculo de luz ---------- */
    (function () {
        var btn = document.getElementById('mode-toggle');
        if (!btn) { return; }
        var replay = false;
        var busy = false;
        document.addEventListener('click', function (e) {
            if (replay || !btn.contains(e.target)) { return; }
            if (!fxOn() || !canAnimate()) { return; }
            e.stopImmediatePropagation();
            e.preventDefault();
            if (busy) { return; }
            busy = true;
            var nextNox = root.getAttribute('data-mode') !== 'nox';
            var r = btn.getBoundingClientRect();
            var x = r.left + r.width / 2;
            var y = r.top + r.height / 2;
            var wipe = document.createElement('div');
            wipe.className = 'lux-wipe';
            wipe.setAttribute('aria-hidden', 'true');
            wipe.style.setProperty('--lux-x', x + 'px');
            wipe.style.setProperty('--lux-y', y + 'px');
            wipe.style.setProperty('--lux-bg', nextNox ? '#0E1325' : '#F0E3C2');
            wipe.style.setProperty('--lux-glow', nextNox ? 'rgba(120, 140, 230, 0.55)' : 'rgba(255, 240, 190, 0.95)');
            document.body.appendChild(wipe);
            var big = Math.hypot(Math.max(x, window.innerWidth - x), Math.max(y, window.innerHeight - y)) + 40;
            var grow = wipe.animate(
                [{ clipPath: 'circle(0px at ' + x + 'px ' + y + 'px)' }, { clipPath: 'circle(' + big + 'px at ' + x + 'px ' + y + 'px)' }],
                { duration: 950, easing: 'cubic-bezier(.4,0,.2,1)', fill: 'forwards' }
            );
            grow.onfinish = function () {
                replay = true; btn.click(); replay = false;
                var out = wipe.animate([{ opacity: 1 }, { opacity: 0 }], { duration: 420, fill: 'forwards' });
                out.onfinish = function () { wipe.remove(); busy = false; };
            };
        }, true);
    })();

    /* ---------- Parallax das velas ---------- */
    (function () {
        var ceiling = document.querySelector('.candle-ceiling');
        if (!ceiling || reduce) { return; }
        var candles = Array.prototype.slice.call(ceiling.querySelectorAll('.candle'));
        var ticking = false;
        function paint() {
            ticking = false;
            if (!fxOn()) { candles.forEach(function (c) { c.style.translate = ''; }); return; }
            var y = Math.min(window.scrollY, 320);
            candles.forEach(function (c, i) { c.style.translate = '0 ' + (y * (i % 2 ? 0.42 : 0.2)) + 'px'; });
        }
        window.addEventListener('scroll', function () {
            if (!ticking) { ticking = true; window.requestAnimationFrame(paint); }
        }, { passive: true });
        paint();
    })();

    /* ---------- Trilha sonora ---------- */
    (function () {
        var btn = document.getElementById('music-toggle');
        if (!btn || !window.Audio) { return; }
        var audio = null;
        var wantsPlay = read('djangoblog-music') === 'on';
        var VOLUME = 0.35;
        var fadeTimer = null;

        function paint() {
            var on = !!(audio && !audio.paused) || wantsPlay;
            btn.setAttribute('aria-pressed', on ? 'true' : 'false');
            btn.textContent = on ? 'Music: on' : 'Music: off';
        }
        function ensure() {
            if (audio) { return audio; }
            audio = new Audio(btn.getAttribute('data-src'));
            audio.loop = true;
            audio.preload = 'auto';
            audio.volume = 0;
            var saved = parseFloat(read('djangoblog-music-t'));
            if (saved > 0) {
                audio.addEventListener('loadedmetadata', function () {
                    try { if (saved < audio.duration - 1) { audio.currentTime = saved; } } catch (e) { /* sem seek */ }
                }, { once: true });
            }
            return audio;
        }
        function fade(to, done) {
            window.clearInterval(fadeTimer);
            fadeTimer = window.setInterval(function () {
                var v = audio.volume, step = 0.03;
                if (Math.abs(to - v) <= step) { audio.volume = to; window.clearInterval(fadeTimer); if (done) { done(); } }
                else { audio.volume = v + (to > v ? step : -step); }
            }, 60);
        }
        function play() {
            ensure();
            var p = audio.play();
            if (p && p.then) {
                p.then(function () { fade(VOLUME); paint(); }).catch(function () {
                    /* o navegador pede um gesto: começa no primeiro clique ou tecla */
                    var resume = function () { document.removeEventListener('pointerdown', resume); document.removeEventListener('keydown', resume); if (wantsPlay) { play(); } };
                    document.addEventListener('pointerdown', resume, { once: true });
                    document.addEventListener('keydown', resume, { once: true });
                    paint();
                });
            }
        }
        function pause() {
            if (!audio) { return; }
            fade(0, function () { audio.pause(); paint(); });
        }

        btn.addEventListener('click', function () {
            wantsPlay = !wantsPlay;
            store('djangoblog-music', wantsPlay ? 'on' : 'off');
            if (wantsPlay) { play(); } else { pause(); }
            paint();
        });

        function saveTime() { if (audio && !audio.paused) { store('djangoblog-music-t', String(audio.currentTime)); } }
        window.setInterval(saveTime, 1500);
        window.addEventListener('pagehide', saveTime);

        paint();
        if (wantsPlay) { play(); }
    })();
})();
