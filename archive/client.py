"""Archive Client

This client class is used to retrieve information from the agent using
the CDMI interface that it exposes.

"""
__copyright__ = "Copyright (C) 2016 University of Maryland"
__license__ = "GNU AFFERO GENERAL PUBLIC LICENSE, Version 3"


from libcdmi import cdmi
from django.conf import settings

def get_default_client():
    cfg = settings.CDMI_SERVER
    return Client(cfg["endpoint"], cfg["username"], cfg["password"] )

class Client(object):

    def __init__(self, endpoint, username, password):
        credentials = {
            "user": username,
            "password": password
        }
        self.conn = cdmi.CDMIConnection(endpoint, credentials)

    def create_collection(self, full_path, metadata=None):
        if metadata:
            return self.conn.container_proxy.create(full_path, metadata=metadata)
        return self.conn.container_proxy.create(full_path)

    def get_collection(self, full_path):
        return self.conn.container_proxy.read(full_path)

    def delete_collection(self, full_path):
        return self.conn.container_proxy.delete(full_path)

    def get_resource_info(self, full_path):
        return self.conn.blob_proxy.read(full_path)

    def get_resource_content(self, full_path):
        return self.conn.blob_proxy.read(full_path, cdmi_object=False)

