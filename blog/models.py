from django.db import models
from django.utils.text import slugify
from django.conf import settings
from django.urls import reverse
from PIL import Image
from embed_video.fields import EmbedVideoField


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Post(models.Model):
    StatusChoices = [('draft', 'Draft'), ('published', 'Published'), ]

    # Casa do post: no tema "magic" a página vira as cores dela (veja houses.css)
    HouseChoices = [
        ('g', 'Gryffindor'),
        ('s', 'Slytherin'),
        ('h', 'Hufflepuff'),
        ('r', 'Ravenclaw'),
    ]

    tags = models.ManyToManyField(Tag, blank=True, related_name="posts")

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    video_url = EmbedVideoField(blank=True, null=True, verbose_name="YouTube Video URL")
    content = models.TextField()
    status = models.CharField(max_length=10, choices=StatusChoices, default='published')
    house = models.CharField(max_length=1, choices=HouseChoices, blank=True, default='')
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True, related_name="posts"
    )

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="posts"
    )

    # Cover image field
    cover_image = models.ImageField(upload_to="post_covers/", blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_absolute_url(self):
        return reverse("post_detail", kwargs={"slug": self.slug})

    def save(self, *args, **kwargs):
        # Generate a unique slug (only when the post has none yet)
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Post.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug

        super().save(*args, **kwargs)

        # Resize the image if it is larger than 800x800
        if self.cover_image:
            img_path = self.cover_image.path
            img = Image.open(img_path)
            if img.height > 800 or img.width > 800:
                img.thumbnail((800, 800))
                img.save(img_path)

    def __str__(self):
        return self.title


class Comment(models.Model):
    """Comentário de um usuário logado em um post."""

    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="comments"
    )
    text = models.TextField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.author} em {self.post}"


class ContactMessage(models.Model):
    """Mensagem enviada pelo formulário da página Contact (lida no painel admin)."""

    name = models.CharField(max_length=80)
    email = models.EmailField()
    message = models.TextField(max_length=1000, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} <{self.email}>"
