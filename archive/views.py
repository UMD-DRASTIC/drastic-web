import os

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from archive.client import get_default_client

def home(request):
    return redirect('archive:view', path='')

def resource_view(request, id):
    ctx = {"resource": {"id": id, "name": "A test name", "collection":{"name": "data"}}}
    return render(request, 'archive/resource.html', ctx)

def navigate(request, path):

    client     = get_default_client()
    collection = client.get_collection(path if path.startswith("/") else "/{}".format(path))

    collections = []
    resources   = []

    for child in collection.get("children"):
        if child.endswith("/"):
            collections.append(child)
        else:
            resources.append(child)

    collections.sort()
    resources.sort()

    parts = path.split("/")

    def make_collection_dict(c):
        return {
            "name": c,
            "path": "{}{}".format(path, c)
        }

    def make_resource_dict(r):
        name, ext = os.path.splitext(r)
        print ext
        return {
            "name": r,
            "type": ext[1:].upper()
        }

    ctx = {
        'collection': {
            'collection_paths': path.split('/'),
            'collections': [make_collection_dict(c) for c in collections],
            'resources': [make_resource_dict(r) for r in resources],
        }
    }

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
