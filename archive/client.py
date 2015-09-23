"""Archive Client

This client class is used to retrieve information from the agent using
the CDMI interface that it exposes.

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

