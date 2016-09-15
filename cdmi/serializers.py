""""CDMI serializers

"""
__copyright__ = "Copyright (C) 2016 University of Maryland"
__license__ = "GNU AFFERO GENERAL PUBLIC LICENSE, Version 3"


from rest_framework import serializers
from cdmi.models import CDMIContainer


class CDMIContainerSerializer(serializers.ModelSerializer):

    objectType = serializers.CharField()
    objectID = serializers.CharField()
    objectName = serializers.CharField()
    parentURI = serializers.CharField()
    parentID = serializers.CharField()
    domainURI = serializers.CharField()
    capabilitiesURI = serializers.CharField()
    completionStatus = serializers.CharField()
    percentComplete = serializers.CharField()
    metadata = serializers.CharField()
    exports = serializers.CharField()