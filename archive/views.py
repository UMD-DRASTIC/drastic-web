"""Archive views

Copyright 2015 Archive Analytics Solutions

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""


import collections
import json
import os
from django.http import (
    StreamingHttpResponse,
    Http404
)
from django.core.exceptions import PermissionDenied
from django.shortcuts import (
    render,
    redirect
)
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from archive.forms import (
    CollectionForm,
    CollectionNewForm,
    ResourceForm,
    ResourceNewForm
)

from activity.signals import (
    new_resource_signal,
    new_collection_signal,
    edited_resource_signal,
    edited_collection_signal
)

from indigo.drivers import get_driver
from indigo.models.resource import Resource
from indigo.models.collection import Collection
from indigo.models.group import Group
from indigo.models.search import SearchIndex
from indigo.models.search2 import SearchIndex2
from indigo.models.errors import (
    CollectionConflictError,
    ResourceConflictError
)
from indigo.metadata import (
    get_resource_keys,
    get_collection_keys
)



def notify_agent(resource_id, event=""):
    from nodes.client import choose_client
    client = choose_client()
    client.notify(resource_id, event)
    
    
# TODO: Move this to a helper
def get_extension(name):
    _, ext = os.path.splitext(name)
    if ext:
        return ext[1:].upper()
    return "UNKNOWN"


# noinspection PyUnusedLocal
@login_required()
def home(request):
    return redirect('archive:view', path='')


##############################################################################
# Collection specific view functions
##############################################################################
@login_required()
def resource_view(request, path):
    resource = Resource.find_by_path(path)
    if not resource:
        raise Http404()

    if not resource.user_can(request.user, "read"):
        raise PermissionDenied

    container = Collection.find_by_path(resource.container)

    paths = []
    full = ""
    for p in container.path().split('/'):
        if not p:
            continue
        full = u"{}/{}".format(full, p)
        paths.append((p, full))

    ctx = {
        "resource": resource.to_dict(request.user),
        "container": container,
        "container_path": container.path(),
        "collection_paths": paths
    }
    return render(request, 'archive/resource/view.html', ctx)


@login_required
def new_resource(request, parent):
    if parent == '/':
        parent_collection = Collection.get_root_collection()
    else:
        parent_collection = Collection.find_by_path(parent)
    # Inherits perms from container by default.
    if not parent_collection:
        raise Http404()

    # User must be able to write to this collection
    if not parent_collection.user_can(request.user, "write"):
        raise PermissionDenied

    keys = get_resource_keys()
    mdata = collections.OrderedDict()
    for k in keys:
        mdata[k] = ""
    if not mdata:
        mdata[""] = ""

    read_access, write_access = parent_collection.read_acl()
    initial = {
        'metadata': json.dumps(mdata),
        'read_access': read_access,
        'write_access': write_access
    }

    if request.method == 'POST':
        form = ResourceNewForm(request.POST, files=request.FILES, initial=initial)
        if form.is_valid():
            data = form.cleaned_data
            try:
                blob_id = data['file'].read()
                url = "cassandra://{}".format(blob_id)

                name = data['name']
                metadata = {}

                for k, v in json.loads(data['metadata']):
                    if k in metadata:
                        if isinstance(metadata[k], list):
                            metadata[k].append(v)
                        else:
                            metadata[k] = [metadata[k], v]
                    else:
                        metadata[k] = v

                resource = Resource.create(name=name,
                                           container=parent_collection.path(),
                                           metadata=metadata,
                                           url=url,
                                           size=data['file'].size,
                                           mimetype=data['file'].content_type,
                                           type=get_extension(data['file'].name))
                resource.create_acl(data['read_access'], data['write_access'])
                
                notify_agent(resource.path(), "resource:new")
                messages.add_message(request, messages.INFO,
                                     u"New resource '{}' created" .format(resource.name))

                new_resource_signal.send(None, user=request.user, resource=resource)
            except ResourceConflictError:
                messages.add_message(request, messages.ERROR,
                                     "That name is in use within the current collection")

            return redirect('archive:view', path=parent_collection.path())
    else:
        form = ResourceNewForm(initial=initial)

    ctx = {
        "form": form,
        "container": parent_collection,
        "groups": Group.objects.all()
    }
    return render(request, 'archive/resource/new.html', ctx)


@login_required
def edit_resource(request, path):
    # Requires edit on resource
    resource = Resource.find_by_path(path)
    if not resource:
        raise Http404()

    container = Collection.find_by_path(resource.container)
    if not container:
        raise Http404()

    if not resource.user_can(request.user, "edit"):
        raise PermissionDenied

    if request.method == "POST":
        form = ResourceForm(request.POST)
        if form.is_valid():
            metadata = {}
            for k, v in json.loads(form.cleaned_data['metadata']):
                if k in metadata:
                    if isinstance(metadata[k], list):
                        metadata[k].append(v)
                    else:
                        metadata[k] = [metadata[k], v]
                else:
                    metadata[k] = v

            try:
                data = form.cleaned_data

                resource.update(metadata=metadata)
                resource.create_acl(data['read_access'], data['write_access'])
                
                notify_agent(resource.path(), "resource:edit")
                edited_resource_signal.send(None, user=request.user, resource=resource)

                return redirect('archive:resource_view', path=resource.path())
            except ResourceConflictError:
                messages.add_message(request, messages.ERROR,
                                     "That name is in use withinin the current collection")
    else:
        md = resource.get_metadata()
        metadata = json.dumps(md)
        if not md:
            metadata = '{"":""}'

        read_access, write_access = resource.read_acl()
        initial_data = {'name': resource.name, 'metadata': metadata,
                        'read_access': read_access,
                        'write_access': write_access
                       }
        form = ResourceForm(initial=initial_data)

    ctx = {
        "form": form,
        "resource": resource,
        "container": container,
        "groups": Group.objects.all()
    }

    return render(request, 'archive/resource/edit.html', ctx)


@login_required
def delete_resource(request, path):
    resource = Resource.find_by_path(path)
    if not resource:
        raise Http404

    if not resource.user_can(request.user, "delete"):
        raise PermissionDenied

    container = resource.get_container()
    if request.method == "POST":
        resource.delete()
        notify_agent(resource.path(), "resource:delete")
        messages.add_message(request, messages.INFO,
                             "The resource '{}' has been deleted".format(resource.name))
        return redirect('archive:view', path=container.path())

    # Requires delete on resource
    ctx = {
        "resource": resource,
        "container": container,
    }

    return render(request, 'archive/resource/delete.html', ctx)


##############################################################################
# Collection specific view functions
##############################################################################

@login_required()
def navigate(request, path):
    # client = get_default_client()
    if not path or path == '/':
        collection = Collection.get_root_collection()
    else:
        collection = Collection.find_by_path(path or '/')

    if not collection:
        raise Http404()

    if not collection.user_can(request.user, "read") and not collection.is_root:
        # If the user can't read, then return 404 rather than 403 so that
        # we don't leak information.
        raise Http404()

    paths = []
    full = ""
    for p in collection.path().split('/'):
        if not p:
            continue
        full = u"{}/{}".format(full, p)
        paths.append((p, full))

    def child_collections():
        return collection.get_child_collections()

    def child_resources():
        return collection.get_child_resources()

    children_c = list(child_collections())
    children_c.sort(key=lambda x: x['name'].lower())
    children_r = list(child_resources())
    children_r.sort(key=lambda x: x['name'].lower())
    ctx = {
        'collection': collection.to_dict(request.user),
        'children_c': [c.to_dict(request.user) for c in children_c],
        'children_r': [c.to_dict(request.user) for c in children_r],
        'collection_paths': paths,
        'empty': len(children_c) + len(children_r) == 0,
    }

    return render(request, 'archive/index.html', ctx)


def search(request):
    query = request.GET.get('q')

    ctx = {
        "q": query
    }

    terms = [x.lower() for x in query.split(' ')]
    
    results = SearchIndex2.find(terms, request.user)
    ctx['results'] = results
    ctx['total'] = len(ctx['results'])
    ctx['highlights'] = terms

    return render(request, 'archive/search.html', ctx)


def search2(request):
    query = request.GET.get('q')

    ctx = {
        "q": query
    }

    terms = [x.lower() for x in query.split(' ')]

    ctx['results'] = SearchIndex2.find(terms, request.user)
    ctx['total'] = len(ctx['results'])
    ctx['highlights'] = terms

    return render(request, 'archive/search.html', ctx)


@login_required
def new_collection(request, parent):
    if parent == '/':
        parent_collection = Collection.get_root_collection()
    else:
        parent_collection = Collection.find_by_path(parent)

    if not parent_collection.user_can(request.user, "write"):
        raise PermissionDenied

    keys = get_collection_keys()
    mdata = collections.OrderedDict()
    for k in keys:
        mdata[k] = ""
    if not mdata:
        mdata[""] = ""

    read_access, write_access = parent_collection.read_acl()
    initial = {
        'metadata': json.dumps(mdata),
        "read_access": read_access,
        "write_access": write_access
    }
    form = CollectionNewForm(request.POST or None, initial=initial)
    if request.method == 'POST':
        if form.is_valid():
            data = form.cleaned_data
            try:
                name = data['name']
                parent = parent_collection.path()
                metadata = {}

                for k, v in json.loads(data['metadata']):
                    if k in metadata:
                        if isinstance(metadata[k], list):
                            metadata[k].append(v)
                        else:
                            metadata[k] = [metadata[k], v]
                    else:
                        metadata[k] = v

                collection = Collection.create(name=name,
                                               container=parent,
                                               metadata=metadata)
                collection.create_acl(data['read_access'], data['write_access'])
                messages.add_message(request, messages.INFO,
                                     u"New collection '{}' created" .format(collection.name))

                new_collection_signal.send(None, user=request.user, collection=collection)
                return redirect('archive:view', path=collection.path())
            except CollectionConflictError:
                messages.add_message(request, messages.ERROR,
                                     "That name is in use in the current collection")

    groups = Group.objects.all()
    return render(request, 'archive/new.html', {'form': form, "parent": parent_collection, "groups": groups})


@login_required
def edit_collection(request, path):
    coll = Collection.find_by_path(path)

    if not coll.user_can(request.user, "edit"):
        raise PermissionDenied

    if request.method == "POST":
        form = CollectionForm(request.POST)
        if form.is_valid():
            metadata = {}
            for k, v in json.loads(form.cleaned_data['metadata']):
                if k in metadata:
                    if isinstance(metadata[k], list):
                        metadata[k].append(v)
                    else:
                        metadata[k] = [metadata[k], v]
                else:
                    metadata[k] = v

            try:
                data = form.cleaned_data
                coll.update(metadata=metadata)
                coll.create_acl(data['read_access'], data['write_access'])
                edited_collection_signal.send(None, user=request.user, collection=coll)
                return redirect('archive:view', path=coll.path())
            except CollectionConflictError:
                messages.add_message(request, messages.ERROR,
                                     "That name is in use in the current collection")
    else:
        md = coll.get_metadata()
        metadata = json.dumps(md)
        if not md:
            metadata = '{"":""}'
        read_access, write_access = coll.read_acl()
        initial_data = {'name': coll.name, 'metadata': metadata,
                        'read_access': read_access,
                        'write_access': write_access}
        form = CollectionForm(initial=initial_data)

    groups = Group.objects.all()
    return render(request, 'archive/edit.html', {'form': form, 'collection': coll, 'groups': groups})


@login_required
def delete_collection(request, path):
    coll = Collection.find_by_path(path)

    if not coll.user_can(request.user, "delete"):
        raise PermissionDenied

    if request.method == "POST":
        parent_coll = Collection.find(coll.container)
        if parent_coll:
            parent_path = parent_coll.path()
        else:
            # Just in case
            parent_path = ''
        Collection.delete_all(coll.path())
        messages.add_message(request, messages.INFO,
                             "The collection '{}' has been deleted".format(coll.name))
        return redirect('archive:view', path=parent_path)

    return render(request, 'archive/delete.html', {'collection': coll})


@login_required
def download(request, path):
    """
    Requests for download are redirected to the agent via the agent,
    but for debugging the requests are served directly.

    We will send appropriate user auth to the agent.
    """
    from indigo.models.blob import Blob, BlobPart

    resource = Resource.find_by_path(path)
    if not resource:
        raise Http404

    if not resource.user_can(request.user, "read"):
        raise PermissionDenied

    driver = get_driver(resource.url)

    resp = StreamingHttpResponse(streaming_content=driver.chunk_content(),
                                 content_type=resource.mimetype)
    resp['Content-Disposition'] = 'attachment; filename="{}"'.format(resource.name)

    return resp


@login_required
def preview(request, path):
    """
    Find the preview of the resource with the given ID and deliver it.  This will
    be rendered in the iframe of the resource view page.
    """
    resource = Resource.find_by_path(path)
    if not resource:
        raise Http404

    preview_info = {
        # "type": "image",
        # "url": "http://....."
    }

    return render(request, 'archive/preview.html', {'preview': preview_info})
