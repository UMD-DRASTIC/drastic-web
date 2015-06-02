from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

def home(request):
    return redirect('archive:view', path='')

def resource_view(request, id):
    ctx = {"resource": {"id": id, "name": "A test name", "collection":{"name": "data"}}}
    return render(request, 'archive/resource.html', ctx)

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
        ctx['collection']['resources'] = [
            {"name": "Some data file", "type": "XLS", "id": "X"},
            {"name": "A CSV file", "type": "CSV", "id": "Y"},
            {"name": "An XML file", "type": "XML", "id": "Z"},
        ]

    return render(request, 'archive/index.html', ctx)


def search(request):
    query = request.GET.get('q')

    ctx = {
        "q": query
    }

    ctx['results'] = {}
    if query:
        ctx['results']['collections'] = [
            {"name": "something", "path": "data/something"},
        ]
        ctx['results']['resources'] = [
            {"name": "A CSV file", "type": "CSV", "id": "Y"},
            {"name": "An XML file", "type": "XML", "id": "Z"},
        ]

    return render(request, 'archive/search.html', ctx)

@login_required
def new(request):
    return render(request, 'archive/index.html', {})
