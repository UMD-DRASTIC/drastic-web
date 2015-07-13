

class CDMIMiddleware(object):

    def process_response(self, request, response):
        #if request.path.startswith("/cdmi"):
        #    response["Content-Type"] = "application/json"
        #    response["X-CDMI-Specification-Version"] = "1.1"

        return response

