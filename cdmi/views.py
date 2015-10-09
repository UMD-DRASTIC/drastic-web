""""CDMI views

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

from collections import OrderedDict
import base64
import mimetypes
import hashlib
from cStringIO import StringIO
import zipfile
import os
import json
import time

from django.shortcuts import redirect
from django.http import JsonResponse
from django.http import HttpResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.utils.translation import ugettext_lazy as _
from rest_framework.status import (
    HTTP_201_CREATED,
    HTTP_202_ACCEPTED,
    HTTP_204_NO_CONTENT,
    HTTP_400_BAD_REQUEST,
    HTTP_403_FORBIDDEN,
    HTTP_404_NOT_FOUND,
    HTTP_409_CONFLICT,
    HTTP_412_PRECONDITION_FAILED,
)
from rest_framework.renderers import (
    BaseRenderer,
    JSONRenderer
)
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.reverse import reverse_lazy
from rest_framework.authentication import (
    BasicAuthentication,
    exceptions
)

from rest_framework import HTTP_HEADER_ENCODING
from rest_framework.permissions import IsAuthenticated

from cdmi.capabilities import SYSTEM_CAPABILITIES
from cdmi.storage import CDMIDataAccessObject
from archive.uploader import CassandraUploadedFile
from indigo.drivers import get_driver
from indigo.models.resource import Resource
from indigo.models.collection import Collection
from indigo.models.blob import Blob
from indigo.models.blob import BlobPart
from indigo.models.user import User

from indigo.util import split
from indigo.util_archive import (
    path_exists,
    is_resource,
    is_collection
)
from indigo.models.errors import (
    CollectionConflictError,
    ResourceConflictError,
    NoSuchCollectionError,
    NoSuchResourceError,
    NoWriteAccessError,
)

# List of supported version (In order so the first to be picked up is the most
# recent one
CDMI_SUPPORTED_VERSION = ["1.1", "1.0.2"]

# Possible sections of the CDMI request body where the data object content
# may be specified
POSSIBLE_DATA_OBJECT_LOCATIONS = [
    'deserialize',
    'serialize',
    'copy',
    'move',
    'reference',
    'deserializevalue',
    'value'
]

# TODO: Move this to a helper
def get_extension(name):
    _, ext = os.path.splitext(name)
    if ext:
        return ext[1:].upper()
    return "UNKNOWN"


def check_cdmi_version(request):
    """Check the HTTP request header to see what version the client is
    supporting. Return the highest version supported by both the client and
    the server, "" if no match is found or no version provided by the client"""
    spec_version_raw = request.META.get("HTTP_X_CDMI_SPECIFICATION_VERSION", "")
    versions_list = [el.strip() for el in spec_version_raw.split(",")]
    for version in CDMI_SUPPORTED_VERSION:
        if version in versions_list:
            return version
    else:
        return ""


def capabilities(request, path):
    """Read all fields from an existing capability object.

    TODO: This part of the specification isn't implemented properly according
    to the specification, capabilities should be a special kind of containers
    with ObjectID"""
    cdmi_version = check_cdmi_version(request)
    if not cdmi_version:
        return HttpResponse(status=HTTP_400_BAD_REQUEST)
    body = OrderedDict()
    if path in ['', '/']:
        body['capabilities'] = SYSTEM_CAPABILITIES._asdict()
        body["objectType"] = "application/cdmi-capability"
        body["objectID"] = "00007E7F00104BE66AB53A9572F9F51E"
        body["objectName"] = "cdmi_capabilities/"
        body["parentURI"] = "/"
        body["parentID"] = "00007E7F0010128E42D87EE34F5A6560"
        body["childrenrange"] = "0-3"
        body["children"] = ["domain/", "container/", "dataobject/", "queue/"]
    elif path.startswith('/dataobject'):
        d = CDMIDataAccessObject({}).dataObjectCapabilities._asdict()
        body['capabilities'] = d
        body["objectType"] = "application/cdmi-capability"
        body["objectID"] = "00007E7F00104BE66AB53A9572F9F51F"
        body["objectName"] = "dataobject/"
        body["parentURI"] = "/"
        body["parentID"] = "00007E7F00104BE66AB53A9572F9F51FE"
        body["childrenrange"] = "0"
        body["children"] = []
    elif path.startswith('/container'):
        d = CDMIDataAccessObject({}).containerCapabilities._asdict()
        body['capabilities'] = d
        body["objectType"] = "application/cdmi-capability"
        body["objectID"] = "00007E7F00104BE66AB53A9572F9F51A"
        body["objectName"] = "container/"
        body["parentURI"] = "/"
        body["parentID"] = "00007E7F00104BE66AB53A9572F9F51E"
        body["childrenrange"] = "0"
        body["children"] = []
    return JsonResponse(body)



class CDMIContainerRenderer(JSONRenderer):
    """
    Renderer which serializes CDMI container to JSON.
    """
    media_type = 'application/cdmi-container'
    format = 'json'


class CDMIObjectRenderer(JSONRenderer):
    """
    Renderer which serializes CDMI container to JSON.
    """
    media_type = 'application/cdmi-object'
    format = 'json'


class OctetStreamRenderer(BaseRenderer):

    media_type = 'application/octet-stream'
    format = 'bin'

    def render(self, data, media_type=None, renderer_context=None):
        #return data.encode(self.charset)
        return data


class CassandraAuthentication(BasicAuthentication):
    www_authenticate_realm = 'Indigo'

    def authenticate_credentials(self, userid, password):
        """
        Authenticate the userid and password against username and password.
        """
        user = User.find(userid)
        if user is None or not user.is_active():
            raise exceptions.AuthenticationFailed(_('User inactive or deleted.'))
        if not user.authenticate(password):
            raise exceptions.AuthenticationFailed(_('Invalid username/password.'))
        return (user, None)


class CDMIView(APIView):
    authentication_classes = (CassandraAuthentication,)
    renderer_classes = (CDMIContainerRenderer, CDMIObjectRenderer,
                        JSONRenderer, OctetStreamRenderer)
    permission_classes = (IsAuthenticated,)

    def __init__(self, **kwargs):
        super(CDMIView, self).__init__(**kwargs)
        cfg = settings.CDMI_SERVER
        self.api_root = cfg["endpoint"]
        #self.api_root = reverse_lazy('api_cdmi', args=path, request=request)

    def _get_genericBodyFields(self, obj, is_container):
        body = OrderedDict()
        path = obj.path()
        if is_container:
            # Container
            # Mandatory objectType
            body['objectType'] = "application/cdmi-container"
            # Mandatory capabilitiesURI
            if path != '/':
                sPath = path + '/'
            else:
                sPath = path
            body['capabilitiesURI'] = ('{0}/cdmi_capabilities/container{1}'
                                       ''.format(self.api_root, sPath)
                                       )
        else:
            # Data object
            # Mandatory objectType
            body['objectType'] = "application/cdmi-object"
            # Mandatory capabilitiesURI
            body['capabilitiesURI'] = ('{0}/cdmi_capabilities/dataobject{1}'
                                       ''.format(self.api_root, path)
                                       )
        # Mandatory objectID
        objectID = obj.id
        body['objectID'] = objectID#base64.b16encode(objectID)
        # Set objectName and parentURI
        objectNameStart = path[:-1].rfind('/') + 1
        body['objectName'] = path[objectNameStart:]
        if objectNameStart:
            parentPath = obj.container
            if parentPath == '/':
                body['parentURI'] = parentPath
            else:
                body['parentURI'] = parentPath + '/'
            parent = Collection.find_by_path(parentPath)
            parentID = parent.id
            body['parentID'] = parentID #base64.b16encode(parentID)
        #body['owner'] = self.database.get_owner_path(path)
        # TODO: add Mandatory domain
        body['domainURI'] = ('{0}/cdmi_domains/indigo/'.format(self.api_root))
        # Populate metadata
        body['metadata'] = obj.get_metadata()
#         # Update with transient/operational/user metadata
#         body['metadata'].update(self.database.get_metadata(username,
#                                                            storagePath,
#                                                            inherited=True
#                                                            )
#                                 )
        # Update with ACL metadata
        try:
            acl_dict = obj.get_acl_metadata()
            body['metadata'].update(acl_dict)

#             replicas = self.database.get_replicas_dataObject(username,
#                                                              storagePath)
#             body['metadata'].update({
#                 'cdmi_replicas': len(replicas)
#             })
        except AttributeError:
            # ACLs unsupported by storage backend
            pass
        return body



    @csrf_exempt
    def get(self, request, path='/', format=None):
        self.user = request.user
        print self.user

        # Add a '/' at the beginning
        path = "/{}".format(path)
        # In CDMI standard a container is defined by the / at the end
        is_container = path.endswith('/')
        if is_container:
            if path == '/': # root
                return self.read_container(path)
            else:
                return self.read_container(path[:-1])
        else:
            return self.read_dataObject(path)

    @csrf_exempt
    def put(self, request, path='/', format=None):
        self.user = request.user
        print self.user

        # Add a '/' at the beginning
        path = "/{}".format(path)
        # In CDMI standard a container is defined by the / at the end
        is_container = path.endswith('/')
        if is_container:
            if path == "/": # root
                return self.put_container(path)
            else:
                return self.put_container(path[:-1])
        else:
            return self.put_dataObject(path)

    @csrf_exempt
    def delete(self, request, path='/', format=None):
        self.user = request.user
        print self.user

        # Add a '/' at the beginning
        path = "/{}".format(path)
        # In CDMI standard a container is defined by the / at the end
        is_container = path.endswith('/')
        try:
            if not path or path == '/':
                # Refuse to delete root container
                return Response(status=HTTP_409_CONFLICT)
            elif is_container:
                # Delete container
                self.delete_container(path[:-1])
            else:
                # Delete data object
                self.delete_dataObject(path)
        except NoSuchResourceError:
            # Path does not exist at all
            return Response(status=HTTP_404_NOT_FOUND)
        except (ResourceConflictError, CollectionConflictError):
            # Incorrectly specified path - object as container or vice versa
            return Response(status=HTTP_404_NOT_FOUND)
        except NoWriteAccessError:
            return Response(status=HTTP_403_FORBIDDEN)
        else:
            return Response(status=HTTP_204_NO_CONTENT)


    def delete_dataObject(self, path):
        resource = Resource.find_by_path(path)
        if not resource:
            collection = Collection.find_by_path(path)
            if collection:
                return self.delete_container(path)
            else:
                raise NoSuchResourceError
        container = resource.get_container()
        resource.delete()

    def delete_container(self, path):
        collection = Collection.find_by_path(path)
        if not collection:
            raise NoSuchResourceError
        Collection.delete_all(collection.path())

    def read_container(self, path):
        collection = Collection.find_by_path(path)

        if not collection:
            return Response(status=HTTP_404_NOT_FOUND)

        body = OrderedDict()
        body['completionStatus'] = "Complete"
        # Update with generic mandatory body fields
        body.update(self._get_genericBodyFields(collection, True))
        body['childrenrange'] = "0-0"

        # "X-CDMI-Specification-Version" = "1.1"
        # "Content-Type" = "application/cdmi-container"

        child_c = list(collection.get_child_collections())
        child_c = [ "{}/".format(c.name) for c in child_c ]
        child_r = list(collection.get_child_resources())
        child_r = [ "{}".format(c.name) for c in child_r ]

        body['children'] = child_c + child_r

        return JsonResponse(body, content_type=body["objectType"])

    def read_dataObject(self, path):
        # Data object
        resource = Resource.find_by_path(path)
        if not resource:
            collection = Collection.find_by_path(path)
            if collection:
                # Remove trailing '/' from the path
                return self.read_container(path)
            else:
                return Response(status=HTTP_404_NOT_FOUND)

        body = OrderedDict()
        # Update with generic mandatory body fields
        body.update(self._get_genericBodyFields(resource, False))

        # Mandatory mimetype
        body['mimetype'] = body['metadata'].pop('cdmi_mimetype', None)
        if not body['mimetype']:
            # Give best guess at mimetype
            mt = mimetypes.guess_type(path)
            if mt[0]:
                body['mimetype'] = mt[0]
            else:
                # Interpret as binary data
                body['mimetype'] = 'application/octet-stream'

        # Mandatory completionStatus
        body['completionStatus'] = body['metadata'].pop(
            'cdmi_completionStatus', None
        )

        # Fetch the object value
#         data = redirect('archive:download', path=path).content
        driver = get_driver(resource.url)

        # TODO: Improve that for large files. Check a=what CDMI recommends
        # for stream access
        data = ""
        for chk in driver.chunk_content():
            data += chk

        if self.request.META.has_key("HTTP_RANGE"):
            start = 0
            end = len(data)
            if self.request.range.start:
                start = self.request.range.start
            if self.request.range.end:
                end = self.request.range.end
            data = data[start:end]
        else:
            # Mandatory valuerange
            # Have to manually parse parameters
            start = 0
            end = len(data)
            for key in self.request.GET:
                if key.startswith('value:'):
                    value = key[len('value:'):]
                    start, end = map(int, value.split('-'))
                    end = min(end, len(data))
                    data = data[start:end]

#         if start != 0 or end != len(data):
#             self.response.status = "206 Partial Content"

        start = 0
        end = len(data)
        # We don't support read/write value range so return the whole thing
        body['valuerange'] = "{0}-{1}".format(start, end)
        # Mandatory valuetransferencoding
        # We'll assume that all data objects are binary
        # Encode them in base46
        body['valuetransferencoding'] = "base64"
        body['value'] = base64.b64encode(data)
        if (self.request.META.has_key("HTTP_X_CDMI_SPECIFICATION_VERSION") and
            self.request.META.get('HTTP_ACCEPT', '') == 'application/cdmi-object'):
            return JsonResponse(body,
                                content_type=body['objectType'])
        else:
            return Response(data,
                            content_type=body['mimetype'])
            # redirect should be better but fails with alloyclient.get
#             return redirect('archive:download', path=path)


    def put_container(self, path):
#         if not username:
#             self.response.status = "401 Unauthorized"
#             return
#         # CREATE or UPDATE Container
        parent, name = split(path)
        body = OrderedDict()
        try:
            if name:
                collection = Collection.create(name=name,
                                                container=parent)
                delayed = True
            else:
                collection = Collection.get_root_collection()
                delayed = False
        except NoSuchCollectionError:
            return Response(status=HTTP_404_NOT_FOUND)
        except ResourceConflictError:
            pass
        except CollectionConflictError:
            # ValidationError -> Try to create the root
            # Container exists, we update it
            collection = Collection.find_by_path(path)
            delayed = False
#         except NoWriteAccessError:
#             self.response.status = "403 Forbidden"
#             return
        res = self.put_container_metadata(collection)
        if res != HTTP_204_NO_CONTENT:
            return Response(status=res)
        # Update with generic mandatory body fields
        body.update(self._get_genericBodyFields(collection, True))
        # There are no children - we only just created the container
        body['childrenrange'] = "0-0"
        body['children'] = []
        cdmi_version = check_cdmi_version(self.request)
        if cdmi_version:
            # Client is expecting a serialized CDMI response
            content_type = body['objectType']
            # Mandatory completionStatus
            if delayed:
                response_status = HTTP_202_ACCEPTED
                body['completionStatus'] = "Processing"
            else:
                response_status = HTTP_201_CREATED
                body['completionStatus'] = "Complete"
        else:
            # Specification states that:
            #
            #     A response message body may be provided as per RFC 2616.
            #
            # Send the CDMI response but with Content-Type = application/json
            content_type = 'application/json'
            # Mandatory completionStatus
            # Does not accept CDMI - cannot return "202 Accepted"
            # Try to wait until complete
            while not path_exists(path):
                # Wait for 5 seconds
                time.sleep(5)
            response_status = "201 Created"
            body['completionStatus'] = "Complete"
        return JsonResponse(body,
                            content_type=body['objectType'],
                            status=response_status)


    def put_container_metadata(self, collection):
        # TODO: cdmi_acl, remove metadata
        # Store any metadata and return appropriate error
        metadata = {}
        tmp = self.request.content_type.split(";")
        content_type = tmp[0]
#         ?if (content_type == 'application/cdmi-container'):
        try:
            body = self.request.body
            requestBody = json.loads(body)
        except:
            return HTTP_400_BAD_REQUEST
        try:
            metadata = requestBody.get("metadata", {})
            if metadata:
                collection.update(metadata=metadata)
            return HTTP_204_NO_CONTENT
        except NoWriteAccessError:
            return HTTP_403_FORBIDDEN
#         else:
#             return HTTP_409_CONFLICT
#         return


    def put_dataObject(self, path):

        # Check if a collection with the name exists
        collection = Collection.find_by_path(path)
        if collection:
            # Remove trailing '/' from the path
            return self.put_container(path)

        parent, name = split(path)
        body = OrderedDict()
        storagePath = path
        metadata = {}
        # CREATE or UPDATE data object
        tmp = self.request.content_type.split("; ")
        content_type = tmp[0]
        delayed = False
        use_cdmi = self.request.META.has_key("HTTP_X_CDMI_SPECIFICATION_VERSION")
        use_cdmi=True


        # TODO Check header charset, parse content_type ?
#         if not use_cdmi:
#             if self.request.charset == "UTF-8":
#                 metadata['cdmi_valuetransferencoding'] = "utf-8"
#             else:
#                 metadata['cdmi_valuetransferencoding'] = "base64"

#         if "X-CDMI-Partial" in self.request.headers:
#             metadata['cdmi_completionStatus'] = "Processing"
#         else:
#             metadata['cdmi_completionStatus'] = "Complete"

        if not content_type:
            if use_cdmi:
                # This is mandatory - either application/cdmi-object or
                # mimetype of data object to create
                return Response(status=HTTP_400_BAD_REQUEST)
                # TODO: send diagnostic?
            else:
                # use http
                mimetype = "application/octet-stream"
        if content_type == 'application/cdmi-container':
            # CDMI request performed to create a new container resource
            # but omitting the trailing slash at the end of the URI
            # CDMI standards mandates 400 Bad Request response
            return Response(status=HTTP_400_BAD_REQUEST)
        elif content_type == 'application/cdmi-object':
            if not use_cdmi:
                # Should send the X-CDMI-Specification-Version to use this
                # mimetype
                return Response(status=HTTP_400_BAD_REQUEST)

            # Sent as CDMI JSON
            try:
                body = self.request.body
                requestBody = json.loads(body)
            except Exception as e:
                return Response(status=HTTP_400_BAD_REQUEST)
            # Check for metadata parameters
#             for param_name in self.request.params:
#                 if param_name.startswith('metadata:'):
#                     k = param_name.split(':', 1)[1]
#                     try:
#                         metadata[k] = requestBody['metadata'][k]
#                     except KeyError:
#                         pass
#                 elif param_name == 'mimetype':
#                     mdk = '{0}_mimetype'.format(METADATA_PREFIX)
#                     metadata[mdk] = requestBody['mimetype']
            metadata = requestBody.get("metadata", {})

            valueType = [key
                         for key in requestBody
                         if key in POSSIBLE_DATA_OBJECT_LOCATIONS
                         ]
            # Sanity check request body
            if not valueType:
                # No data specified
                # Check for metadata update
                if metadata:
                    try:
                        resource = Resource.find_by_path(path)
                        resource.update(metadata=metadata)
                        return JsonResponse(metadata, status=HTTP_204_NO_CONTENT )
                    except NoWriteAccessError:
                        return Response(status=HTTP_403_FORBIDDEN)
                else:
                    # To update metadata without data must supply metadata
                    # parameters
                    return Response(status=HTTP_400_BAD_REQUEST)
            elif len(valueType) > 1:
                # Only one of these fields shall be specified in any given
                # operation.
                    return Response(status=HTTP_400_BAD_REQUEST)
            elif valueType[0] != 'value':
                # Only 'value' is supported at the present time
                    return Response(status=HTTP_400_BAD_REQUEST)
            # CDMI specification mandates that text/plain should be used
            # where mimetype is absent
            mimetype = requestBody.get('mimetype', 'text/plain')
            # Assemble metadata
            if not metadata:
                metadata.update(requestBody.get('metadata', {}))
            content = requestBody.get(valueType[0])
            encoding = requestBody.get('valuetransferencoding', 'utf-8')
            if encoding == "base64":
                try:
                    content = base64.b64decode(content)
                except TypeError:
                    return Response(status=HTTP_400_BAD_REQUEST)
            elif encoding != "utf-8":
                return Response(status=HTTP_400_BAD_REQUEST)
            metadata['cdmi_valuetransferencoding'] = encoding
        else:
            # Sent as non-CDMI
            mimetype = content_type
            content = self.request.body
            # TODO: Assemble metadata from HTTP headers
        start = None
        end = None
#         # Range ?
#         if self.request.range:
#             start = 0
#             end = len(content)
#             if self.request.range.start:
#                 start = self.request.range.start
#             if self.request.range.end:
#                 end = self.request.range.end

        metadata['cdmi_mimetype'] = mimetype
        # Find out if object will be created so that correct HTTP
        # response code can be returned
        created = not(is_resource(storagePath))
        # Store the data object
        try:
            if start and end:
                pass
                # Update a range of the file ??
#                 delayed = self.database.update_dataObject(username,
#                                                           storagePath,
#                                                           content,
#                                                           metadata,
#                                                           start,
#                                                           end)
            else:
                raw_data = content
                chunk_size = 1048576
                file_name = name
                blob = Blob.create()
                content_type = mimetype
                hasher = hashlib.sha256()

                if settings.COMPRESS_UPLOADS:
                    # Compress the raw_data and store that instead
                    f = StringIO()
                    z = zipfile.ZipFile(f, "w", zipfile.ZIP_DEFLATED)
                    z.writestr("data", raw_data)
                    z.close()
                    data = f.getvalue()
                    f.close()
                else:
                    data = raw_data

                part = BlobPart.create(blob_id=blob.id,
                                       compressed=settings.COMPRESS_UPLOADS,
                                       content=data)
                parts = blob.parts or []
                parts.append(part.id)
                blob.update(parts=parts)

                hasher.update(data)

                blob_id = blob.id
                url = "cassandra://{}".format(blob_id)
                resource = Resource.find_by_path(storagePath)
                if resource:
                    resource.update(url=url,
                                    size=len(content),
                                    mimetype=mimetype,
                                    type=get_extension(name))
                else:
                    resource = Resource.create(name=name,
                                               container=parent,
                                               url=url,
                                               size=len(content),
                                               mimetype=mimetype,
                                               type=get_extension(name))
        except (NoSuchCollectionError,
                CollectionConflictError,
                NoSuchResourceError):
            return Response(status=HTTP_404_NOT_FOUND)
        except NoWriteAccessError:
            return Response(status=HTTP_403_FORBIDDEN)

        if (use_cdmi):
            response_content_type = 'application/cdmi-object'
            if created:
                if delayed:
                    response_status = "202 Accepted"
                    body['completionStatus'] = "Processing"
                else:
                    response_status = "201 Created"
                    body['completionStatus'] = "Complete"
                # Update with generic mandatory body fields
                body.update(self._get_genericBodyFields(resource, False))
                # Mandatory mimetype
                body['mimetype'] = mimetype
                return JsonResponse(body,
                                    content_type=response_content_type,
                                    status=response_status)
            else:
                # No response message mandated by CDMI Spec 8.6.7
                return Response(status=HTTP_204_NO_CONTENT)
            # Update with generic mandatory body fields
            body.update(self._get_genericBodyFields(username, path, False))
            # Mandatory mimetype
            body['mimetype'] = mimetype
            return JsonResponse(body)
        else:
            # Does not accept CDMI - cannot return "202 Accepted"
            # Wait until complete
            while not is_resource(storagePath):
                # Wait for 5 seconds
                time.sleep(5)
            if created:
                response_status = "201 Created"
            else:
                response_status = "204 No Content"
            # No response message
            return Response(status=response_status)
