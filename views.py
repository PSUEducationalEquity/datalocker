from django.shortcuts import render

def index(request):
    """
    Displays the application home page
    """
    return render(request, 'datalocker/index.html', {})
