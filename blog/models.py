from django.db import models
from django.utils.text import slugify
from PIL import Image  # <--- ADICIONADO CONFORME A IMAGEM

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

    tags = models.ManyToManyField(Tag, blank=True, related_name="posts")

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    content = models.TextField()
    status = models.CharField(max_length=10, choices=StatusChoices, default='published')
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True, related_name="posts"
    )
    
    # Campo de imagem de capa
    cover_image = models.ImageField(upload_to="post_covers/", blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # --- MÉTODO SAVE ATUALIZADO CONFORME A IMAGEM ---
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
        
        # Redimensiona a imagem se for maior que 800x800
        if self.cover_image:
            img_path = self.cover_image.path
            img = Image.open(img_path)
            if img.height > 800 or img.width > 800:
                img.thumbnail((800, 800))
                img.save(img_path)

    def __str__(self):  
        return self.title