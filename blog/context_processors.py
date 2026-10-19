from django.conf import settings


def social_links(request):
    """Disponibiliza os links das redes sociais (definidos em settings) para todos os templates."""
    return {"SOCIAL_LINKS": settings.SOCIAL_LINKS}
