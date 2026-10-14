"""
URL configuration for config project.
...
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
import debug_toolbar

# --- HANDLER CUSTOMIZADO ---
handler403 = "blog.views.custom_403"

urlpatterns = [
    path("admin/", admin.site.urls),

    # --- ROTAS DE AUTENTICAÇÃO ---
    path("login/", auth_views.LoginView.as_view(template_name="blog/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(next_page="home"), name="logout"),

    # --- ROTAS DE REDEFINIÇÃO DE SENHA (ADICIONADAS CONFORME A IMAGEM) ---
    path("password-reset/", auth_views.PasswordResetView.as_view(template_name="blog/password_reset.html"), name="password_reset"),
    path("password-reset/done/", auth_views.PasswordResetDoneView.as_view(template_name="blog/password_reset_done.html"), name="password_reset_done"),
    path("reset/<uidb64>/<token>/", auth_views.PasswordResetConfirmView.as_view(template_name="blog/password_reset_confirm.html"), name="password_reset_confirm"),
    path("reset/done/", auth_views.PasswordResetCompleteView.as_view(template_name="blog/password_reset_complete.html"), name="password_reset_complete"),
    # -----------------------------------------------------------------------

    # --- ROTAS DO BLOG ---
    path("", include("blog.urls")),

    path("__debug__/", include(debug_toolbar.urls)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)