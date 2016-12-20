""""Drastic UI apps
"""
__copyright__ = "Copyright (C) 2016 University of Maryland"
__license__ = "GNU AFFERO GENERAL PUBLIC LICENSE, Version 3"


from django.apps import AppConfig
from drastic import get_config


class DrasticAppConfig(AppConfig):
    name = 'drastic_ui'
    verbose_name = "Drastic"

    def ready(self):
        from drastic.models import connect, Collection

        cfg = get_config(None)
        connect(keyspace=cfg.get('KEYSPACE', 'drastic'),
                   hosts=cfg.get('CASSANDRA_HOSTS', ('127.0.0.1', )))

        #  root = Collection.find("/")
        if False:  # not root:
            print "Creating root collection"
            Collection.create_root()
        else:
            print "Using existing root collection"
