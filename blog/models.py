from django.db import models
from django.utils.text import slugify
from django.conf import settings
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


# APAGUE A CLASSE POST QUE ESTAVA AQUI (a que só tinha video_url)


class Post(models.Model):
    StatusChoices = [('draft', 'Draft'), ('published', 'Published'), ]

    tags = models.ManyToManyField(Tag, blank=True, related_name="posts")

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    
    # ADICIONE O CAMPO VIDEO_URL AQUI
    video_url = EmbedVideoField(blank=True, null=True, verbose_name="YouTube Video URL")
    
    # (Você já tinha um campo chamado 'video' na sua classe original, 
    # então recomendo manter apenas o 'video_url' que acabamos de criar e apagar o antigo 'video')
    
    content = models.TextField()
    status = models.CharField(max_length=10, choices=StatusChoices, default='published')
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