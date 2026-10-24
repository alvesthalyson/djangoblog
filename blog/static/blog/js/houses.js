/*
 * DjangoBlog — casas, pomo de ouro e Patrono (tema "magic").
 *
 * - Teste do Chapéu Seletor: 5 perguntas, a casa fica salva no navegador.
 * - Tema por casa: o atributo data-house do <html> troca as cores (houses.css).
 *   A casa do post aberto (data-page-house) vale sobre a escolhida no teste.
 * - Pomo de ouro: voa pela tela; clicar nele conta um ponto.
 * - Patrono: um animal de luz atravessa a tela ao publicar um post
 *   ou ao clicar em "Expecto Patronum".
 *
 * Tudo respeita "Turn effects off" e "reduzir movimento" do sistema.
 */
(function () {
    'use strict';

    var root = document.documentElement;
    if (root.getAttribute('data-theme') !== 'magic') {
        return;
    }

    var reduceMotion = !!(window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches);

    var HOUSES = {
        g: {
            name: 'Gryffindor', color: '#B02A2A',
            text: 'Bold, loyal and quick to stand up for others. You would open the door first and think about the hinges later.'
        },
        s: {
            name: 'Slytherin', color: '#1F5A42',
            text: 'Resourceful, driven and a little mysterious. You see what a situation could become and work out how to get there.'
        },
        h: {
            name: 'Hufflepuff', color: '#E0A81E',
            text: 'Patient, fair and generous. You make a place feel like home, and people would follow you for that alone.'
        },
        r: {
            name: 'Ravenclaw', color: '#2C5AA8',
            text: 'Curious, inventive and happiest with a good puzzle. You notice the pattern in the carvings before anyone else.'
        }
    };

    /* Cada resposta soma um ponto para uma casa (g, s, h ou r). */
    var QUIZ = [
        { q: 'A door appears in the old library wall. What do you do?', o: [
            ['Open it at once, adventure waits for no one.', 'g'],
            ['Study the carvings around it first.', 'r'],
            ['Knock and ask if anyone inside needs help.', 'h'],
            ['Wait and find out who gains from it being opened.', 's']] },
        { q: 'What would you most like to be remembered for?', o: [
            ['Doing the brave thing when it was hard.', 'g'],
            ['One idea nobody else had thought of.', 'r'],
            ['Being the friend everyone could count on.', 'h'],
            ['Building something that outlasts you.', 's']] },
        { q: 'Pick a place to spend the evening.', o: [
            ['A hilltop bonfire under open sky.', 'g'],
            ['A silent tower full of books.', 'r'],
            ['A warm kitchen full of friends.', 'h'],
            ['A lakeside cave lit by green lanterns.', 's']] },
        { q: 'A friend is blamed for something they did not do. You…', o: [
            ['Stand up and say so, loudly.', 'g'],
            ['Quietly gather the proof.', 'r'],
            ['Stay at their side, whatever happens.', 'h'],
            ['Make sure the right person hears the truth.', 's']] },
        { q: 'Which element feels most like you?', o: [
            ['Fire', 'g'], ['Air', 'r'], ['Earth', 'h'], ['Water', 's']] }
    ];

    function load(key) {
        try {
            return window.localStorage.getItem(key);
        } catch (e) {
            return null;
        }
    }

    function save(key, value) {
        try {
            window.localStorage.setItem(key, value);
        } catch (e) {
            /* armazenamento bloqueado: vale só até recarregar */
        }
    }

    function effectsOn() {
        return root.getAttribute('data-fx') !== 'off' && !reduceMotion;
    }

    function validHouse(key) {
        return Object.prototype.hasOwnProperty.call(HOUSES, key) ? key : null;
    }

    var pageHouse = validHouse(root.getAttribute('data-page-house'));
    var myHouse = validHouse(load('djangoblog-house'));

    /* ---------- Cartas (mensagens curtas, como as do magic.js) ---------- */
    function showLetter(text) {
        var box = document.querySelector('.letters');
        if (!box) {
            box = document.createElement('div');
            box.className = 'letters';
            box.setAttribute('role', 'status');
            box.setAttribute('aria-live', 'polite');
            document.body.appendChild(box);
        }

        var letter = document.createElement('div');
        letter.className = 'letter letter--success';

        var seal = document.createElement('span');
        seal.className = 'letter__seal';
        seal.setAttribute('aria-hidden', 'true');

        var p = document.createElement('p');
        p.className = 'letter__text';
        p.textContent = text;

        var close = document.createElement('button');
        close.type = 'button';
        close.className = 'letter__close';
        close.setAttribute('aria-label', 'Dismiss message');
        close.innerHTML = '&times;';

        letter.appendChild(seal);
        letter.appendChild(p);
        letter.appendChild(close);
        box.appendChild(letter);

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
        close.addEventListener('click', dismiss);
        window.setTimeout(dismiss, 4200);
    }

    /* ---------- Troca de tema: crachá no menu e onda de cor ---------- */
    var toggle = document.getElementById('house-toggle');

    function paintHouseButton() {
        if (!toggle) {
            return;
        }
        var hat = toggle.querySelector('[data-house-hat]');
        var crestBox = toggle.querySelector('[data-house-crest]');
        var label = toggle.querySelector('[data-house-label]');
        if (myHouse) {
            var crest = crestBox.querySelector('.crest');
            if (crest) {
                crest.setAttribute('data-h', myHouse);
            }
            hat.hidden = true;
            crestBox.hidden = false;
            label.textContent = HOUSES[myHouse].name;
            toggle.setAttribute('aria-label', 'Sorting Hat: you are in ' + HOUSES[myHouse].name + '. Open the quiz again');
        } else {
            hat.hidden = false;
            crestBox.hidden = true;
            label.textContent = 'Sorting Hat';
            toggle.setAttribute('aria-label', 'Open the sorting quiz');
        }
    }

    function applyHouse() {
        var visible = pageHouse || myHouse;
        if (visible) {
            root.setAttribute('data-house', visible);
        } else {
            root.removeAttribute('data-house');
        }
        paintHouseButton();
    }

    function wipe(houseKey) {
        if (!effectsOn()) {
            return;
        }
        var old = document.querySelector('.house-wipe');
        if (old && old.parentNode) {
            old.parentNode.removeChild(old);
        }
        var layer = document.createElement('div');
        layer.className = 'house-wipe';
        layer.setAttribute('aria-hidden', 'true');
        layer.style.setProperty('--wipe', HOUSES[houseKey].color);
        document.body.appendChild(layer);
        var remove = function () {
            if (layer.parentNode) {
                layer.parentNode.removeChild(layer);
            }
        };
        layer.addEventListener('animationend', remove);
        window.setTimeout(remove, 1500);
    }

    applyHouse();

    /* Ao abrir um post de outra casa, a página "veste" as cores dele com uma onda de cor. */
    if (pageHouse && pageHouse !== myHouse) {
        wipe(pageHouse);
    }

    /* ---------- Teste do Chapéu Seletor ---------- */
    var quiz = document.getElementById('quiz');
    var questionView = document.getElementById('quiz-question-view');
    var resultView = document.getElementById('quiz-result-view');
    var progress = document.getElementById('quiz-progress');
    var title = document.getElementById('quiz-title');
    var options = document.getElementById('quiz-options');
    var answers = [];
    var result = null;

    function tally(list) {
        var count = { g: 0, s: 0, h: 0, r: 0 };
        list.forEach(function (key) {
            count[key] += 1;
        });
        var max = Math.max(count.g, count.s, count.h, count.r);
        /* Empate: vale a casa que apareceu primeiro entre as respostas. */
        for (var i = 0; i < list.length; i += 1) {
            if (count[list[i]] === max) {
                return list[i];
            }
        }
        return 'g';
    }

    function showQuestion() {
        var step = QUIZ[answers.length];
        progress.textContent = 'Question ' + (answers.length + 1) + ' of ' + QUIZ.length;
        title.textContent = step.q;
        options.textContent = '';
        step.o.forEach(function (option, index) {
            var button = document.createElement('button');
            button.type = 'button';
            button.className = 'quiz__option';
            button.setAttribute('data-index', String(index));
            button.textContent = option[0];
            options.appendChild(button);
        });
        /* Reinicia a animação de entrada de cada pergunta */
        questionView.style.animation = 'none';
        void questionView.offsetWidth;
        questionView.style.animation = '';
        var first = options.querySelector('.quiz__option');
        if (first && !quiz.hidden) {
            first.focus();
        }
    }

    function showResult() {
        result = tally(answers);
        var house = HOUSES[result];
        questionView.hidden = true;
        resultView.hidden = false;
        quiz.classList.add('quiz--done');
        document.getElementById('quiz-crest').querySelector('.crest').setAttribute('data-h', result);
        document.getElementById('quiz-house').textContent = house.name + '!';
        document.getElementById('quiz-text').textContent = house.text;
        document.getElementById('quiz-wear').focus();
    }

    function startQuiz() {
        answers = [];
        result = null;
        quiz.classList.remove('quiz--done');
        questionView.hidden = false;
        resultView.hidden = true;
        showQuestion();
    }

    var lastFocus = null;

    function openQuiz() {
        lastFocus = document.activeElement;
        quiz.hidden = false;
        document.body.classList.add('quiz-open');
        startQuiz();
    }

    function closeQuiz() {
        quiz.hidden = true;
        document.body.classList.remove('quiz-open');
        if (lastFocus && lastFocus.focus) {
            lastFocus.focus();
        }
    }

    if (quiz && toggle) {
        toggle.addEventListener('click', openQuiz);
        document.getElementById('quiz-close').addEventListener('click', closeQuiz);
        document.getElementById('quiz-retry').addEventListener('click', startQuiz);

        quiz.addEventListener('click', function (event) {
            if (event.target === quiz) {
                closeQuiz();
            }
        });

        options.addEventListener('click', function (event) {
            var button = event.target.closest ? event.target.closest('.quiz__option') : null;
            if (!button) {
                return;
            }
            var index = Number(button.getAttribute('data-index'));
            answers.push(QUIZ[answers.length].o[index][1]);
            if (answers.length >= QUIZ.length) {
                showResult();
            } else {
                showQuestion();
            }
        });

        document.getElementById('quiz-wear').addEventListener('click', function () {
            myHouse = result;
            save('djangoblog-house', myHouse);
            closeQuiz();
            applyHouse();
            wipe(myHouse);
        });

        /* Esc fecha; Tab fica dentro da janela */
        document.addEventListener('keydown', function (event) {
            if (quiz.hidden) {
                return;
            }
            if (event.key === 'Escape') {
                closeQuiz();
                return;
            }
            if (event.key !== 'Tab') {
                return;
            }
            var focusable = Array.prototype.filter.call(
                quiz.querySelectorAll('button'),
                function (el) { return el.offsetParent !== null; }
            );
            if (!focusable.length) {
                return;
            }
            var first = focusable[0];
            var last = focusable[focusable.length - 1];
            if (event.shiftKey && document.activeElement === first) {
                event.preventDefault();
                last.focus();
            } else if (!event.shiftKey && document.activeElement === last) {
                event.preventDefault();
                first.focus();
            }
        });
    }

    /* ---------- Patrono ---------- */
    var patronusTimer = null;

    function castPatronus() {
        var template = document.getElementById('patronus-template');
        if (!template || !effectsOn()) {
            return;
        }
        clearPatronus();

        var dim = document.createElement('div');
        dim.className = 'patdim';
        dim.setAttribute('aria-hidden', 'true');

        var animal = document.createElement('div');
        animal.className = 'patronus';
        animal.setAttribute('aria-hidden', 'true');
        var leap = document.createElement('span');
        leap.className = 'patronus__leap';
        leap.appendChild(template.content.cloneNode(true));
        animal.appendChild(leap);

        document.body.appendChild(dim);
        document.body.appendChild(animal);
        patronusTimer = window.setTimeout(clearPatronus, 7200);
    }

    function clearPatronus() {
        window.clearTimeout(patronusTimer);
        Array.prototype.forEach.call(document.querySelectorAll('.patdim, .patronus'), function (el) {
            if (el.parentNode) {
                el.parentNode.removeChild(el);
            }
        });
    }

    var patronusButton = document.getElementById('patronus-toggle');
    if (patronusButton) {
        patronusButton.addEventListener('click', castPatronus);
    }

    /* Ao publicar um post (mensagem de sucesso na carta), o Patrono atravessa a tela. */
    if (document.querySelector('.letter--success')) {
        window.setTimeout(castPatronus, 600);
    }

    /* ---------- Pomo de ouro ---------- */
    var counter = document.getElementById('snitch-count');
    var caught = parseInt(load('djangoblog-snitches') || '0', 10) || 0;
    var snitchTimer = null;

    function paintCounter() {
        if (counter) {
            counter.textContent = String(caught);
        }
    }
    paintCounter();

    function releaseSnitch() {
        var template = document.getElementById('snitch-template');
        if (!template || document.querySelector('.snitch')) {
            return;
        }
        var button = document.createElement('button');
        button.type = 'button';
        button.className = 'snitch';
        button.setAttribute('aria-label', 'Catch the Golden Snitch');
        var inner = document.createElement('span');
        inner.className = 'snitch__in';
        inner.appendChild(template.content.cloneNode(true));
        button.appendChild(inner);

        button.addEventListener('click', function () {
            if (button.parentNode) {
                button.parentNode.removeChild(button);
            }
            caught += 1;
            save('djangoblog-snitches', String(caught));
            paintCounter();
            showLetter('You caught the Golden Snitch! +150 points');
            window.clearTimeout(snitchTimer);
            snitchTimer = window.setTimeout(releaseSnitch, 7000);
        });

        document.body.appendChild(button);
    }

    releaseSnitch();
})();
