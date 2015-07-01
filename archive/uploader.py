from io import BytesIO
import hashlib

from django.core.files.uploadhandler import FileUploadHandler, StopFutureHandlers
from django.core.files.uploadedfile import InMemoryUploadedFile

from indigo.models import Blob, BlobPart

class AgentUploader(FileUploadHandler):

    chunk_size = 1048576 # 1 Mb chunks

    def new_file(self, field_name, file_name, content_type, content_length, charset, content_type_extra):
        """
        A new file is starting, we should prep Cassandra for a new upload
        """
        self.file_name = file_name
        self.blob = Blob.create()
        self.content_type = content_type
        self.hasher = hashlib.sha256()

        raise StopFutureHandlers()

    def receive_data_chunk(self, raw_data, start):
        """
        Will be called to write 1Mb chunks of data (except for the
        last chunk).
        """
        print u"Received {} bytes".format(len(raw_data))

        self.hasher.update(raw_data)

        part = BlobPart.create(blob_id=self.blob.id, content=raw_data)
        parts = self.blob.parts or []
        parts.append(part.id)

        self.blob.update(parts=parts)

        return None

    def file_complete(self, file_size):
        """
            File is complete, we should return an UploadedFile for use in the
            view. Our UploadedFile will need to reference a Blob object in
            Cassandra which will itself contain a list of all of the BlobParts
            we wrote to the DB.
        """
        print u"File upload complete with {} bytes".format(file_size)
        self.blob.update(size=file_size, hash=self.hasher.hexdigest())

        uploaded = CassandraUploadedFile(name=self.file_name,
                                         content=str(self.blob.id),
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

