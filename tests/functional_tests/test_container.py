"""|sect| `CDMI_9`_ Tests the creation, reading, updating, and deleting of container objects.

All mandatory header fields and content are tested.

Where an assertion tests a specific part of the spec, a link is provided to the relevant section, and the assertion's
comment prints the section number in parentheses after the message.
"""
from functools import partial
import json
import logging

import shortuuid

from . import utils
from .utils import log_request, assert_context, object_context, get_config

create_container_response_fields = (u'objectType', u'objectID', u'objectName', u'parentURI', u'parentID',
                                    u'capabilitiesURI', u'completionStatus', u'metadata', u'childrenrange',
                                    u'children')

read_container_response_fields = (u'objectType', u'objectID', u'objectName', u'parentURI', u'parentID',
                                  u'capabilitiesURI', u'completionStatus', u'metadata', u'childrenrange', u'children')


def setup_module():
    conf = get_config('CDMI')
    conf['headers']['Accept'] = 'application/cdmi-container'
    conf['headers']['Content-Type'] = 'application/cdmi-container'
    response = utils.session.put('{0}/{1}/'.format(conf['host'], conf['object-container']), headers=conf['headers'])
    log_request(response)


def teardown_module():
    conf = get_config('CDMI')
    response = utils.session.delete('{0}/{1}/'.format(conf['host'], conf['object-container']), headers=conf['headers'])
    log_request(response)


def test_create_a_container_object_using_cdmi_content_type_by_name():
    """|sect| `CDMI_9.2`_ Tests valid creation of a CDMI container object.

    :command: ``PUT /<container name>/``

    :asserts:
        * HTTP status code == 201 |sect| `CDMI_9.2.8`_
        * HTTP Content-Type == 'application/cdmi-container' |sect| `CDMI_9.2.6`_
        * HTTP X-CDMI-Specification-Version == '1.0.2' |sect| `CDMI_9.2.6`_
        * Presence of mandatory CDMI fields in response |sect| `CDMI_9.2.7`_ domainURI is currently being treated as
          optional because |sect| `CDMI_12.1.1`_ says it is.
        * CDMI objectType == 'application/cdmi-container' |sect| `CDMI_9.2.7`_
        * CDMI objectName == container name |sect| `CDMI_9.2.7`_
        * CDMI parentURI == '/testrunner/' |sect| `CDMI_9.2.7`_
        * CDMI completionStatus == 'Complete' |sect| `CDMI_9.2.7`_
    """
    conf = get_config('CDMI')
    conf['headers']['Accept'] = 'application/cdmi-container'
    conf['headers']['Content-Type'] = 'application/cdmi-container'
    # params = {
    #     'metadata': {}
    # }

    container_name = shortuuid.uuid() + '/'

    with object_context(container_name, utils.session, conf) as response, assert_context() as _assert:
        _assert(response.status_code == 201,
                u'Expected HTTP status code {0} got {1} (9.2.8)'.format(201, response.status_code))

        body = response.json()

        logging.info(u'Created container "{0}" with object ID: {1}'.format(container_name, body['objectID']))

        _assert(conf['headers']['Content-Type'] in response.headers['Content-Type'],
                u'Expected HTTP Content-Type "{0}" got "{1}" (9.2.6)'.format(conf['headers']['Content-Type'],
                                                                             response.headers['Content-Type']))
        _assert(response.headers['X-CDMI-Specification-Version'] == conf['headers']['X-CDMI-Specification-Version'],
                u'Expected version "{0}" got "{1}" (9.2.6)'.format(conf['headers']['X-CDMI-Specification-Version'],
                                                                   response.headers['X-CDMI-Specification-Version']))

        for field in create_container_response_fields:
            _assert(field in body, u'Data object response is missing mandatory field "{0}" (9.2.7)'.format(field))

        _assert(conf['headers']['Content-Type'] in body['objectType'],
                u'Expected CDMI objectType "{0}" got "{1}" (9.2.7)'.format(conf['headers']['Content-Type'],
                                                                           body['objectType']))
        _assert(body['objectName'] == container_name,
                u'Expected CDMI objectName "{0}" got "{1}" (9.2.7)'.format(container_name, body['objectName']))
        _assert(body['parentURI'] == u'/{0}/'.format(conf['object-container']),
                u'Expected CDMI parentURI "{0}" got "{1}" (9.2.7)'.format(u'/{0}/'.format(conf['object-container']),
                                                                          body['parentURI']))
        _assert(body['completionStatus'] == u'Complete',
                u'Expected CDMI completionStatus "{0}" got "{1}" (9.2.7)'.format(u'Complete', body['completionStatus']))


