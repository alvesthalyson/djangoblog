from django.shortcuts import render
from .models import Post, Category, Tag

# --- IMPORTS ADICIONADOS ---
from .forms import PostForm  # Importa o formulário personalizado que criamos

# Imports necessários para as Classes
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

# --- Views Baseadas em Classes ---

class PostListView(ListView):
    model = Post
    template_name = "blog/post_list.html"
    context_object_name = "page_obj" 
    paginate_by = 6

    def get_queryset(self):
        # Filtra apenas posts publicados e ordena do mais recente
        return Post.objects.filter(status="published").order_by("-created_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Adiciona categorias e tags ao contexto
        context["categories"] = Category.objects.all()
        context["tags"] = Tag.objects.all()
        return context

class PostDetailView(DetailView):
    model = Post
    template_name = "blog/post_detail.html"
    context_object_name = "post"

    def get_queryset(self):
        # Garante que apenas posts publicados sejam acessíveis
        return Post.objects.filter(status="published")

# --- Classes Atualizadas para usar o PostForm ---

class PostCreateView(CreateView):
    model = Post
    form_class = PostForm  # <--- ALTERADO: substitui 'fields = [...]'
    template_name = "blog/post_form.html"

    def get_success_url(self):
        return reverse_lazy("post_detail", kwargs={"slug": self.object.slug})

class PostUpdateView(UpdateView):
    model = Post
    form_class = PostForm  # <--- ALTERADO: substitui 'fields = [...]'
    template_name = "blog/post_form.html" 

    def get_success_url(self):
        return reverse_lazy("post_detail", kwargs={"slug": self.object.slug})

class PostDeleteView(DeleteView):
    model = Post
    template_name = "blog/post_confirm_delete.html"
    success_url = reverse_lazy("home") 

# --- Views Baseadas em Funções (Mantidas para about e contact) ---

def home(request):
    categories = Category.objects.all()
    tags = Tag.objects.all()
    return render(request, "blog/home.html", {"categories": categories, "tags": tags})

def about(request):
    return render(request, "blog/about.html", {"team": "DjangoBlog Team"})

def contact(request):
    return render(request, "blog/contact.html", {"content": "DjangoBlog Team"})