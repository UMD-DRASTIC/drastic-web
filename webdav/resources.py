from os import path as ospath
from datetime import datetime

from djangodav.fs.resources import BaseFSDavResource
from djangodav.utils import url_join
from drastic.models import Collection, Resource, DataObject

import logging


logging.warn('WEBDAV has been loaded')
CHUNK_SIZE = 1048576


def chunkstring(string, length):
    return (string[0+i:length+i] for i in range(0, len(string), length))


class DrasticDavResource(BaseFSDavResource):
    root = '/'
    node = None
    notfound = False

    def me(self):
        if self.node is not None or self.notfound:
            return self.node

        try:
            self.node = Collection.find(self.get_abs_path())
        except Exception:
            logging.exception('Cannot fetch drastic collection for {}'.format(self.path))

        if self.node is None:
            try:
                self.node = Resource.find(self.get_abs_path())
            except Exception:
                logging.exception("Cannot find drastic file resource for {}"
                                  .format(self.path))

        if self.node is None:
            self.notfound = True
        return self.node

    def get_abs_path(self):
        """Return the absolute path of the resource. Used internally to interface with
        an actual file system. If you override all other methods, this one will not
        be used."""
        return ospath.join(self.root, *self.path)

    @property
    def getcontentlength(self):
        """Return the size of the resource in bytes."""
        return self.me().get_size()

    def get_created(self):
        """Return the create time as datetime object."""
        return self.me().get_create_ts()

    def get_modified(self):
        """Return the modified time as datetime object."""
        return self.me().get_modified_ts()

    @property
    def is_root(self):
        if self.path is None or len(self.path) == 0:
            return True
        else:
            return False

    @property
    def displayname(self):
        if self.is_root:
            return '/'
        else:
            return super(DrasticDavResource, self).displayname

    @property
    def is_collection(self):
        """Return True if this resource is a directory (collection in WebDAV parlance)."""
        return isinstance(self.me(), Collection)

    @property
    def is_object(self):
        """Return True if this resource is a file (resource in WebDAV parlance)."""
        return not self.is_collection

    @property
    def exists(self):
        """Return True if this resource exists."""
        return self.me() is not None

    @property
    def getetag(self):
        return self.me().uuid

    def get_children(self):
        """Return an iterator of all direct children of this resource."""
        if self.is_collection:
            child_c, child_r = self.me().get_child()
            child_c = [u"{}/".format(c) for c in child_c]
            child_c.extend(child_r)
            for child in child_c:
                yield self.clone(url_join(*(self.path + [child])))

    def read(self):
        data = []
        for chk in self.me().chunk_content():
            data.append(chk)
        return data

    def write(self, request):
        """Write this data object from HTTP request."""
        # Note that all permission checks happen in DAVView
        # TODO Can be optimized with Cassandra LWT

        # Check if the resource already exists
        content = request.body
        # md5sum = md5(content).hexdigest()
        mimetype = "application/octet-stream"
        logging.warn(str(dir(request)))
        if hasattr(request, 'content_type'):
            tmp = request.content_type.split("; ")
            mimetype = tmp[0]

        resource = Resource.find(self.get_abs_path())
        if resource:
            # NOTE For now WEBDAV updates are not supported.
            # TODO WEBDAV updates were resulting in empty files. Compare with CDMIResource
            raise NotImplementedError()
            # Update value
            # Delete old blobs
            old_meta = resource.get_metadata()
            old_acl = resource.get_acl()
            create_ts = resource.get_create_ts()

            resource.delete_blobs()
            uuid = None
            seq_num = 0
            for chk in chunkstring(content, CHUNK_SIZE):
                if uuid is None:
                    uuid = DataObject.create(chk,
                                             metadata=old_meta,
                                             acl=old_acl,
                                             create_ts=create_ts).uuid
                else:
                    DataObject.append_chunk(uuid, chk, seq_num, False)
                seq_num += 1
            url = "cassandra://{}".format(uuid)
            resource.update(url=url,
                            mimetype=mimetype)
        else:  # Create resource
            uuid = None
            seq_num = 0
            create_ts = datetime.now()
            for chk in chunkstring(content, CHUNK_SIZE):
                if uuid is None:
                    uuid = DataObject.create(chk, False,
                                             create_ts=create_ts).uuid
                else:
                    DataObject.append_chunk(uuid, chk, seq_num, False)
                seq_num += 1
            if uuid is None:  # Content is null
                uuid = self.create_empty_data_object()
            url = "cassandra://{}".format(uuid)
            resource = Resource.create(name=self.displayname,
                                       container=self.get_parent_path()[:-1],
                                       url=url,
                                       mimetype=mimetype,
                                       size=len(content))

    def delete(self):
        """Delete the resource, recursive is implied."""
        self.me().delete()

    def create_collection(self):
        """Create a directory in the location of this resource."""
        # TODO needs checks from CDMIView
        container = None
        if self.get_parent_path() == '' or self.get_parent_path() == '/':
            container = '/'
        else:
            container = self.get_parent_path()[:-1]
        Collection.create(name=self.displayname, container=container)

    def copy_object(self, destination, depth=0):
        raise NotImplementedError

    def move_object(self, destination):
        raise NotImplementedError
