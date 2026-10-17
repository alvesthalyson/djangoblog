from django.urls import path
from .views import (
    PostListView, 
    PostDetailView, 
    PostCreateView, 
    PostUpdateView, 
    PostDeleteView, 
    RegisterView, 
    MyPostsView,
    about, 
    contact
)

urlpatterns = [
    # Rota inicial (Lista de Posts)
    path("", PostListView.as_view(), name="home"),
    
    # Rota "Meus Posts" (apenas posts do usuário logado)
    path("my-posts/", MyPostsView.as_view(), name="my_posts"),
    
    # Rota de Registro de Usuário
    path("register/", RegisterView.as_view(), name="register"),
    
    # Rotas de Posts (CRUD)
    path("posts/new/", PostCreateView.as_view(), name="post_create"),
    path("posts/<slug:slug>/edit/", PostUpdateView.as_view(), name="post_edit"),
    path("posts/<slug:slug>/delete/", PostDeleteView.as_view(), name="post_delete"),
    path("posts/<slug:slug>/", PostDetailView.as_view(), name="post_detail"),
    
    # Rotas institucionais (mantidas como funções)
    path("about/", about, name="about"),
    path("contact/", contact, name="contact"),
]