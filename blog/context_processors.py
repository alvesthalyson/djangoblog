from django.utils.translation import gettext as _
from django.conf import settings

# Posição e tempos de cada vela do teto (tema "magic").
# x/y: posição (% e px) · h: altura da cera (px) · bd/bt: atraso e duração do flutuar (s)
# fd: atraso da chama (s) · od: atraso ao apagar (s, a da direita apaga primeiro)
# id: atraso ao acender (s, a da esquerda acende primeiro)
CANDLES = [
    {"x": 5, "y": 34, "h": 46, "bd": -1.2, "bt": 6.5, "fd": -0.6, "od": 1.4, "id": 0.0},
    {"x": 16, "y": 12, "h": 60, "bd": -2.6, "bt": 5.8, "fd": -1.1, "od": 1.2, "id": 0.12},
    {"x": 29, "y": 46, "h": 38, "bd": -0.8, "bt": 7.0, "fd": -0.2, "od": 1.0, "id": 0.24},
    {"x": 43, "y": 20, "h": 54, "bd": -3.4, "bt": 6.2, "fd": -1.5, "od": 0.8, "id": 0.36},
    {"x": 57, "y": 52, "h": 42, "bd": -2.0, "bt": 5.5, "fd": -0.9, "od": 0.6, "id": 0.48},
    {"x": 70, "y": 16, "h": 58, "bd": -4.2, "bt": 6.8, "fd": -0.4, "od": 0.4, "id": 0.6},
    {"x": 83, "y": 40, "h": 36, "bd": -1.1, "bt": 6.0, "fd": -1.3, "od": 0.2, "id": 0.72},
    {"x": 94, "y": 24, "h": 50, "bd": -3.0, "bt": 7.2, "fd": -0.7, "od": 0.0, "id": 0.84},
]


def social_links(request):
    """Disponibiliza os links das redes sociais (definidos em settings) para todos os templates."""
    return {"SOCIAL_LINKS": settings.SOCIAL_LINKS}


def site_theme(request):
    """Informa o tema ativo (SITE_THEME) e, no tema "magic", as velas do teto."""
    return {"SITE_THEME": settings.SITE_THEME, "CANDLES": CANDLES}


def js_strings(request):
    """Textos que os scripts do tema "magic" mostram na tela, já traduzidos para o idioma atual.

    Eles chegam ao navegador por um <script type="application/json"> (veja base.html).
    """
    houses = {
        "g": {
            "name": _("Gryffindor"),
            "text": _("Bold, loyal and quick to stand up for others. You would open the door first and think about the hinges later."),
        },
        "s": {
            "name": _("Slytherin"),
            "text": _("Resourceful, driven and a little mysterious. You see what a situation could become and work out how to get there."),
        },
        "h": {
            "name": _("Hufflepuff"),
            "text": _("Patient, fair and generous. You make a place feel like home, and people would follow you for that alone."),
        },
        "r": {
            "name": _("Ravenclaw"),
            "text": _("Curious, inventive and happiest with a good puzzle. You notice the pattern in the carvings before anyone else."),
        },
    }
    quiz = [
        {"q": _("A door appears in the old library wall. What do you do?"), "o": [
            [_("Open it at once, adventure waits for no one."), "g"],
            [_("Study the carvings around it first."), "r"],
            [_("Knock and ask if anyone inside needs help."), "h"],
            [_("Wait and find out who gains from it being opened."), "s"]]},
        {"q": _("What would you most like to be remembered for?"), "o": [
            [_("Doing the brave thing when it was hard."), "g"],
            [_("One idea nobody else had thought of."), "r"],
            [_("Being the friend everyone could count on."), "h"],
            [_("Building something that outlasts you."), "s"]]},
        {"q": _("Pick a place to spend the evening."), "o": [
            [_("A hilltop bonfire under open sky."), "g"],
            [_("A silent tower full of books."), "r"],
            [_("A warm kitchen full of friends."), "h"],
            [_("A lakeside cave lit by green lanterns."), "s"]]},
        {"q": _("A friend is blamed for something they did not do. You…"), "o": [
            [_("Stand up and say so, loudly."), "g"],
            [_("Quietly gather the proof."), "r"],
            [_("Stay at their side, whatever happens."), "h"],
            [_("Make sure the right person hears the truth."), "s"]]},
        {"q": _("Which element feels most like you?"), "o": [
            [_("Fire"), "g"], [_("Air"), "r"], [_("Earth"), "h"], [_("Water"), "s"]]},
    ]
    ui = {
        "sortingHat": _("Sorting Hat"),
        "openQuiz": _("Open the sorting quiz"),
        "openQuizAgain": _("Sorting Hat: you are in %(house)s. Open the quiz again"),
        "question": _("Question %(n)s of %(total)s"),
        "catchSnitch": _("Catch the Golden Snitch"),
        "caughtSnitch": _("You caught the Golden Snitch! +150 points"),
        "dismiss": _("Dismiss message"),
        "lumos": _("Lumos"),
        "nox": _("Nox"),
        "toLight": _("Switch to the light theme"),
        "toDark": _("Switch to the dark theme"),
        "effectsOff": _("Turn effects off"),
        "effectsOn": _("Turn effects on"),
        "musicOn": _("Music: on"),
        "musicOff": _("Music: off"),
    }
    return {"JS_STRINGS": {"houses": houses, "quiz": quiz, "ui": ui}}
