import os
import requests

from django.conf import settings
from django.http import StreamingHttpResponse, HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from archive.client import get_default_client

def home(request):
    return redirect('archive:view', path='')

def resource_view(request, path):
    ctx = {"resource": {"id": id, "name": "A test name", "collection":{"name": "data"}}}

    client     = get_default_client()
    resource   = client.get_resource_info("/" + path)

    # Strip the leading / from the parent url
    if resource['parentURI'].startswith("/"):
        resource['parentURI'] = resource['parentURI'][1:]
    if resource['parentURI'] and not resource['parentURI'].endswith("/"):
        resource['parentURI'] = resource['parentURI'] + "/"
    resource['name'] = path.split('/')[-1]
    resource['path'] = path
    return render(request, 'archive/resource.html', {"resource": resource})

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
        return {
            "name": r,
            "type": ext[1:].upper(),
            "path": "{}{}".format(path, r)
        }


    ctx = {
        'collection': {
            'collection_paths': [p for p in path.split('/') if p],
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

@login_required
def download(request, path):
    """
    Requests for download are redirected to the agent via the agent,
    but for debugging the requests are served directly.

    We will send appropriate user auth to the agent.
    """

    # Permission checks

    client     = get_default_client()
    resource   = client.get_resource_info("/" + path)

    # We have size and mimetype from the resource info, then we want to
    # either:
    #   - Redirect to the appropriate agent URL
    #   - Stream the response ourselves, but only in debug

    def get_content_debug():
        yield client.get_resource_content("/" + path)

    if settings.DEBUG:
        resp = StreamingHttpResponse(streaming_content=get_content_debug(),
                                     content_type=resource.get('mimetype', 'application/octect-stream'))
        resp['Content-Disposition'] = 'attachment; filename="{}"'.format(path.split('/')[-1])

        return resp

    # TODO: Set the response in such a way that nginx can correctly redirect to the agent to do
    # the appropriate work of returning the file.

    return ""



