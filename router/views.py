from django.shortcuts import render


def route_cdmi(request, path):
    """
    This router will obtain the user's details and then re-route the call
    through to the agent.  This re-routing is done using XSendfile support
    in nginx (see http://wiki.nginx.org/X-accel). This is achieved by setting
    the X-Accel-Redirect header to the URL where the agent will receive it.
    X-Accel-Buffering should be set to false to avoid caching.
    """

