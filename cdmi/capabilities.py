""""CDMI Capabilities

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


from collections import namedtuple


SystemCapabilities = namedtuple(
    'SystemCapabilities',
    ['cdmi_domains',
     'cdmi_dataobjects',
     'cdmi_security_access_control',
     'cdmi_serialization_json',
     'cdmi_query',
     'cdmi_query_regex',
     'cdmi_query_contains',
     'cdmi_query_tags',
     'cdmi_query_value',
     'cdmi_notification',
     'cdmi_logging',
     'cdmi_object_move_from_local',
     'cdmi_object_copy_from_local',
     'cdmi_object_copy_from_remote',
     'cdmi_references'
     ]
)

StorageSystemMetadataCapabilities = namedtuple(
    "StorageSystemMetadataCapabilities",
    ['cdmi_acl',
     'cdmi_size',
     'cdmi_ctime',
     'cdmi_atime',
     'cdmi_mtime',
     'cdmi_acount',
     'cdmi_mcount'
     ]
)

DataSystemMetadataCapabilities = namedtuple(
    "DataSystemMetadataCapabilities",
    ['cdmi_data_autodelete',
     'cdmi_retention_autodelete',   # See Spec!
     'cdmi_data_retention',
     'cdmi_data_dispersion',
     'cdmi_geographic_placement'
     ]
)

ContainerCapabilities = namedtuple(
    "ContainerCapabilities",
    ['cdmi_create_container',     # Containers within containers
     'cdmi_delete_container',
     'cdmi_create_queue',
     'cdmi_copy_queue',
     'cdmi_move_queue',
     'cdmi_read_metadata',
     'cdmi_modify_metadata',
     'cdmi_list_children',
     'cdmi_list_children_range',
     'cdmi_create_dataobject',
     'cdmi_post_dataobject',
     'cdmi_create_reference',
     'cdmi_copy_dataobject',
     'cdmi_move_dataobject'
     ]
)

DataObjectCapabilities = namedtuple(
    "DataObjectCapabilities",
    ['cdmi_read_metadata',
     'cdmi_read_value',
     'cdmi_read_value_range',
     'cdmi_modify_metadata',
     'cdmi_modify_value',
     'cdmi_delete_dataobject'
     ]
)

DomainCapabilities = namedtuple(
    'DomainCapabilities',
    ['cdmi_create_domain',
     'cdmi_delete_domain',
     'cdmi_domain_summary',
     'cdmi_domain_members',
     'cdmi_list_children',
     'cdmi_read_metadata',
     'cdmi_modify_metadata',
     'cdmi_modify_deserialize_domain',
     'cdmi_copy_domain',
     'cdmi_deserialize_domain'
     ]
)

QueueObjectCapabilities = namedtuple(
    "QueueObjectCapabilities",
    ['cdmi_read_metadata',
     'cdmi_read_value',
     'cdmi_modify_metadata',
     'cdmi_delete_queue',
     'cdmi_modify_value',
     ]
)

SYSTEM_CAPABILITIES = SystemCapabilities(**{
    'cdmi_domains': True,
    'cdmi_dataobjects': True,
    'cdmi_security_access_control': True,
    'cdmi_serialization_json': True,
    'cdmi_query': False,
    'cdmi_query_regex': False,
    'cdmi_query_contains': False,
    'cdmi_query_tags': False,
    'cdmi_query_value': False,
    'cdmi_notification': False,
    'cdmi_logging': False,
    'cdmi_object_move_from_local': False,
    'cdmi_object_copy_from_local': False,
    'cdmi_object_copy_from_remote': False,
    'cdmi_security_access_control': False,
    'cdmi_references': False
})

DOMAIN_CAPABILITIES = DomainCapabilities(**{
    'cdmi_create_domain': False,
    'cdmi_delete_domain': False,
    'cdmi_domain_summary': False,
    'cdmi_domain_members': False,
    'cdmi_list_children': False,
    'cdmi_read_metadata': False,
    'cdmi_modify_metadata': False,
    'cdmi_modify_deserialize_domain': False,
    'cdmi_copy_domain': False,
    'cdmi_deserialize_domain': False
})

# We actually won't support Queues for v1.0
# All values will be False
QUEUE_OBJECT_CAPABILITIES = QueueObjectCapabilities(**{
    'cdmi_read_metadata': False,
    'cdmi_read_value': False,
    'cdmi_modify_metadata': False,
    'cdmi_delete_queue': False,
    'cdmi_modify_value': False
})