def test_create_a_container_object_using_non_cdmi_content_type_by_name():
    """|sect| `CDMI_9.3`_ Tests valid creation of a CDMI container object using a non-CDMI content type.

    :command: ``PUT /<container name>/``

    :asserts: HTTP status code == 201 |sect| `CDMI_9.3.7`_
    """
    conf = get_config('CDMI')
    del conf['headers']['X-CDMI-Specification-Version']

    container_name = shortuuid.uuid() + '/'

    with object_context(container_name, utils.session, conf) as response, assert_context() as _assert:
        _assert(response.status_code == 201,
                u'Expected HTTP status code {0} got {1} (9.2.8)'.format(201, response.status_code))


def test_read_a_container_object_using_cdmi_content_type_by_name():
    """|sect| `CDMI_9.4`_ Tests valid reading of a CDMI container object.

    :command: ``GET /<container name>/``

    :asserts:
        * HTTP status code == 200 |sect| `CDMI_9.4.7`_
        * HTTP Content-Type == 'application/cdmi-container' |sect| `CDMI_9.4.5`_
        * HTTP X-CDMI-Specification-Version == '1.0.2' |sect| `CDMI_9.4.5`_
        * Presence of mandatory CDMI fields in response |sect| `CDMI_9.4.6`_ domainURI is currently being treated as
          optional because |sect| `CDMI_12.1.1`_ says it is.
        * CDMI objectType == 'application/cdmi-container' |sect| `CDMI_9.4.6`_
        * CDMI objectName == container name |sect| `CDMI_9.4.6`_
        * CDMI parentURI == '/testrunner/' |sect| `CDMI_9.4.6`_
        * CDMI completionStatus == 'Complete' |sect| `CDMI_9.4.6`_
    """
    conf = get_config('CDMI')
    conf['headers']['Accept'] = 'application/cdmi-container'

    container_name = shortuuid.uuid() + '/'

    with object_context(container_name, utils.session, conf) as create_response, assert_context() as _assert:
        _assert(create_response.status_code == 201,
                u'Expected HTTP status code {0} got {1} (9.2.8)'.format(201, create_response.status_code))

        del conf['headers']['Accept']
        conf['headers']['Content-Type'] = 'application/cdmi-container'

        response = utils.session.get('{0}/{1}/{2}'.format(conf['host'], conf['object-container'], container_name),
                                     headers=conf['headers'])

        log_request(response)

        _assert(response.status_code == 200,
                u'Expected HTTP status code {0} got {1} (9.4.7)'.format(200, response.status_code))

        _assert(conf['headers']['Content-Type'] in response.headers['Content-Type'],
                u'Expected HTTP Content-Type "{0}" got "{1}" (9.4.5)'.format(conf['headers']['Content-Type'],
                                                                             response.headers['Content-Type']))
        _assert(response.headers['X-CDMI-Specification-Version'] == conf['headers']['X-CDMI-Specification-Version'],
                u'Expected version "{0}" got "{1}" (9.4.5)'.format(conf['headers']['X-CDMI-Specification-Version'],
                                                                   response.headers['X-CDMI-Specification-Version']))

        body = response.json()

        for field in read_container_response_fields:
            _assert(field in body, u'Data object response is missing mandatory field "{0}" (9.4.6)'.format(field))

        _assert(conf['headers']['Content-Type'] in body['objectType'],
                u'Expected CDMI objectType "{0}" got "{1}" (9.4.6)'.format(conf['headers']['Content-Type'],
                                                                           body['objectType']))
        _assert(body['objectName'] == container_name,
                u'Expected CDMI objectName "{0}" got "{1}" (9.4.6)'.format(container_name, body['objectName']))
        _assert(body['parentURI'] == u'/{0}/'.format(conf['object-container']),
                u'Expected CDMI parentURI "{0}" got "{1}" (9.4.6)'.format(u'/{0}/'.format(conf['object-container']),
                                                                          body['parentURI']))
        _assert(body['completionStatus'] == u'Complete',
                u'Expected CDMI completionStatus "{0}" got "{1}" (9.4.6)'.format(u'Complete',
                                                                                 body['completionStatus']))


