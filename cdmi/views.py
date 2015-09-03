from collections import OrderedDict
import os.path

from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes
)

from cdmi.capabilities import SYSTEM_CAPABILITIES
from cdmi.storage import CDMIDataAccessObject

from indigo.models.resource import Resource
from indigo.models.collection import Collection


def capabilities(request, path):

    body = OrderedDict()
    if path in ['', '/']:
        body['capabilities'] = SYSTEM_CAPABILITIES._asdict()
    elif path.startswith('/dataobject'):
        d = CDMIDataAccessObject({}).dataObjectCapabilities._asdict()
        body['capabilities'] = d
    elif path.startswith('/container'):
        d = CDMIDataAccessObject({}).containerCapabilities._asdict()
        body['capabilities'] = d

    return JsonResponse(body)

def crud_id(request, id):
    if request.method == "GET":
        resource = Resource.find_by_id(id)
        if resource is not None:
            return redirect('archive:download', id=resource.id)
        else:
            return HttpResponse("404 Not Found")
    else:
        return HttpResponse("Not implemented yet")


@api_view(['GET'])
@authentication_classes((SessionAuthentication, BasicAuthentication))
@permission_classes((IsAuthenticated,))
def crud(request, path):
    print request.user.is_authenticated()
    print request.user
    print request.auth
    content = {
        'user': unicode(request.user),  # `django.contrib.auth.User` instance.
        'auth': unicode(request.auth),  # None
    }
    return HttpResponse(content)
#     username = request.POST['username']
#     password = request.POST['password']
#     print username, password
    if request.method == "GET":
        # Add a leading / to have a real path
        path = "/{}".format(path)
        # In CDMI standard a container is defined by the / at the end
        is_container = path.endswith('/')
        if is_container:
            return read_container(request, path[:-1])
        else:
            return read_dataObject(request, path)
    elif request.method == 'PUT':
        # Add a leading / to have a real path
        path = "/{}".format(path)
        print path
        # In CDMI standard a container is defined by the / at the end
        is_container = path.endswith('/')
        if is_container:
            return create_container(request, path[:-1])
        else:
            return create_dataObject(request, path)
    else:
        return HttpResponse("Not implemented yet")

def read_container(request, path):
    return HttpResponse("Read Container {}".format(path))

def create_container(request, path):
    return HttpResponse("Create Container {}".format(path))

def read_dataObject(request, path):
    if request.META.has_key("X-CDMI-Specification-Version"):
        return read_dataObject_CDMI(request, path)
    
    resource = Resource.find_by_path(path)
    return redirect('archive:download', id=resource.id)
    
def read_dataObject_CDMI(request, path):
    return HttpResponse("Read dataObject CDMI mode {}".format(path))

def create_dataObject(request, path):
    if request.META.has_key("X-CDMI-Specification-Version"):
        return create_dataObject_CDMI(request, path)
    
    coll_name = os.path.dirname(path)
    resc_name = os.path.basename(path)
    
    container = Collection.find_by_path(coll_name)
    blob_id = HttpRequest.read()
    url = "cassandra://{}".format(blob_id)
    print container
    print url
#     resource = Resource.create(name=resc_name,
#                                container=container.id,
#                                metadata={},
#                                read_access=[],
#                                write_access=[],
#                                delete_access=[],
#                                edit_access=[],
#                                url=url,
#                                size=0,
#                                mimetype=request.META['CONTENT_TYPE'],
#                                file_name=resc_name,
#                                type=get_extension(file_name))

    notify_agent(resource.id, "resource:new")
    return HttpResponse("Create dataObject  {}".format(path))
    
def create_dataObject_CDMI(request, path):
    return HttpResponse("Create dataObject CDMI mode {}".format(path))