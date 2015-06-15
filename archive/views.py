import json
import os
import requests

from django.conf import settings
from django.http import StreamingHttpResponse, HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages


from archive.client import get_default_client
from archive.forms import CollectionForm
from users.authentication import administrator_required

from indigo.models import Collection
from indigo.models.errors import UniqueException


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
    #collection = client.get_collection(path if path.startswith("/") else "/{}".format(path))

    collection = Collection.find_by_path(path or '/')

    paths = []
    full = ""
    for p in collection.path.split('/'):
        if not p:
            continue
        full = u"{}/{}".format(full, p)
        paths.append( (p,full,) )

    ctx = {
        'collection': collection.to_dict(),
        'child_collections': [c.to_dict() for c in collection.get_child_collections()],
        'child_collections_count': collection.get_child_collection_count(),
        'collection_paths': paths
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
def new(request, parent):
    if not parent:
        parent_collection = Collection.get_root_collection()
    else:
        parent_collection = Collection.find_by_id(parent)

    form = CollectionForm(request.POST or None, initial={'metadata':'{"":""}'})
    if request.method == 'POST':
        if form.is_valid():
            data = form.cleaned_data
            try:
                name = data['name']
                parent = parent_collection.id
                metadata = {}
                for k, v in json.loads(data['metadata']):
                    metadata[k] = v
                collection = Collection.create(name=name, parent=parent, metadata=metadata)
                messages.add_message(request, messages.INFO,
                                     u"New collection '{}' created" .format(collection.name))
                return redirect('archive:view', path=parent_collection.path)
            except UniqueException:
                messages.add_message(request, messages.ERROR,
                                     "That name is in use in the current collection")
    return render(request, 'archive/new.html', {'form': form, "parent": parent_collection})

@login_required
def edit(request, id):
    coll = Collection.find_by_id(id)
    if request.method == "POST":
        form = CollectionForm(request.POST)
        if form.is_valid():
            # TODO: Check for duplicates
            metadata = {}
            for k, v in json.loads(form.cleaned_data['metadata']):
                metadata[k] = v

            try:
                coll.update(name=form.cleaned_data['name'], metadata=metadata)
                return redirect('archive:view', path=coll.path)
            except UniqueException:
                messages.add_message(request, messages.ERROR,
                                     "That name is in use in the current collection")
    else:
        metadata = json.dumps(coll.metadata)
        if not coll.metadata:
            metadata = '{"":""}'
        form = CollectionForm(initial={'name':coll.name, 'metadata': metadata})

    return render(request, 'archive/edit.html', {'form': form, 'collection': coll})

@login_required
def delete(request, id):
    return render(request, 'archive/delete.html', {})


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



