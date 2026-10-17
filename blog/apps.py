from django.apps import AppConfig


class BlogConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'blog'

    def ready(self):
        # Registra os signals (ex.: apagar a imagem de capa ao deletar um post)
        import blog.signals  # noqa: F401
