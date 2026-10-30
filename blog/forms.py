from django import forms
from django.utils.translation import gettext as _, gettext_lazy
from .models import Comment, ContactMessage, Post
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, label=gettext_lazy("Email address"))

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["title", "content", "category", "tags", "status", "house", "cover_image", "video_url"]

        widgets = {
            "content": forms.Textarea(attrs={"rows": 8, "class": "form-control"}),
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "category": forms.Select(attrs={"class": "form-select"}),
            "status": forms.Select(attrs={"class": "form-select"}),
            "house": forms.Select(attrs={"class": "form-select"}),
            "tags": forms.SelectMultiple(attrs={"class": "form-select"}),
            "cover_image": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "video_url": forms.URLInput(attrs={"class": "form-control", "placeholder": gettext_lazy("Enter YouTube video URL")}),
        }

        labels = {
            "title": gettext_lazy("Title"),
            "content": gettext_lazy("Content"),
            "category": gettext_lazy("Category"),
            "tags": gettext_lazy("Tags"),
            "status": gettext_lazy("Status"),
            "house": gettext_lazy("House"),
            "cover_image": gettext_lazy("Cover image"),
            "video_url": gettext_lazy("YouTube video URL"),
        }
        help_texts = {"house": gettext_lazy("Optional. With the magic theme, the page wears this house's colours.")}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Os nomes das opções (rascunho/publicado, casas) vêm do model em inglês: traduz aqui.
        self.fields["status"].choices = [(v, gettext_lazy(l)) for v, l in Post.StatusChoices]
        self.fields["house"].choices = [("", "---------")] + [(v, gettext_lazy(l)) for v, l in Post.HouseChoices]

    def clean_title(self):
        title = self.cleaned_data["title"]
        if len(title) < 5:
            raise forms.ValidationError(_("Title must be at least 5 characters long."))
        return title

    def clean(self):
        cleaned_data = super().clean()
        title = cleaned_data.get("title")
        content = cleaned_data.get("content")
        if title and content and title.lower() in content.lower()[:50]:
            raise forms.ValidationError(_("Don't repeat the title verbatim at the start of the content."))
        return cleaned_data

    def clean_cover_image(self):
        image = self.cleaned_data.get("cover_image")
        if image:
            if image.size > 5 * 1024 * 1024:
                raise forms.ValidationError(_("Image file too large (max 5MB)."))
            valid_extensions = [".jpg", ".jpeg", ".png", ".webp"]
            if not any(image.name.lower().endswith(ext) for ext in valid_extensions):
                raise forms.ValidationError(_("Unsupported file type. Use JPG, PNG, or WEBP."))
        return image


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["text"]
        widgets = {
            "text": forms.Textarea(attrs={"rows": 4, "class": "form-control", "placeholder": gettext_lazy("What did you think?")}),
        }
        labels = {"text": gettext_lazy("Your comment")}
        error_messages = {"text": {"required": gettext_lazy("Write something before posting.")}}


class ContactForm(forms.ModelForm):
    # Campo-isca: pessoas não veem (fica escondido); robôs costumam preencher tudo.
    website = forms.CharField(
        required=False,
        label=gettext_lazy("Leave this field empty"),
        widget=forms.TextInput(attrs={"tabindex": "-1", "autocomplete": "off"}),
    )

    class Meta:
        model = ContactMessage
        fields = ["name", "email", "message"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": gettext_lazy("Your name"), "autocomplete": "name"}),
            "email": forms.EmailInput(attrs={"class": "form-control", "placeholder": "you@example.com", "autocomplete": "email"}),
            "message": forms.Textarea(attrs={"rows": 5, "class": "form-control", "placeholder": gettext_lazy("Anything you'd like to tell me?")}),
        }
        labels = {
            "name": gettext_lazy("Name"),
            "email": gettext_lazy("Email"),
            "message": gettext_lazy("Message (optional)"),
        }
        error_messages = {
            "name": {"required": gettext_lazy("Please tell me your name.")},
            "email": {"required": gettext_lazy("Please add your email so I can reply."), "invalid": gettext_lazy("That email does not look right.")},
        }
