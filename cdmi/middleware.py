""""CDMI Middleware

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

