import collections
import json
import os
import requests

from django.conf import settings
from django.http import (StreamingHttpResponse, HttpResponse,
                         Http404)
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages


from archive.client import get_default_client
from archive.forms import CollectionForm, ResourceForm
from users.authentication import administrator_required

from activity.signals import (new_resource_signal,
                              new_collection_signal,
                              edited_resource_signal,
                              edited_collection_signal)

from indigo.drivers import get_driver
from indigo.models.resource import Resource
from indigo.models.collection import Collection
from indigo.models.group import Group
from indigo.models.search import SearchIndex
from indigo.models.errors import UniqueException
from indigo.metadata import get_resource_keys, get_collection_keys

# TODO: Move this to a helper
def get_extension(name):
    _, ext = os.path.splitext(name)
    if ext:
        return ext[1:].upper()
    return "UNKNOWN"

@login_required()
def home(request):
    return redirect('archive:view', path='')

def notify_agent(resource_id, event=""):
    from nodes.client import choose_client
    client = choose_client()
    client.notify(resource_id, event)

##############################################################################
# Collection specific view functions
##############################################################################

@login_required()
def resource_view(request, id):

    resource = Resource.find_by_id(id)
    if not resource:
        raise Http404();

    if not resource.user_can(request.user, "read"):
        raise PermissionDenied

    container = Collection.find_by_id(resource.container)

    ctx = {
        "resource": resource.to_dict(request.user),
        "container": container
    }
    return render(request, 'archive/resource/view.html', ctx)

@login_required
def new_resource(request, container):
    # Inherits perms from container by default.
    container = Collection.find_by_id(container)
    if not container:
        raise Http404()

    # User must be able to write to this collection
    if not container.user_can(request.user, "write"):
        raise PermissionDenied

    keys = get_resource_keys()
    mdata = collections.OrderedDict()
    for k in keys:
        mdata[k] = ""
    if not mdata:
        mdata[""] = ""

    initial = {
        'metadata': json.dumps(mdata),
        'read_access': container.read_access,
        'write_access': container.write_access,
        'edit_access': container.edit_access,
        'delete_access': container.delete_access,
    }


    if request.method == 'POST':
        form = ResourceForm(request.POST, files=request.FILES, initial=initial )
        if form.is_valid():
            data = form.cleaned_data
            try:
                blob_id = data['file'].read()
                url = "cassandra://{}".format(blob_id)

                name = data['name']
                metadata = {}
                for k, v in json.loads(data['metadata']):
                    metadata[k] = v
                resource = Resource.create(name=name,
                                           container=container.id,
                                           metadata=metadata,
                                           read_access=data['read_access'],
                                           write_access=data['write_access'],
                                           delete_access=data['delete_access'],
                                           edit_access=data['edit_access'],
                                           url=url,
                                           size=data['file'].size,
                                           mimetype=data['file'].content_type,
                                           file_name=data['file'].name,
                                           type=get_extension(data['file'].name))

                notify_agent(resource.id, "resource:new")
                SearchIndex.index(resource, ['name', 'metadata'])
                messages.add_message(request, messages.INFO,
                                     u"New resource '{}' created" .format(resource.name))

                new_resource_signal.send(None, user=request.user, resource=resource)
            except UniqueException:
                messages.add_message(request, messages.ERROR,
                                     "That name is in use within the current collection")

            return redirect('archive:view', path=container.path)
    else:
        form = ResourceForm( initial=initial )

    ctx = {
        "form": form,
        "container": container,
        "groups": Group.objects.all()
    }
    return render(request, 'archive/resource/new.html', ctx)

