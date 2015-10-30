Error codes returned:

get:
  - 401: returned by django if no authentication
  - 400: unsupported CDMI version (X_CDMI_SPECIFICATION_VERSION != 1.1, 1.0.2)
  - 404: collection not found
  - 403: user can't read collection
  - 406: read a container without X_CDMI_SPECIFICATION_VERSION header
  - 406: accept header should be 'application/cdmi-container' or '*/*' for a container
  - 406: wrong parameter for a container
  - 200: read ok for a container
  - 404: resource not found (1st try if there's a collection with this name)
  - 403: user can't read resource
  - 416: range paremeter incorrect
  - 206: partial content returned (use of range)
  - 200: read ok in http for a resource
  - 406: accept header should be 'application/cdmi-object' or '*/*' for a resource
  - 406: wrong parameter for a resource
  - 200: read ok in cdmi for a resource

put
  - 400: unsupported CDMI version (X_CDMI_SPECIFICATION_VERSION != 1.1, 1.0.2)
  - 403: user can't edit collection
  - 403: user can't edit resource
  - 406: update through http for a container undefined
  - 404: parent collection not found
  - 403: user can't write parent collection
  - 201: collection created
  - 202: collection creation delayed
  - 400: content_type mandatory in cdmi mode for resource or bad cdmi
  - 400: data not in json format in cdmi mode
  - 400: no or wrong value
  - 406: wrong parameter for a resource
  - 201: resource created
  - 204: resource created/updated in http mode

