# ecommerce/views.py
from django.shortcuts import render

# Home page view
def index(request):
    return render(request, "index.html")

# Contact page view
def contact(request):
    return render(request, "contact.html")

# About page view
def about(request):
    return render(request, "about.html")

def base(request):
    return render(request, 'base.html')