def test_read_a_container_object_using_cdmi_content_type_by_id():
    """|sect| `CDMI_9.4`_ Tests valid reading of a CDMI container object by its objectID.

    :command: ``GET /cdmi_objectid/<container objectID>/``

    :asserts:
        * HTTP status code == 200 |sect| `CDMI_9.4.7`_
        * HTTP Content-Type == 'application/cdmi-container' |sect| `CDMI_9.4.5`_
        * HTTP X-CDMI-Specification-Version == '1.0.2' |sect| `CDMI_9.4.5`_
        * Presence of mandatory CDMI fields in response |sect| `CDMI_9.4.6`_ domainURI is currently being treated as
          optional because |sect| `CDMI_12.1.1`_ says it is.
        * CDMI objectType == 'application/cdmi-container' |sect| `CDMI_9.4.6`_
        * CDMI objectName == container name |sect| `CDMI_9.4.6`_
        * CDMI parentURI == '/testrunner/' |sect| `CDMI_9.4.6`_
        * CDMI completionStatus == 'Complete' |sect| `CDMI_9.4.6`_
    """
    conf = get_config('CDMI')
    conf['headers']['Accept'] = 'application/cdmi-container'

    container_name = shortuuid.uuid() + '/'

    with object_context(container_name, utils.session, conf) as create_response, assert_context() as _assert:
        _assert(create_response.status_code == 201,
                u'Expected HTTP status code {0} got {1} (9.2.8)'.format(201, create_response.status_code))

        del conf['headers']['Accept']
        conf['headers']['Content-Type'] = 'application/cdmi-container'

        object_id = create_response.json()['objectID']

        response = utils.session.get('{0}/cdmi_objectid/{1}'.format(conf['host'], object_id), headers=conf['headers'])

        log_request(response)

        _assert(response.status_code == 200,
                u'Expected HTTP status code {0} got {1} (9.4.7)'.format(200, response.status_code))

        _assert(conf['headers']['Content-Type'] in response.headers['Content-Type'],
                u'Expected HTTP Content-Type "{0}" got "{1}" (9.4.5)'.format(conf['headers']['Content-Type'],
                                                                             response.headers['Content-Type']))
        _assert(response.headers['X-CDMI-Specification-Version'] == conf['headers']['X-CDMI-Specification-Version'],
                u'Expected version "{0}" got "{1}" (9.4.5)'.format(conf['headers']['X-CDMI-Specification-Version'],
                                                                   response.headers['X-CDMI-Specification-Version']))

        body = response.json()

        for field in read_container_response_fields:
            _assert(field in body, u'Data object response is missing mandatory field "{0}" (9.4.6)'.format(field))

        _assert(conf['headers']['Content-Type'] in body['objectType'],
                u'Expected CDMI objectType "{0}" got "{1}" (9.4.6)'.format(conf['headers']['Content-Type'],
                                                                           body['objectType']))
        _assert(body['objectName'] == container_name,
                u'Expected CDMI objectName "{0}" got "{1}" (9.4.6)'.format(container_name, body['objectName']))
        _assert(body['parentURI'] == u'/{0}/'.format(conf['object-container']),
                u'Expected CDMI parentURI "{0}" got "{1}" (9.4.6)'.format(u'/{0}/'.format(conf['object-container']),
                                                                          body['parentURI']))
        _assert(body['completionStatus'] == u'Complete',
                u'Expected CDMI completionStatus "{0}" got "{1}" (9.4.6)'.format(u'Complete',
                                                                                 body['completionStatus']))


