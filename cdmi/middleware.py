

class CDMIMiddleware(object):
    """
    Post-processes requests to /cdmi to make sure we add the appropriate
    CDMI headers.
    """

    def process_response(self, request, response):
        """
        As long as this isn't an internal error, and it is a CDMI request,
        make sure we add the CDMI header
        """

        if (response.status_code < 500) and  request.path.startswith("/cdmi"):
            response["X-CDMI-Specification-Version"] = "1.1"

        return response

