from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied
from django.views.decorators.http import require_POST
from .models import Post, Category, Tag, Comment

from .forms import PostForm, RegisterForm, CommentForm, ContactForm
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages

from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.db import models
from django.db.models import Count

# --- Views Baseadas em Classes ---

class PostListView(ListView):
    model = Post
    template_name = "blog/post_list.html"
    paginate_by = 6

    def get_queryset(self):
        return (
            Post.objects.filter(status="published")
            .annotate(comment_count=Count("comments"))
            .order_by("-created_at")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.all()
        context["tags"] = Tag.objects.all()
        return context

class PostDetailView(DetailView):
    model = Post
    template_name = "blog/post_detail.html"
    context_object_name = "post"

    def get_queryset(self):
        # Posts publicados são públicos; rascunhos só aparecem para o autor.
        queryset = Post.objects.filter(status="published")
        if self.request.user.is_authenticated:
            queryset = Post.objects.filter(
                models.Q(status="published") | models.Q(author=self.request.user)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # No tema "magic", a página do post veste as cores da casa dele (se tiver uma)
        context["page_house"] = self.object.house
        context["page_house_name"] = self.object.get_house_display() if self.object.house else ""
        context["comments"] = self.object.comments.select_related("author")
        context.setdefault("comment_form", CommentForm())
        return context

    def post(self, request, *args, **kwargs):
        """Recebe um novo comentário (só usuários logados)."""
        self.object = self.get_object()
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path())
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = self.object
            comment.author = request.user
            comment.save()
            messages.success(request, "Comment posted!")
            return redirect(f"{self.object.get_absolute_url()}#comments")
        context = self.get_context_data(object=self.object, comment_form=form)
        return self.render_to_response(context)

class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = "blog/post_form.html"
    login_url = "login"

    def form_valid(self, form):
        form.instance.author = self.request.user
        messages.success(self.request, "Post published successfully!")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("post_detail", kwargs={"slug": self.object.slug})

class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = "blog/post_form.html"
    login_url = "login"

    def test_func(self):
        return self.get_object().author == self.request.user

    def get_success_url(self):
        return reverse_lazy("post_detail", kwargs={"slug": self.object.slug})

class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    template_name = "blog/post_confirm_delete.html"
    login_url = "login"
    success_url = reverse_lazy("home")

    def test_func(self):
        return self.get_object().author == self.request.user

class MyPostsView(LoginRequiredMixin, ListView):
    model = Post
    template_name = "blog/my_posts.html"
    paginate_by = 6
    login_url = "login"

    def get_queryset(self):
        return (
            Post.objects.filter(author=self.request.user)
            .annotate(comment_count=Count("comments"))
            .order_by("-created_at")
        )

class RegisterView(CreateView):
    form_class = RegisterForm
    template_name = "blog/register.html"
    success_url = "/"

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        return response

# --- Views Baseadas em Funções ---

@require_POST
def comment_delete(request, pk):
    """Apaga um comentário: só o autor dele ou o dono do post."""
    if not request.user.is_authenticated:
        return redirect_to_login(request.get_full_path())
    comment = get_object_or_404(Comment.objects.select_related("post"), pk=pk)
    if request.user not in (comment.author, comment.post.author):
        raise PermissionDenied
    post = comment.post
    comment.delete()
    messages.success(request, "Comment deleted.")
    return redirect(f"{post.get_absolute_url()}#comments")

def about(request):
    return render(request, "blog/about.html", {})

def contact(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            # Campo-isca preenchido = robô: finge sucesso e não guarda nada.
            if not form.cleaned_data.get("website"):
                form.save()
            messages.success(request, "Thanks! Your message was sent.")
            return redirect("contact")
    else:
        initial = {}
        if request.user.is_authenticated:
            initial = {"name": request.user.get_username(), "email": request.user.email}
        form = ContactForm(initial=initial)
    return render(request, "blog/contact.html", {"form": form})

# --- Handlers de erro personalizados ---
def custom_403(request, exception=None):
    return render(request, "blog/403.html", status=403)

def custom_404(request, exception=None):
    return render(request, "404.html", status=404)

def custom_500(request):
    return render(request, "500.html", status=500)
