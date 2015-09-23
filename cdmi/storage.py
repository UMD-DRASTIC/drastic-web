""""CDMI storage

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

import re
from collections import OrderedDict

from cdmi.capabilities import (
    StorageSystemMetadataCapabilities, ContainerCapabilities, DataObjectCapabilities)

class CDMIDataAccessObject(object):
    """CDMI Data Access Object to interact with a data store.

    Enhances the Abstract Base Data Access Object, providing CDMI capabilities
    and CDMI compliant identifier manipulation.
    """

    def __init__(self, config):
        #super(CDMIDataAccessObject, self).__init__(config)
        self.metdataCapabilities = StorageSystemMetadataCapabilities(
            cdmi_acl=False,
            cdmi_size=False,
            cdmi_ctime=False,
            cdmi_atime=False,
            cdmi_mtime=False,
            cdmi_acount=False,
            cdmi_mcount=False
        )
        self.containerCapabilities = ContainerCapabilities(
            cdmi_create_container=False,
            cdmi_delete_container=False,
            cdmi_create_queue=False,
            cdmi_copy_queue=False,
            cdmi_move_queue=False,
            cdmi_read_metadata=False,
            cdmi_modify_metadata=False,
            cdmi_list_children=False,
            cdmi_list_children_range=False,
            cdmi_create_dataobject=False,
            cdmi_post_dataobject=False,
            cdmi_create_reference=False,
            cdmi_copy_dataobject=False,
            cdmi_move_dataobject=False
        )
        self.dataObjectCapabilities = DataObjectCapabilities(
            cdmi_read_metadata=False,
            cdmi_read_value=False,
            cdmi_read_value_range=False,
            cdmi_modify_metadata=False,
            cdmi_modify_value=False,
            cdmi_delete_dataobject=False
        )

    def _CDMIify_metadata(self, metadata):
        """Impose CDMI compliance on metadata dictionary.

        :type metadata: dict
        :returns: CDMI compliant metadata dictionary
        :rtype: dict
        """
        cdmi_md = OrderedDict()
        for k, val in metadata.iteritems():
            # This may be improved
            if not k.startswith(METADATA_PREFIX):
                # Replace keys containing internally used "alloy_" prefix  with
                # CDMI mandated reversed URL style prefixes
                cdmi_k = re.sub('^alloy', METADATA_PREFIX, k, 1)
            else:
                cdmi_k = k
            cdmi_md[cdmi_k] = val

        return cdmi_md

    def _unCDMIify_metadata(self, metadata):
        """Strip CDMI cruft from metadata dictionary for internal storage.

        :type metadata: dict
        :returns: metadata dictionary for internal storage
        :rtype: dict
        """
        store_md = {}
        for k, val in metadata.iteritems():
            if k.startswith('cdmi_'):
                # cdmi_ values are prohibited by CDMI spec for user-defined
                # metadata
                continue
            else:
                store_md[k] = val

        return store_md