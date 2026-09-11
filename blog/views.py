from django.http import HttpResponse
from django.shortcuts import render

def home(request):
    return render(request, "blog/home.html")

def about(request):
    return render(request, "blog/about.html", {"team": "DjangoBlog Team"})

def contact(request):
    return render(request, "blog/contact.html", {"content": "DjangoBlog Team"})