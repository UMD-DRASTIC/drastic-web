import json
import os
import requests

from django.conf import settings
from django.http import (StreamingHttpResponse, HttpResponse,
                         Http404, HttpResponseForbidden)
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages


from archive.client import get_default_client
from archive.forms import CollectionForm, ResourceForm
from users.authentication import administrator_required

from indigo.models.resource import Resource
from indigo.models.collection import Collection
from indigo.models.group import Group
from indigo.models.search import SearchIndex
from indigo.models.errors import UniqueException


@login_required()
def home(request):
    return redirect('archive:view', path='')

##############################################################################
# Collection specific view functions
##############################################################################

@login_required()
def resource_view(request, id):

    resource = Resource.find_by_id(id)
    if not resource:
        raise Http404();

    if not resource.user_can(request.user, "read"):
        return HttpResponseForbidden()

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
        return HttpResponseForbidden()

    initial = {
        'metadata':'{"":""}',
        'read_access': container.read_access,
        'write_access': container.write_access,
        'edit_access': container.edit_access,
        'delete_access': container.delete_access,
    }

    form = ResourceForm(request.POST or None, initial=initial )
    if request.method == 'POST':
        if form.is_valid():
            data = form.cleaned_data
            try:
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
                                           edit_access=data['edit_access'])
                SearchIndex.index(resource, ['name', 'metadata'])
                messages.add_message(request, messages.INFO,
                                     u"New resource '{}' created" .format(resource.name))
            except UniqueException:
                messages.add_message(request, messages.ERROR,
                                     "That name is in use within the current collection")


            return redirect('archive:view', path=container.path)

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
        return HttpResponseForbidden()

    if request.method == "POST":
        form = ResourceForm(request.POST)
        if form.is_valid():
            # TODO: Check for duplicates
            metadata = {}
            for k, v in json.loads(form.cleaned_data['metadata']):
                metadata[k] = v

            try:
                data = form.cleaned_data
                resource.update(name=data['name'],
                            metadata=metadata,
                            read_access=data['read_access'],
                            write_access=data['write_access'],
                            delete_access=data['delete_access'],
                            edit_access=data['edit_access'])

                SearchIndex.reset(resource.id)
                SearchIndex.index(resource, ['name', 'metadata'])

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
    # Requires delete on resource
    ctx = {
        "resource": "",
        "container": "",
    }

    return render(request, 'archive/resource/delete.html', ctx)


##############################################################################
# Collection specific view functions
##############################################################################

@login_required()
def navigate(request, path):

    client     = get_default_client()
    collection = Collection.find_by_path(path or '/')

    if not collection:
        raise Http404()

    if not collection.user_can(request.user, "read"):
        return HttpResponseForbidden()

    paths = []
    full = ""
    for p in collection.path.split('/'):
        if not p:
            continue
        full = u"{}/{}".format(full, p)
        paths.append( (p,full,) )

    def child_collections():
        res = []
        for coll in collection.get_child_collections():
            if not collection.user_can(request.user, "read"):
                continue
            res.append(coll)
        return res

    def child_resources():
        result = []
        for resource in collection.get_child_resources():
            if not resource.user_can(request.user, "read"):
                continue
            result.append(resource)
        return result


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
        return HttpResponseForbidden()

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
        return HttpResponseForbidden()

    if request.method == "POST":
        form = CollectionForm(request.POST)
        if form.is_valid():
            # TODO: Check for duplicates
            metadata = {}
            for k, v in json.loads(form.cleaned_data['metadata']):
                metadata[k] = v

            try:
                data = form.cleaned_data
                print data
                coll.update(name=data['name'],
                            metadata=metadata,
                            read_access=data['read_access'],
                            write_access=data['write_access'],
                            delete_access=data['delete_access'],
                            edit_access=data['edit_access'])

                SearchIndex.reset(coll.id)
                SearchIndex.index(coll, ['name', 'metadata'])

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
        return HttpResponseForbidden()

    if request.method == "POST":
        SearchIndex.reset(coll.id)
        # TODO: Mark collection as inactive...
        messages.add_message(request, messages.INFO,
                                     "The collection '{}' has been deleted".format(coll.name))
        return redirect('archive:view', path='')

    return render(request, 'archive/delete.html', {'collection': coll})


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



