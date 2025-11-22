from django.shortcuts import render

def home_view(request):
    """Homepage view"""
    return render(request, 'homepage/home.html')
