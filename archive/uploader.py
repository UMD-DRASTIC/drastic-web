"""Archive AgentUploader

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


from io import BytesIO
import hashlib
import zipfile
from cStringIO import StringIO
from django.conf import settings
from django.core.files.uploadhandler import (
    FileUploadHandler,
    StopFutureHandlers
)
from django.core.files.uploadedfile import InMemoryUploadedFile

from indigo.models import DataObject


class AgentUploader(FileUploadHandler):

    chunk_size = 1048576 # 1 Mb chunks

    def new_file(self, field_name, file_name, content_type, content_length,
                 charset, content_type_extra):
        """
        A new file is starting, we should prep Cassandra for a new upload
        """
        self.file_name = file_name
        self.content_type = content_type
        self.hasher = hashlib.sha256()
        self.data = None
        self.uuid = None
        self.seq_number = 0

        raise StopFutureHandlers()

    def receive_data_chunk(self, raw_data, start):
        """
        Will be called to write 1Mb chunks of data (except for the
        last chunk).
        """
        print u"Received {} bytes - {}".format(len(raw_data), self.seq_number)

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
        
        if not self.uuid:
            data_object = DataObject.create(data, settings.COMPRESS_UPLOADS)
            self.uuid = data_object.uuid
        else:
            DataObject.append_chunk(self.uuid, data, self.seq_number, settings.COMPRESS_UPLOADS)
        self.seq_number += 1

        self.hasher.update(data)

        return None

    def file_complete(self, file_size):
        """
            File is complete, we should return an UploadedFile for use in the
            view. Our UploadedFile will need to reference a Blob object in
            Cassandra which will itself contain a list of all of the BlobParts
            we wrote to the DB.
        """
        print u"File upload complete with {} bytes".format(file_size)

        uploaded = CassandraUploadedFile(name=self.file_name,
                                         content=str(self.uuid),
                                         content_type=self.content_type,
                                         length=file_size)
        return uploaded


class CassandraUploadedFile(InMemoryUploadedFile):
    """
    A simple representation of a file, which just has content, size, and a name.
    In this particular case we are just storing the blob ID as content rather than
    the actual content.
    """
    def __init__(self, name, content, content_type, length):
        super(CassandraUploadedFile, self).__init__(BytesIO(content), None, name,
                                                 content_type, length, None, None)

