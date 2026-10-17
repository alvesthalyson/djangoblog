"""
URL configuration for config project.
"""

from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from blog import views as blog_views


# --- HANDLERS DE ERRO PERSONALIZADOS ---
handler403 = "blog.views.custom_403"
handler404 = "blog.views.custom_404"
handler500 = "blog.views.custom_500"


urlpatterns = [
    # Administração
    path("admin/", admin.site.urls),

    # Autenticação
    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="blog/login.html"
        ),
        name="login",
    ),

    path(
        "logout/",
        auth_views.LogoutView.as_view(
            next_page="home"
        ),
        name="logout",
    ),

    # Redefinição de senha
    path(
        "password-reset/",
        auth_views.PasswordResetView.as_view(
            template_name="blog/password_reset.html"
        ),
        name="password_reset",
    ),

    path(
        "password-reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="blog/password_reset_done.html"
        ),
        name="password_reset_done",
    ),

    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="blog/password_reset_confirm.html"
        ),
        name="password_reset_confirm",
    ),

    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="blog/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),

    # Rotas do blog
    path("", include("blog.urls")),
]


if settings.DEBUG:
    # Django Debug Toolbar (só em desenvolvimento)
    import debug_toolbar

    urlpatterns += [path("__debug__/", include(debug_toolbar.urls))]

    # Exibe as imagens enviadas durante o desenvolvimento
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )

    # Exibe o frontend 404 mesmo com DEBUG=True.
    # Esta rota precisa permanecer por último.
    urlpatterns += [
        re_path(
            r"^.*$",
            blog_views.custom_404,
            name="custom_404",
        ),
    ]