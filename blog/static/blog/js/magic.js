/*
 * DjangoBlog — comportamento do tema "pergaminho e velas" (SITE_THEME=magic).
 *
 * - Alterna entre Lumos (claro) e Nox (escuro) e lembra a escolha.
 * - Liga e desliga os efeitos (velas, luz da varinha, faíscas, cursor).
 * - Luz que segue o cursor: no Lumos é um brilho quente; no Nox é uma aura
 *   branca que só aparece quando o mouse está sobre algo clicável.
 * - Rastro de faíscas atrás do cursor.
 * - Cartas (mensagens do sistema): fecham sozinhas e podem ser dispensadas.
 *
 * Os atributos data-mode e data-fx do <html> são definidos antes da primeira
 * pintura por um pequeno script no <head> (veja base.html), para a página
 * não "piscar" no tema errado.
 */
(function () {
    'use strict';

    var root = document.documentElement;
    if (root.getAttribute('data-theme') !== 'magic') {
        return;
    }

    var reduceMotion = !!(window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches);
    var finePointer = !!(window.matchMedia && window.matchMedia('(pointer: fine)').matches);

    function save(key, value) {
        try {
            window.localStorage.setItem(key, value);
        } catch (e) {
            /* armazenamento bloqueado: a escolha vale só até recarregar */
        }
    }

    /* ---------- Lumos / Nox ---------- */
    var modeButton = document.getElementById('mode-toggle');

    function paintModeButton() {
        if (!modeButton) {
            return;
        }
        var nox = root.getAttribute('data-mode') === 'nox';
        var label = modeButton.querySelector('[data-mode-label]');
        if (label) {
            label.textContent = nox ? 'Lumos' : 'Nox';
        }
        modeButton.setAttribute('aria-label', nox ? 'Switch to the light theme' : 'Switch to the dark theme');
    }

    function setMode(mode) {
        /* data-toggled marca que foi o visitante quem trocou: só então as velas
           animam o apagar e o acender. Na carga da página elas já nascem no estado certo. */
        root.setAttribute('data-toggled', '1');
        root.setAttribute('data-mode', mode);
        root.setAttribute('data-bs-theme', mode === 'nox' ? 'dark' : 'light');
        save('djangoblog-mode', mode);
        paintModeButton();
    }

    if (modeButton) {
        modeButton.addEventListener('click', function () {
            setMode(root.getAttribute('data-mode') === 'nox' ? 'lumos' : 'nox');
        });
    }
    paintModeButton();

    /* ---------- Efeitos ligados / desligados ---------- */
    var fxButton = document.getElementById('fx-toggle');
    var glow = null;

    function effectsOn() {
        return root.getAttribute('data-fx') !== 'off';
    }

    function paintFxButton() {
        if (fxButton) {
            fxButton.textContent = effectsOn() ? 'Turn effects off' : 'Turn effects on';
        }
    }

    if (fxButton) {
        fxButton.addEventListener('click', function () {
            var next = effectsOn() ? 'off' : 'on';
            root.setAttribute('data-fx', next);
            save('djangoblog-fx', next);
            paintFxButton();
            if (next === 'off' && glow) {
                glow.classList.remove('is-on');
            }
        });
    }
    paintFxButton();

    /* ---------- Luz da varinha e faíscas ---------- */
    if (finePointer) {
        glow = document.createElement('div');
        glow.className = 'wand-glow';
        glow.setAttribute('aria-hidden', 'true');
        document.body.appendChild(glow);

        var pointerX = 0;
        var pointerY = 0;
        var overClickable = false;
        var frameRequested = false;
        var lastSpark = null;
        var lastSparkTime = 0;
        var sparkCount = 0;

        var CLICKABLE = 'a, button, [role="button"], summary, input[type="submit"]';

        var paintGlow = function () {
            frameRequested = false;
            glow.style.transform = 'translate3d(' + pointerX + 'px,' + pointerY + 'px,0)';
            var nox = root.getAttribute('data-mode') === 'nox';
            /* Lumos: brilho sempre que o mouse se move. Nox: aura só sobre algo clicável. */
            glow.classList.toggle('is-on', effectsOn() && (!nox || overClickable));
        };

        var addSpark = function (x, y) {
            if (reduceMotion || !effectsOn()) {
                return;
            }
            var now = Date.now();
            if (now - lastSparkTime < 30) {
                return;
            }
            if (lastSpark && Math.hypot(x - lastSpark.x, y - lastSpark.y) < 26) {
                return;
            }
            lastSparkTime = now;
            lastSpark = { x: x, y: y };

            var size = 9 + (sparkCount++ % 3) * 3;
            var spark = document.createElement('span');
            spark.className = 'spark';
            spark.style.left = (x - size / 2) + 'px';
            spark.style.top = (y - size / 2) + 'px';
            spark.style.width = size + 'px';
            spark.style.height = size + 'px';
            spark.setAttribute('aria-hidden', 'true');
            document.body.appendChild(spark);

            var remove = function () {
                if (spark.parentNode) {
                    spark.parentNode.removeChild(spark);
                }
            };
            spark.addEventListener('animationend', remove);
            window.setTimeout(remove, 1000);
        };

        document.addEventListener('pointermove', function (event) {
            if (event.pointerType && event.pointerType !== 'mouse') {
                return;
            }
            pointerX = event.clientX;
            pointerY = event.clientY;
            var target = event.target;
            overClickable = !!(target && target.closest && target.closest(CLICKABLE));
            if (!frameRequested) {
                frameRequested = true;
                window.requestAnimationFrame(paintGlow);
            }
            addSpark(pointerX, pointerY);
        }, { passive: true });

        root.addEventListener('mouseleave', function () {
            overClickable = false;
            glow.classList.remove('is-on');
        });
    }

    /* ---------- Cartas (mensagens do sistema) ---------- */
    var letters = document.querySelectorAll('.letter');
    Array.prototype.forEach.call(letters, function (letter) {
        var dismiss = function () {
            if (letter.classList.contains('is-leaving')) {
                return;
            }
            letter.classList.add('is-leaving');
            window.setTimeout(function () {
                if (letter.parentNode) {
                    letter.parentNode.removeChild(letter);
                }
            }, 450);
        };

        var close = letter.querySelector('.letter__close');
        if (close) {
            close.addEventListener('click', dismiss);
        }

        /* Só as mensagens de sucesso somem sozinhas; erros ficam até serem fechados. */
        if (letter.classList.contains('letter--success')) {
            window.setTimeout(dismiss, 4200);
        }
    });
})();
