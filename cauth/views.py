from django.shortcuts import render

def login_view(request):
    return render(request, 'login.html', {})

def logout_view(request):
    return render(request, 'login.html', {})