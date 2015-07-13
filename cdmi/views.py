from collections import OrderedDict

from django.shortcuts import render
from django.http import JsonResponse

from cdmi.capabilities import SYSTEM_CAPABILITIES
from cdmi.storage import CDMIDataAccessObject


def capabilities(request, path):

    body = OrderedDict()
    if path in ['', '/']:
        body['capabilities'] = SYSTEM_CAPABILITIES._asdict()
    elif path.startswith('/dataobject'):
        d = CDMIDataAccessObject({}).dataObjectCapabilities._asdict()
        body['capabilities'] = d
    elif path.startswith('/container'):
        d = CDMIDataAccessObject({}).containerCapabilities._asdict()
        body['capabilities'] = d

    return JsonResponse(body)