@login_required
def edit_resource(request, id):
    # Requires edit on resource
    resource = Resource.find_by_id(id)
    if not resource:
        raise Http404()

    container = Collection.find_by_id(resource.container)
    if not container:
        raise Http404()

    if not resource.user_can(request.user, "edit"):
        raise PermissionDenied

    if request.method == "POST":
        form = ResourceForm(request.POST, files=request.FILES)
        if form.is_valid():
            # TODO: Check for duplicates
            metadata = {}
            for k, v in json.loads(form.cleaned_data['metadata']):
                metadata[k] = v

            try:
                data = form.cleaned_data

                blob_id = data['file'].read()
                url = "cassandra://{}".format(blob_id)

                resource.update(name=data['name'],
                            metadata=metadata,
                            read_access=data['read_access'],
                            write_access=data['write_access'],
                            delete_access=data['delete_access'],
                            edit_access=data['edit_access'],
                            url=url,
                            size=data['file'].size,
                            mimetype=data['file'].content_type,
                            file_name=data['file'].name,
                            type=get_extension(data['file'].name) )

                notify_agent(resource.id, "resource:edit")
                SearchIndex.reset(resource.id)
                SearchIndex.index(resource, ['name', 'metadata'])

                edited_resource_signal.send(None, user=request.user, resource=resource)

                return redirect('archive:resource_view', id=resource.id)
            except UniqueException:
                messages.add_message(request, messages.ERROR,
                                     "That name is in use withinin the current collection")
    else:
        metadata = json.dumps(resource.metadata)
        if not resource.metadata:
            metadata = '{"":""}'

        initial_data = {'name':resource.name, 'metadata': metadata,
            'read_access': resource.read_access,
            'write_access': resource.write_access,
            'edit_access': resource.edit_access,
            'delete_access': resource.delete_access}
        form = ResourceForm(initial=initial_data)


    ctx = {
        "form": form,
        "resource": resource,
        "container": container,
        "groups": Group.objects.all()
    }

    return render(request, 'archive/resource/edit.html', ctx)

@login_required
def delete_resource(request, id):
    resource = Resource.find_by_id(id)
    if not resource:
        raise Http404

    if not resource.user_can(request.user, "delete"):
        raise PermissionDenied

    # TODO: Make sure the GET request warns the user and then the
    # POST request can actually delete the resource.

    # TODO: Make resource deletion a soft delete.

    # Requires delete on resource
    ctx = {
        "resource": "",
        "container": "",
    }

    notify_agent(resource.id, "resource:delete")
    return render(request, 'archive/resource/delete.html', ctx)


##############################################################################
# Collection specific view functions
##############################################################################

@login_required()
def navigate(request, path):

    #client     = get_default_client()
    collection = Collection.find_by_path(path or '/')

    if not collection:
        raise Http404()

    if not collection.user_can(request.user, "read") and not collection.is_root:
        # If the user can't read, then return 404 rather than 403 so that
        # we don't leak information.
        raise Http404()

    paths = []
    full = ""
    for p in collection.path.split('/'):
        if not p:
            continue
        full = u"{}/{}".format(full, p)
        paths.append( (p,full,) )

    def child_collections():
        return collection.get_child_collections()

    def child_resources():
        return collection.get_child_resources()


    ctx = {
        'collection': collection.to_dict(request.user),
        'child_collections': [c.to_dict(request.user) for c in child_collections()],
        'child_resources': [r.to_dict(request.user) for r in child_resources()],
        'collection_paths': paths
    }

    return render(request, 'archive/index.html', ctx)


def search(request):
    query = request.GET.get('q')

    ctx = {
        "q": query
    }

    terms = [x.lower() for x in query.split(' ')]

    ctx['results'] = SearchIndex.find(terms, request.user)
    ctx['total'] = len(ctx['results'])
    ctx['highlights'] = terms

    return render(request, 'archive/search.html', ctx)

