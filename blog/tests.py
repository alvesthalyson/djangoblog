from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from .forms import PostForm
from .models import Category, Post, Tag


def make_user(username="alice", password="s3nha-forte-123"):
    return User.objects.create_user(username=username, password=password)


def make_post(author, title="Meu primeiro post", status="published", **kwargs):
    return Post.objects.create(
        title=title,
        content="Conteudo de teste suficientemente diferente do titulo.",
        author=author,
        status=status,
        **kwargs,
    )


class PostModelTests(TestCase):
    def setUp(self):
        self.user = make_user()

    def test_slug_is_generated_from_title(self):
        post = make_post(self.user, title="Hello Django World")
        self.assertEqual(post.slug, "hello-django-world")

    def test_slug_is_unique_for_duplicate_titles(self):
        first = make_post(self.user, title="Mesmo titulo")
        second = make_post(self.user, title="Mesmo titulo")
        self.assertNotEqual(first.slug, second.slug)
        self.assertEqual(second.slug, "mesmo-titulo-1")

    def test_default_status_is_published(self):
        post = Post.objects.create(title="Titulo", content="x", author=self.user)
        self.assertEqual(post.status, "published")

    def test_str_returns_title(self):
        self.assertEqual(str(make_post(self.user, title="Titulo X")), "Titulo X")

    def test_category_and_tag_str(self):
        self.assertEqual(str(Category.objects.create(name="Python")), "Python")
        self.assertEqual(str(Tag.objects.create(name="django")), "django")


class PostFormTests(TestCase):
    def _form(self, **overrides):
        data = {
            "title": "Um titulo valido",
            "content": "Um conteudo que nao repete o titulo no comeco.",
            "status": "published",
        }
        data.update(overrides)
        return PostForm(data=data)

    def test_valid_form(self):
        self.assertTrue(self._form().is_valid())

    def test_title_too_short(self):
        form = self._form(title="abc")
        self.assertFalse(form.is_valid())
        self.assertIn("title", form.errors)

    def test_title_repeated_at_start_of_content(self):
        form = self._form(title="Repetido aqui", content="Repetido aqui e mais texto")
        self.assertFalse(form.is_valid())

    def test_rejects_unsupported_image_type(self):
        gif = SimpleUploadedFile("capa.gif", b"GIF89a", content_type="image/gif")
        form = PostForm(
            data={
                "title": "Um titulo valido",
                "content": "Conteudo diferente do titulo.",
                "status": "published",
            },
            files={"cover_image": gif},
        )
        self.assertFalse(form.is_valid())


class PublicViewsTests(TestCase):
    def setUp(self):
        self.user = make_user()
        self.published = make_post(self.user, title="Post publicado")
        self.draft = make_post(self.user, title="Post rascunho", status="draft")

    def test_home_lists_only_published_posts(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Post publicado")
        self.assertNotContains(response, "Post rascunho")

    def test_home_is_paginated(self):
        for i in range(10):
            make_post(self.user, title=f"Paginado numero {i}")
        response = self.client.get(reverse("home"))
        self.assertEqual(len(response.context["object_list"]), 6)
        self.assertTrue(response.context["is_paginated"])

    def test_published_detail_is_public(self):
        response = self.client.get(reverse("post_detail", args=[self.published.slug]))
        self.assertEqual(response.status_code, 200)

    def test_draft_hidden_from_anonymous_users(self):
        response = self.client.get(reverse("post_detail", args=[self.draft.slug]))
        self.assertEqual(response.status_code, 404)

    def test_draft_hidden_from_other_users(self):
        make_user("bob")
        self.client.login(username="bob", password="s3nha-forte-123")
        response = self.client.get(reverse("post_detail", args=[self.draft.slug]))
        self.assertEqual(response.status_code, 404)

    def test_draft_visible_to_author(self):
        self.client.login(username="alice", password="s3nha-forte-123")
        response = self.client.get(reverse("post_detail", args=[self.draft.slug]))
        self.assertEqual(response.status_code, 200)

    def test_static_pages(self):
        for name in ("about", "contact"):
            self.assertEqual(self.client.get(reverse(name)).status_code, 200)


class AuthTests(TestCase):
    def test_register_creates_user_and_logs_in(self):
        response = self.client.post(
            reverse("register"),
            {
                "username": "novo",
                "email": "novo@example.com",
                "password1": "s3nha-forte-123",
                "password2": "s3nha-forte-123",
            },
        )
        self.assertRedirects(response, "/")
        self.assertTrue(User.objects.filter(username="novo").exists())
        self.assertIn("_auth_user_id", self.client.session)

    def test_register_requires_email(self):
        response = self.client.post(
            reverse("register"),
            {
                "username": "sememail",
                "password1": "s3nha-forte-123",
                "password2": "s3nha-forte-123",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="sememail").exists())

    def test_login_and_logout(self):
        make_user()
        response = self.client.post(
            reverse("login"), {"username": "alice", "password": "s3nha-forte-123"}
        )
        self.assertRedirects(response, reverse("home"))
        self.client.post(reverse("logout"))
        self.assertNotIn("_auth_user_id", self.client.session)


class PostCrudPermissionTests(TestCase):
    def setUp(self):
        self.author = make_user("alice")
        self.other = make_user("bob")
        self.post = make_post(self.author, title="Post da alice")

    def test_create_requires_login(self):
        response = self.client.get(reverse("post_create"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)

    def test_create_sets_current_user_as_author(self):
        self.client.login(username="alice", password="s3nha-forte-123")
        response = self.client.post(
            reverse("post_create"),
            {
                "title": "Post criado pelo teste",
                "content": "Conteudo bem diferente do titulo informado.",
                "status": "published",
            },
        )
        self.assertEqual(response.status_code, 302)
        created = Post.objects.get(title="Post criado pelo teste")
        self.assertEqual(created.author, self.author)

    def test_author_can_edit(self):
        self.client.login(username="alice", password="s3nha-forte-123")
        response = self.client.post(
            reverse("post_edit", args=[self.post.slug]),
            {
                "title": "Titulo editado",
                "content": "Conteudo editado e diferente do titulo.",
                "status": "published",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.post.refresh_from_db()
        self.assertEqual(self.post.title, "Titulo editado")

    def test_other_user_cannot_edit(self):
        self.client.login(username="bob", password="s3nha-forte-123")
        response = self.client.get(reverse("post_edit", args=[self.post.slug]))
        self.assertEqual(response.status_code, 403)

    def test_other_user_cannot_delete(self):
        self.client.login(username="bob", password="s3nha-forte-123")
        response = self.client.post(reverse("post_delete", args=[self.post.slug]))
        self.assertEqual(response.status_code, 403)
        self.assertTrue(Post.objects.filter(pk=self.post.pk).exists())

    def test_author_can_delete(self):
        self.client.login(username="alice", password="s3nha-forte-123")
        response = self.client.post(reverse("post_delete", args=[self.post.slug]))
        self.assertRedirects(response, reverse("home"))
        self.assertFalse(Post.objects.filter(pk=self.post.pk).exists())

    def test_my_posts_requires_login(self):
        response = self.client.get(reverse("my_posts"))
        self.assertEqual(response.status_code, 302)

    def test_my_posts_shows_only_own_posts(self):
        make_post(self.other, title="Post do bob")
        self.client.login(username="alice", password="s3nha-forte-123")
        response = self.client.get(reverse("my_posts"))
        self.assertContains(response, "Post da alice")
        self.assertNotContains(response, "Post do bob")
