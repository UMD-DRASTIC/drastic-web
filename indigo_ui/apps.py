""""Indigo UI apps

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

from django.apps import AppConfig
from indigo import get_config


class IndigoAppConfig(AppConfig):
    name = 'indigo_ui'
    verbose_name = "Indigo"

    def ready(self):
        from indigo.models import initialise, Collection

        cfg = get_config(None)
        initialise(keyspace=cfg.get('KEYSPACE', 'indigo'),
                   hosts=cfg.get('CASSANDRA_HOSTS', ('127.0.0.1', )))

        root = Collection.find("/")
        if not root:
            print "Creating root collection"
            Collection.create_root()
        else:
            print "Using existing root collection"