@login_required
def new_collection(request, parent):
    if not parent:
        parent_collection = Collection.get_root_collection()
    else:
        parent_collection = Collection.find_by_id(parent)

    if not parent_collection.user_can(request.user, "write"):
        raise PermissionDenied

    keys = get_collection_keys()
    mdata = collections.OrderedDict()
    for k in keys:
        mdata[k] = ""
    if not mdata:
        mdata[""] = ""


    initial = {
        'metadata': json.dumps(mdata),
        "read_access": parent_collection.read_access,
        "write_access": parent_collection.write_access,
        "edit_access": parent_collection.edit_access,
        "delete_access": parent_collection.delete_access,
    }
    form = CollectionForm(request.POST or None, initial=initial)
    if request.method == 'POST':
        if form.is_valid():
            data = form.cleaned_data
            try:
                name = data['name']
                parent = parent_collection.id
                metadata = {}
                for k, v in json.loads(data['metadata']):
                    metadata[k] = v
                collection = Collection.create(name=name,
                                               parent=parent,
                                               metadata=metadata,
                                               read_access=data['read_access'],
                                               write_access=data['write_access'],
                                               delete_access=data['delete_access'],
                                               edit_access=data['edit_access'])
                SearchIndex.index(collection, ['name', 'metadata'])
                messages.add_message(request, messages.INFO,
                                     u"New collection '{}' created" .format(collection.name))

                new_collection_signal.send(None, user=request.user, collection=collection)
                return redirect('archive:view', path=collection.path)
            except UniqueException:
                messages.add_message(request, messages.ERROR,
                                     "That name is in use in the current collection")

    groups = Group.objects.all()
    return render(request, 'archive/new.html', {'form': form, "parent": parent_collection, "groups": groups})

@login_required
def edit_collection(request, id):
    coll = Collection.find_by_id(id)

    if not coll.user_can(request.user, "edit"):
        raise PermissionDenied

    if request.method == "POST":
        form = CollectionForm(request.POST)
        if form.is_valid():
            # TODO: Check for duplicates
            metadata = {}
            for k, v in json.loads(form.cleaned_data['metadata']):
                metadata[k] = v
            try:
                data = form.cleaned_data
                coll.update(name=data['name'],
                            metadata=metadata,
                            read_access=data['read_access'],
                            write_access=data['write_access'],
                            delete_access=data['delete_access'],
                            edit_access=data['edit_access'])

                SearchIndex.reset(coll.id)
                SearchIndex.index(coll, ['name', 'metadata'])

                edited_collection_signal.send(None, user=request.user, collection=coll)

                return redirect('archive:view', path=coll.path)
            except UniqueException:
                messages.add_message(request, messages.ERROR,
                                     "That name is in use in the current collection")
    else:
        metadata = json.dumps(coll.metadata)
        if not coll.metadata:
            metadata = '{"":""}'

        initial_data = {'name':coll.name, 'metadata': metadata,
            'read_access': coll.read_access,
            'write_access': coll.write_access,
            'edit_access': coll.edit_access,
            'delete_access': coll.delete_access}
        form = CollectionForm(initial=initial_data)

    groups = Group.objects.all()
    return render(request, 'archive/edit.html', {'form': form, 'collection': coll, 'groups': groups})

@login_required
def delete_collection(request, id):
    coll = Collection.find_by_id(id)

    if not coll.user_can(request.user, "delete"):
        raise PermissionDenied

    if request.method == "POST":
        SearchIndex.reset(coll.id)
        # TODO: Mark collection as inactive...
        messages.add_message(request, messages.INFO,
                                     "The collection '{}' has been deleted".format(coll.name))
        return redirect('archive:view', path='')

    return render(request, 'archive/delete.html', {'collection': coll})


@login_required
def download(request, id):
    """
    Requests for download are redirected to the agent via the agent,
    but for debugging the requests are served directly.

    We will send appropriate user auth to the agent.
    """
    from indigo.models.blob import Blob, BlobPart

    resource = Resource.find_by_id(id)
    if not resource:
        raise Http404

    if not resource.user_can(request.user, "read"):
        raise PermissionDenied

    print resource.url
    driver = get_driver(resource.url)

    resp = StreamingHttpResponse(streaming_content=driver.chunk_content(),
                                 content_type=resource.mimetype)
    resp['Content-Disposition'] = 'attachment; filename="{}"'.format(resource.file_name)

    return resp
