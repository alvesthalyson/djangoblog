from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from .context_processors import CANDLES, site_theme
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


class LayoutTests(TestCase):
    def setUp(self):
        self.user = make_user()

    def test_social_bar_shows_name_and_all_networks(self):
        response = self.client.get(reverse("home"))
        self.assertContains(response, "Thalyson")
        for network in ("Instagram", "Facebook", "TikTok", "LinkedIn"):
            self.assertContains(response, network)

    @override_settings(
        SOCIAL_LINKS=[{"name": "Instagram", "url": "https://example.com/meu-perfil"}]
    )
    def test_social_links_come_from_settings(self):
        response = self.client.get(reverse("home"))
        self.assertContains(response, 'href="https://example.com/meu-perfil"')
        self.assertNotContains(response, "TikTok")
        self.assertContains(response, 'target="_blank"')

    @override_settings(SOCIAL_LINKS=[{"name": "Instagram", "url": "#"}])
    def test_link_without_url_does_not_open_new_tab(self):
        response = self.client.get(reverse("home"))
        self.assertContains(response, '<a href="#">Instagram</a>', html=True)
        self.assertNotContains(response, 'target="_blank"')

    def test_post_without_cover_shows_placeholder(self):
        make_post(self.user, title="Post sem capa")
        response = self.client.get(reverse("home"))
        self.assertContains(response, "No Image")

    def test_categories_section_shows_post_count(self):
        category = Category.objects.create(name="Django")
        make_post(self.user, title="Post com categoria", category=category)
        response = self.client.get(reverse("home"))
        self.assertContains(response, "Django (1)")

    def test_empty_home_invites_first_post(self):
        response = self.client.get(reverse("home"))
        self.assertContains(response, "No posts yet")

    def test_nav_marks_current_page(self):
        response = self.client.get(reverse("about"))
        self.assertContains(response, 'class="nav-link active" href="/about/"')


POST_DATA = {
    "title": "Post criado pelo teste",
    "content": "Conteudo bem diferente do titulo informado.",
    "status": "published",
}


@override_settings(SITE_THEME="magic")
class MagicThemeTests(TestCase):
    def setUp(self):
        self.user = make_user()

    def test_page_declares_the_theme_and_loads_its_assets(self):
        response = self.client.get(reverse("home"))
        self.assertContains(response, 'data-theme="magic"')
        self.assertContains(response, "blog/css/style.css")
        self.assertContains(response, "blog/css/magic.css")
        self.assertContains(response, "blog/js/magic.js")

    def test_starts_in_lumos_mode(self):
        response = self.client.get(reverse("home"))
        self.assertContains(response, 'data-mode="lumos"')

    def test_ceiling_has_eight_candles(self):
        response = self.client.get(reverse("home"))
        self.assertContains(response, 'class="candle-ceiling"')
        self.assertContains(response, 'class="candle"', count=8)

    def test_candle_variables_use_a_dot_as_decimal_separator(self):
        response = self.client.get(reverse("home"))
        self.assertContains(response, "--bd:-1.2s")
        self.assertNotContains(response, "--bd:-1,2s")

    def test_candles_go_out_right_to_left_and_light_left_to_right(self):
        go_out = [candle["od"] for candle in CANDLES]
        light_up = [candle["id"] for candle in CANDLES]
        self.assertEqual(go_out, sorted(go_out, reverse=True))
        self.assertEqual(light_up, sorted(light_up))

    def test_mode_and_effects_toggles_are_present(self):
        response = self.client.get(reverse("home"))
        self.assertContains(response, 'id="mode-toggle"')
        self.assertContains(response, 'id="fx-toggle"')

    def test_success_message_arrives_as_a_letter(self):
        self.client.login(username="alice", password="s3nha-forte-123")
        response = self.client.post(reverse("post_create"), POST_DATA, follow=True)
        self.assertContains(response, "letter letter--success")
        self.assertContains(response, "Post published successfully!")
        self.assertNotContains(response, "alert alert-success")


@override_settings(SITE_THEME="classic")
class ClassicThemeTests(TestCase):
    """O tema bege e marrom continua disponível e sem nada do tema pergaminho."""

    def setUp(self):
        self.user = make_user()

    def test_page_uses_only_the_classic_assets(self):
        response = self.client.get(reverse("home"))
        self.assertContains(response, 'data-theme="classic"')
        self.assertContains(response, "blog/css/style.css")
        self.assertNotContains(response, "blog/css/magic.css")
        self.assertNotContains(response, "blog/js/magic.js")

    def test_page_has_no_magic_elements(self):
        response = self.client.get(reverse("home"))
        for marker in ("candle-ceiling", "mode-toggle", "fx-toggle", "data-mode="):
            self.assertNotContains(response, marker)

    def test_success_message_stays_a_regular_alert(self):
        self.client.login(username="alice", password="s3nha-forte-123")
        response = self.client.post(reverse("post_create"), POST_DATA, follow=True)
        self.assertContains(response, "alert alert-success")
        self.assertNotContains(response, "letter letter--success")

    def test_context_processor_reports_the_active_theme(self):
        self.assertEqual(site_theme(None)["SITE_THEME"], "classic")


