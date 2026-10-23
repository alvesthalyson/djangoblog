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