def test_update_a_container_object_using_cdmi_content_type():
    """|sect| `CDMI_9.5`_ Tests valid update of a CDMI container's metadata.

    :command: ``PUT /<container_name>/``

    :tests:
        * CDMI metadata in message body

    :asserts:
        * HTTP status code == 204 |sect| `CDMI_9.5.8`_
        * HTTP status code == 200 |sect| `CDMI_9.4.7`_ (When reading metadata back)
        * returned object ID is the same as the original file's object ID |sect| `CDMI_9.5.1`_
        * CDMI metadata == metadata
    """
    cases = [
        {
            'name': 'CDMI metadata in message body',
            'data': {
                'metadata': {
                    'masts': 2,
                    'length': 100,
                    'name': 'Zebu'
                },
            },
            'params': None
        },
    ]

    for case in cases:
        f = partial(_update_a_container_object_using_cdmi_content_type, case['data'], case['params'])
        test_update_a_container_object_using_cdmi_content_type.__name__ = 'test_update_a_container_object_using_' \
                                                                          'cdmi_content_type <{0}>'.format(case['name'])
        yield f


def _update_a_container_object_using_cdmi_content_type(data, params):
    conf = get_config('CDMI')
    conf['headers']['Accept'] = 'application/cdmi-container'
    conf['headers']['Content-Type'] = 'application/cdmi-container'
    container_name = shortuuid.uuid() + '/'

    with object_context(container_name, utils.session, conf) as create_response, assert_context() as _assert:
        _assert(create_response.status_code == 201,
                u'Expected HTTP status code {0} got {1} (9.2.8)'.format(201, create_response.status_code))

        body = create_response.json()
        object_id = body['objectID']

        put_response = utils.session.put('{0}/{1}/{2}'.format(conf['host'], conf['object-container'], container_name),
                                         headers=conf['headers'],
                                         data=json.dumps(data),
                                         params=params)

        log_request(put_response)

        _assert(put_response.status_code == 204,
                u'Expected HTTP status code {0} got {1} (9.5.8)'.format(204, put_response.status_code))

        # Read the object back.
        response = utils.session.get('{0}/{1}/{2}'.format(conf['host'], conf['object-container'], container_name),
                                     headers=conf['headers'])

        log_request(response)

        _assert(response.status_code == 200,
                u'Expected HTTP status code {0} got {1} (9.4.7)'.format(200, response.status_code))

        body = response.json()

        _assert(body['objectID'] == object_id,
                u'Expected CDMI objectID "{0}" got "{1}" (9.5.1)'.format(object_id, body['objectID']))

        if 'metadata' in data:
            _assert(utils.compare_metadata(data['metadata'], body['metadata']),
                    u'User-supplied metadata does\'t match.')


def delete_a_container_object_using_cdmi_content_type():
    """|sect| `CDMI_9.6`_ Tests valid deletion of a container object.

    :command: ``DELETE /<container_name>/``

    :asserts: HTTP status code == 204 |sect| `CDMI_9.6.7`_
    """
    conf = get_config('CDMI')
    conf['headers']['Accept'] = 'application/cdmi-container'
    conf['headers']['Content-Type'] = 'application/cdmi-container'
    file_name = shortuuid.uuid() + '/'

    with object_context(file_name, utils.session, conf) as create_response, assert_context() as _assert:
        _assert(create_response.status_code == 201,
                u'Expected HTTP status code {0} got {1} (9.2.8)'.format(201, create_response.status_code))

        response = utils.session.delete('{0}/{1}/{2}'.format(conf['host'], conf['object-container'], file_name),
                                        headers=conf['headers'])

        log_request(response)

        _assert(response.status_code == 204,
                u'Expected HTTP status code {0} got {1} (9.6.7)'.format(204, response.status_code))