class HouseModelAndFormTests(TestCase):
    def setUp(self):
        self.user = make_user()

    def test_post_has_no_house_by_default(self):
        self.assertEqual(make_post(self.user).house, "")

    def test_post_can_belong_to_a_house(self):
        post = make_post(self.user, house="r")
        self.assertEqual(post.get_house_display(), "Ravenclaw")

    def test_form_accepts_each_house_and_none(self):
        for house in ("", "g", "s", "h", "r"):
            form = PostForm(data={**POST_DATA, "house": house})
            self.assertTrue(form.is_valid(), form.errors)

    def test_form_rejects_unknown_house(self):
        form = PostForm(data={**POST_DATA, "house": "x"})
        self.assertFalse(form.is_valid())
        self.assertIn("house", form.errors)

    def test_author_can_choose_a_house_when_publishing(self):
        self.client.login(username="alice", password="s3nha-forte-123")
        self.client.post(reverse("post_create"), {**POST_DATA, "house": "s"})
        self.assertEqual(Post.objects.get(title=POST_DATA["title"]).house, "s")


@override_settings(SITE_THEME="magic")
class HouseMagicThemeTests(TestCase):
    def setUp(self):
        self.user = make_user()

    def test_page_loads_house_assets(self):
        response = self.client.get(reverse("home"))
        self.assertContains(response, "blog/css/houses.css")
        self.assertContains(response, "blog/js/houses.js")

    def test_page_has_hat_quiz_snitch_and_patronus(self):
        response = self.client.get(reverse("home"))
        for marker in (
            'id="house-toggle"', 'id="quiz"', 'id="quiz-wear"',
            'id="snitch-template"', 'id="patronus-template"',
            'id="patronus-toggle"', 'id="snitch-count"',
        ):
            self.assertContains(response, marker)

    def test_quiz_starts_closed(self):
        response = self.client.get(reverse("home"))
        self.assertContains(response, 'id="quiz" hidden')

    def test_card_shows_the_house_of_the_post(self):
        make_post(self.user, title="Post da corvinal", house="r")
        response = self.client.get(reverse("home"))
        self.assertContains(response, "post-card__house")
        self.assertContains(response, "Ravenclaw")

    def test_card_without_house_has_no_house_line(self):
        make_post(self.user, title="Post sem casa")
        response = self.client.get(reverse("home"))
        self.assertNotContains(response, "post-card__house")

    def test_post_page_wears_the_house_colours(self):
        post = make_post(self.user, house="r")
        response = self.client.get(reverse("post_detail", args=[post.slug]))
        self.assertContains(response, 'data-page-house="r"')
        self.assertContains(response, 'data-house="r"')
        self.assertContains(response, "house-ribbon")
        self.assertContains(response, "This post belongs to Ravenclaw")

    def test_post_page_without_house_keeps_the_visitors_theme(self):
        post = make_post(self.user)
        response = self.client.get(reverse("post_detail", args=[post.slug]))
        self.assertNotContains(response, "data-page-house")
        self.assertNotContains(response, "house-ribbon")

    def test_list_page_never_forces_a_house(self):
        make_post(self.user, house="g")
        response = self.client.get(reverse("home"))
        self.assertNotContains(response, "data-page-house")

    def test_post_page_ignores_house_of_a_draft_hidden_from_visitor(self):
        post = make_post(self.user, status="draft", house="g")
        response = self.client.get(reverse("post_detail", args=[post.slug]))
        self.assertEqual(response.status_code, 404)


@override_settings(SITE_THEME="classic")
class HouseClassicThemeTests(TestCase):
    """No tema classic a casa existe nos dados, mas nada do visual das casas aparece."""

    def setUp(self):
        self.user = make_user()

    def test_page_has_none_of_the_house_features(self):
        make_post(self.user, house="g")
        response = self.client.get(reverse("home"))
        for marker in (
            "houses.css", "houses.js", "house-toggle", 'id="quiz"',
            "snitch-template", "patronus-template", "post-card__house",
        ):
            self.assertNotContains(response, marker)

    def test_post_page_has_no_ribbon_or_page_house(self):
        post = make_post(self.user, house="g")
        response = self.client.get(reverse("post_detail", args=[post.slug]))
        self.assertNotContains(response, "house-ribbon")
        self.assertNotContains(response, "data-page-house")
