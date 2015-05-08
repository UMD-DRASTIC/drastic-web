from django.shortcuts import render

def home(request):
    return render(request, 'archive/index.html', {})

def search(request):
    query = request.GET.get('q')

    ctx = {
        "q": query
    }
    return render(request, 'archive/search.html', ctx)

def navigate(request):
    return render(request, 'archive/view.html', {})