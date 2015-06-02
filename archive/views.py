from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

def home(request):
    return redirect('archive:view', path='')

def navigate(request, path):

    parts = path.split('/')

    ctx = {
        'collection': {
            'collection_paths': parts,
            'collections': [],
        }
    }

    if not ctx['collection']['collections']:
        ctx['collection']['collections'] = [
            {"name": "data", "path": "data"},
            {"name": "something", "path": "data/something"},
            {"name": "something-else", "path": "data/something/something-else"},
        ]

    return render(request, 'archive/index.html', ctx)


def search(request):
    query = request.GET.get('q')

    ctx = {
        "q": query
    }
    return render(request, 'archive/search.html', ctx)

@login_required
def new(request):
    return render(request, 'archive/index.html', {})
