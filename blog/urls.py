from django.urls import path
# Importe todas as views necessárias de uma vez
from .views import (PostListView, PostDetailView, PostCreateView,PostUpdateView, PostDeleteView, about, contact)

urlpatterns = [
    # Rota inicial (usando PostListView conforme a imagem)
    path("", PostListView.as_view(), name="home"),
    
    # Rotas de Posts
    path("posts/new/", PostCreateView.as_view(), name="post_create"),
    path("posts/<slug:slug>/edit/", PostUpdateView.as_view(), name="post_edit"),
    path("posts/<slug:slug>/delete/", PostDeleteView.as_view(), name="post_delete"),
    path("posts/<slug:slug>/", PostDetailView.as_view(), name="post_detail"),
    
    # Rotas institucionais (mantidas como funções)
    path("about/", about, name="about"),
    path("contact/", contact, name="contact"),
]