"""|sect| `CDMI_8`_ Tests the creation, reading, updating, and deleting of CDMI and non-CDMI objects.

All mandatory header fields and content are tested.

Where an assertion tests a specific part of the spec, a link is provided to the relevant section, and the assertion's
comment prints the section number in parentheses after the message.
"""
from functools import partial
import logging
from base64 import b64encode, b64decode
import json
import binascii
import shortuuid

from . import utils
from .utils import log_request, assert_context, object_context, get_config

sample_text = u"""Hofstadter's Law:
It always takes longer than you think, even when you take into account Hofstadter's Law."""

replacement_sample_text = u"""Newton's Third Law of Motion:
For every action there is an equal and opposite reaction."""

create_data_object_response_fields = ('objectType', 'objectID', 'objectName', 'parentURI', 'capabilitiesURI',
                                      'completionStatus', 'mimetype', 'metadata')

update_data_object_response_fields = ('objectType', 'objectID', 'capabilitiesURI', 'completionStatus',
                                      'mimetype', 'metadata', 'valuerange', 'valuetransferencoding')


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


def test_create_cdmi_content_by_name():
    """|sect| `CDMI_8.2`_ Tests valid uploading of a CDMI-encoded text file to the root collection.

    :command: ``PUT /<file_name>.txt``

    :tests:
        * CDMI mimetype = text/plain, valuetransferencoding = base64
        * No CDMI mimetype, valuetransferencoding = base64
        * CDMI mimetype = text/plain, valuetransferencoding = utf-8
        * Custom metadata

    :asserts:
        * HTTP status code == 201 |sect| `CDMI_8.2.8`_
        * HTTP Content-Type == 'application/cdmi-object' |sect| `CDMI_8.2.6`_
        * HTTP X-CDMI-Specification-Version == '1.0.2' |sect| `CDMI_8.2.6`_
        * Presence of mandatory CDMI fields in response |sect| `CDMI_8.2.7`_ domainURI
          is currently being treated as optional because |sect| `CDMI_12.1.1`_ says it is.
        * CDMI objectType == 'application/cdmi-object' |sect| `CDMI_8.2.7`_
        * CDMI objectName == uploaded file name |sect| `CDMI_8.2.7`_
        * CDMI parentURI == '/testrunner/' |sect| `CDMI_8.2.7`_
        * CDMI mimetype == 'text/plain' |sect| `CDMI_8.2.7`_
        * CDMI completionStatus == 'Complete' |sect| `CDMI_8.2.7`_
    """
    cases = [
        {
            'name': 'CDMI mimetype: text/plain',
            'data': {
                'mimetype': 'text/plain',
                'metadata': {},
                'valuetransferencoding': 'base64',
                'value': b64encode(sample_text)
            },
            'params': None
        },
        {
            'name': 'No CDMI mimetype',
            'data': {
                'metadata': {},
                'valuetransferencoding': 'base64',
                'value': b64encode(sample_text)
            },
            'params': None
        },
        {
            'name': 'CDMI valuetransferencoding: utf-8',
            'data': {
                'mimetype': 'text/plain',
                'metadata': {},
                'valuetransferencoding': 'utf-8',
                'value': sample_text
            },
            'params': None
        },
        {
            'name': 'with metadata',
            'data': {
                'mimetype': 'text/plain',
                'metadata': {
                    'masts': 2,
                    'length': 100,
                    'name': 'Zeb'
                },
                'valuetransferencoding': 'base64',
                'value': b64encode(sample_text)
            },
            'params': None
        },
    ]

    for case in cases:
        f = partial(_create_cdmi_content_by_name, case['data'], case['params'])
        test_create_cdmi_content_by_name.__name__ = 'test_create_cdmi_content_by_name <{0}>'.format(case['name'])
        yield f


def _create_cdmi_content_by_name(data, params):
    conf = get_config('CDMI')
    conf['headers']['Accept'] = 'application/cdmi-object'
    conf['headers']['Content-Type'] = 'application/cdmi-object'

    file_name = shortuuid.uuid() + '.txt'

    with object_context(file_name, utils.session, conf, json.dumps(data), params) as response, \
            assert_context() as _assert:
        _assert(response.status_code == 201,
                'Expected HTTP status code {0} got {1} (8.2.8)'.format(201, response.status_code))

        body = response.json()

        object_id = body['objectID']

        logging.info('Created file "{0}" with object ID: {1}'.format(file_name, object_id))

        _assert(conf['headers']['Content-Type'] in response.headers['Content-Type'],
                'Expected HTTP Content-Type "{0}" got "{1}" (8.2.6)'.format(conf['headers']['Content-Type'],
                                                                            response.headers['Content-Type']))
        _assert(response.headers['X-CDMI-Specification-Version'] == conf['headers']['X-CDMI-Specification-Version'],
                'Expected version "{0}" got "{1}" (8.2.6)'.format(conf['headers']['X-CDMI-Specification-Version'],
                                                                  response.headers['X-CDMI-Specification-Version']))

        for field in create_data_object_response_fields:
            _assert(field in body, 'Data object response is missing mandatory field "{0}" (8.2.7)'.format(field))

        _assert(conf['headers']['Content-Type'] in body['objectType'],
                'Expected CDMI objectType "{0}" got "{1}" (8.2.7)'.format(conf['headers']['Content-Type'],
                                                                          body['objectType']))
        _assert(body['objectName'] == file_name,
                'Expected CDMI objectName "{0}" got "{1}" (8.2.7)'.format(file_name, body['objectName']))
        _assert(body['parentURI'] == '/{0}/'.format(conf['object-container']),
                'Expected CDMI parentURI "{0}" got "{1}" (8.2.7)'.format('/{0}/'.format(conf['object-container']),
                                                                         body['parentURI']))
        _assert(body['mimetype'] == 'text/plain',
                'Expected CDMI mimetype "{0}" got "{1}" (8.2.7)'.format('text/plain', body['mimetype']))
        _assert(body['completionStatus'] == 'Complete',
                'Expected CDMI completionStatus "{0}" got "{1}" (8.2.7)'.format('Complete', body['completionStatus']))

        if 'metadata' in data:
            _assert(utils.compare_metadata(data['metadata'], body['metadata']),
                    'User-supplied metadata does\'t match.')


def test_create_non_cdmi_content_by_name():
    """|sect| `CDMI_8.3`_ Tests valid uploading of a non CDMI-encoded text file to the root collection.

    :command: ``PUT /<file_name>.txt``

    :asserts: HTTP status code == 201 |sect| `CDMI_8.3.7`_
    """
    conf = get_config('CDMI')
    conf['headers']['Content-Type'] = 'text/plain'
    del conf['headers']['X-CDMI-Specification-Version']
    file_name = shortuuid.uuid() + '.txt'

    with object_context(file_name, utils.session, conf, sample_text) as response, assert_context() as _assert:
        _assert(response.status_code == 201,
                'Expected HTTP status code {0} got {1} (8.3.7)'.format(201, response.status_code))


def test_read_cdmi_content_by_name():
    """|sect| `CDMI_8.4`_ Tests the reading of a data object using CDMI content type.

    :command: ``GET /<file_name>.txt``

    :asserts:
        * HTTP status code == 200 |sect| `CDMI_8.4.7`_
        * HTTP Content-Type == 'application/cdmi-object' |sect| `CDMI_8.4.5`_
        * HTTP X-CDMI-Specification-Version == '1.0.2' |sect| `CDMI_8.4.5`_
        * Presence of mandatory CDMI fields in response |sect| `CDMI_8.4.6`_ domainURI is currently being treated as
          optional because |sect| `CDMI_12.1.1`_ says it is.
        * CDMI objectType == 'application/cdmi-object' |sect| `CDMI_8.4.6`_
        * CDMI objectName == uploaded file name |sect| `CDMI_8.4.6`_
        * CDMI parentURI == '/testrunner/' |sect| `CDMI_8.4.6`_
        * CDMI mimetype == 'text/plain' |sect| `CDMI_8.4.6`_
        * CDMI completionStatus == 'Complete' |sect| `CDMI_8.4.6`_
        * CDMI valuerange starts at 0
        * CDMI valuerange == content length
        * CDMI value == sample text
    """
    conf = get_config('CDMI')
    conf['headers']['Accept'] = 'application/cdmi-object'
    conf['headers']['Content-Type'] = 'application/cdmi-object'
    file_name = shortuuid.uuid() + '.txt'
    params = {
        'mimetype': 'text/plain',
        'metadata': {},
        'valuetransferencoding': 'base64',
        'value': b64encode(sample_text)
    }

    with object_context(file_name, utils.session, conf, json.dumps(params)) as create_response, \
            assert_context() as _assert:
        _assert(create_response.status_code == 201,
                'Expected HTTP status code {0} got {1} (8.3.7)'.format(201, create_response.status_code))

        response = utils.session.get('{0}/{1}/{2}'.format(conf['host'], conf['object-container'], file_name),
                                     headers=conf['headers'])

        log_request(response)

        _assert(response.status_code == 200,
                'Expected HTTP status code {0} got {1} (8.4.7)'.format(200, response.status_code))
        _assert(conf['headers']['Content-Type'] in response.headers['Content-Type'],
                'Expected HTTP Content-Type "{0}" got "{1}" (8.4.5)'.format(conf['headers']['Content-Type'],
                                                                            response.headers['Content-Type']))
        _assert(response.headers['X-CDMI-Specification-Version'] == conf['headers']['X-CDMI-Specification-Version'],
                'Expected version "{0}" got "{1}" (8.4.5)'.format(conf['headers']['X-CDMI-Specification-Version'],
                                                                  response.headers['X-CDMI-Specification-Version']))

        body = response.json()

        for field in update_data_object_response_fields:
            _assert(field in body, 'Data object response is missing mandatory field "{0}" (8.4.6)'.format(field))

        _assert(conf['headers']['Content-Type'] in body['objectType'],
                'Expected CDMI objectType "{0}" got "{1}" (8.4.6)'.format(conf['headers']['Content-Type'],
                                                                          body['objectType']))
        _assert(body['objectName'] == file_name,
                'Expected CDMI objectName "{0}" got "{1}" (8.4.6)'.format(file_name, body['objectName']))
        _assert(body['parentURI'] == '/{0}/'.format(conf['object-container']),
                'Expected CDMI parentURI "{0}" got "{1}" (8.4.6)'.format('/{0}/'.format(conf['object-container']),
                                                                         body['parentURI']))
        _assert(body['mimetype'] == 'text/plain',
                'Expected CDMI mimetype "{0}" got "{1}" (8.4.6)'.format('text/plain', body['mimetype']))
        _assert(body['completionStatus'] == 'Complete',
                'Expected CDMI completionStatus "{0}" got "{1}" (8.4.6)'.format('Complete', body['completionStatus']))

        value = b64decode(body['value'])
        value_range = body['valuerange'].split('-')
        value_range_start = int(value_range[0])
        value_range_end = int(value_range[1])

        _assert(value_range_start == 0,
                'Entire value range was requested, but I got a starting point of {0}'.format(value_range_start))
        _assert(value_range_end - value_range_start == len(value),
                'The returned valuerange is not the same as the length of the returned data. '
                'Expected {0}, got {1}.'.format(value_range_end - value_range_start, len(value)))
        _assert(value == sample_text,
                'Returned data is not what was expected.\n'
                'Expected: "{0}"\nGot: "{1}"'.format(sample_text, value))


def test_read_cdmi_content_by_id():
    """|sect| `CDMI_8.4`_ Tests the reading of a data object using CDMI content type with its object ID.

    :command: ``GET /cdmi_objectid/<objectID>``

    :asserts:
        * HTTP status code == 200 |sect| `CDMI_8.4.7`_
        * HTTP Content-Type == 'application/cdmi-object' |sect| `CDMI_8.4.5`_
        * HTTP X-CDMI-Specification-Version == '1.0.2' |sect| `CDMI_8.4.5`_
        * Presence of mandatory CDMI fields in response |sect| `CDMI_8.4.6`_ domainURI is currently being treated as
          optional because |sect| `CDMI_12.1.1`_ says it is.
        * CDMI objectType == 'application/cdmi-object' |sect| `CDMI_8.4.6`_
        * CDMI objectName == uploaded file name |sect| `CDMI_8.4.6`_
        * CDMI parentURI == '/testrunner/' |sect| `CDMI_8.4.6`_
        * CDMI mimetype == 'text/plain' |sect| `CDMI_8.4.6`_
        * CDMI completionStatus == 'Complete' |sect| `CDMI_8.4.6`_
        * CDMI valuerange starts at 0
        * CDMI valuerange == content length
        * CDMI value == sample text
    """
    conf = get_config('CDMI')
    conf['headers']['Accept'] = 'application/cdmi-object'
    conf['headers']['Content-Type'] = 'application/cdmi-object'
    file_name = shortuuid.uuid() + '.txt'
    params = {
        'mimetype': 'text/plain',
        'metadata': {},
        'valuetransferencoding': 'base64',
        'value': b64encode(sample_text)
    }

    with object_context(file_name, utils.session, conf, json.dumps(params)) as create_response, \
            assert_context() as _assert:
        _assert(create_response.status_code == 201,
                'Expected HTTP status code {0} got {1} (8.3.7)'.format(201, create_response.status_code))

        body = create_response.json()
        object_id = body['objectID']
        logging.info('ObjectID = {0}'.format(object_id))

        response = utils.session.get('{0}/cdmi_objectid/{1}'.format(conf['host'], object_id), headers=conf['headers'])

        log_request(response)

        _assert(response.status_code == 200,
                'Expected HTTP status code {0} got {1} (8.4.7)'.format(200, response.status_code))
        _assert(conf['headers']['Content-Type'] in response.headers['Content-Type'],
                'Expected HTTP Content-Type "{0}" got "{1}" (8.4.5)'.format(conf['headers']['Content-Type'],
                                                                            response.headers['Content-Type']))
        _assert(response.headers['X-CDMI-Specification-Version'] == conf['headers']['X-CDMI-Specification-Version'],
                'Expected version "{0}" got "{1}" (8.4.5)'.format(conf['headers']['X-CDMI-Specification-Version'],
                                                                  response.headers['X-CDMI-Specification-Version']))

        body = response.json()

        for field in update_data_object_response_fields:
            _assert(field in body, 'Data object response is missing mandatory field "{0}" (8.4.6)'.format(field))

        _assert(conf['headers']['Content-Type'] in body['objectType'],
                'Expected CDMI objectType "{0}" got "{1}" (8.4.6)'.format(conf['headers']['Content-Type'],
                                                                          body['objectType']))
        _assert(body['objectName'] == file_name,
                'Expected CDMI objectName "{0}" got "{1}" (8.4.6)'.format(file_name, body['objectName']))
        _assert(body['objectID'] == object_id,
                'Expected CDMI objectID "{0}" got "{1}" (8.4.6)'.format(object_id, body['objectID']))
        _assert(body['parentURI'] == '/{0}/'.format(conf['object-container']),
                'Expected CDMI parentURI "{0}" got "{1}" (8.4.6)'.format('/{0}/'.format(conf['object-container']),
                                                                         body['parentURI']))
        _assert(body['mimetype'] == 'text/plain',
                'Expected CDMI mimetype "{0}" got "{1}" (8.4.6)'.format('text/plain', body['mimetype']))
        _assert(body['completionStatus'] == 'Complete',
                'Expected CDMI completionStatus "{0}" got "{1}" (8.4.6)'.format('Complete', body['completionStatus']))

        value = b64decode(body['value'])
        value_range = body['valuerange'].split('-')
        value_range_start = int(value_range[0])
        value_range_end = int(value_range[1])

        _assert(value_range_start == 0,
                'Entire value range was requested, but I got a starting point of {0}'.format(value_range_start))
        _assert(value_range_end - value_range_start == len(value),
                'The returned valuerange is not the same as the length of the returned data. '
                'Expected {0}, got {1}.'.format(value_range_end - value_range_start, len(value)))
        _assert(value == sample_text,
                'Returned data is not what was expected.\n'
                'Expected: "{0}"\nGot: "{1}"'.format(sample_text, value))


def test_read_non_cdmi_content_by_name():
    """|sect| `CDMI_8.5`_ Tests reading of a non CDMI-encoded text file.

    :command: ``GET /<file_name>.txt``

    :asserts:
        * HTTP status code == 200 |sect| `CDMI_8.5.7`_
        * Presence of HTTP Content-Type |sect| `CDMI_8.5.5`_
        * HTTP Content-Type == 'application/cdmi-object' |sect| `CDMI_8.5.5`_
        * HTTP body == sample text
    """
    conf = get_config('CDMI')
    conf['headers']['Accept'] = 'application/cdmi-object'
    conf['headers']['Content-Type'] = 'application/cdmi-object'
    file_name = shortuuid.uuid() + '.txt'
    params = {
        'mimetype': 'text/plain',
        'metadata': {},
        'valuetransferencoding': 'base64',
        'value': b64encode(sample_text)
    }

    with object_context(file_name, utils.session, conf, json.dumps(params)) as create_response, \
            assert_context() as _assert:
        _assert(create_response.status_code == 201,
                'Expected HTTP status code {0} got {1} (8.3.7)'.format(201, create_response.status_code))

        conf['headers']['Content-Type'] = 'text/plain'
        del conf['headers']['X-CDMI-Specification-Version']
        del conf['headers']['Accept']

        response = utils.session.get('{0}/{1}/{2}'.format(conf['host'], conf['object-container'], file_name))

        log_request(response)

        _assert(response.status_code == 200,
                'Expected HTTP status code {0} got {1} (8.3.7)'.format(200, response.status_code))
        _assert('Content-Type' in response.headers,
                'Couldn\'t find "Content-Type" in the response headers, '
                'expected "{0}" (8.5.5)'.format(conf['headers']['Content-Type']))
        _assert(conf['headers']['Content-Type'] in response.headers['Content-Type'],
                'Expected HTTP Content-Type "{0}" got "{1}" (8.5.5)'.format(conf['headers']['Content-Type'],
                                                                            response.headers['Content-Type']))
        _assert(response.text == sample_text,
                'Returned data is not what was expected.\n'
                'Expected: "{0}"\nGot: "{1}"'.format(sample_text, response.text))


def test_read_non_cdmi_content_by_id():
    """|sect| `CDMI_8.5`_ Tests reading of a non CDMI-encoded text file with its object ID.

    :command: ``GET /cdmi_objectid/<objectID>``

    :asserts:
        * HTTP status code == 200 |sect| `CDMI_8.5.7`_
        * HTTP Content-Type == 'application/cdmi-object' |sect| `CDMI_8.5.5`_
        * HTTP body == sample text
    """
    conf = get_config('CDMI')
    conf['headers']['Accept'] = 'application/cdmi-object'
    conf['headers']['Content-Type'] = 'application/cdmi-object'
    file_name = shortuuid.uuid() + '.txt'
    params = {
        'mimetype': 'text/plain',
        'metadata': {},
        'valuetransferencoding': 'base64',
        'value': b64encode(sample_text)
    }

    with object_context(file_name, utils.session, conf, json.dumps(params)) as create_response, \
            assert_context() as _assert:
        _assert(create_response.status_code == 201,
                'Expected HTTP status code {0} got {1} (8.3.7)'.format(201, create_response.status_code))

        body = create_response.json()
        object_id = body['objectID']

        conf['headers']['Content-Type'] = 'text/plain'
        del conf['headers']['X-CDMI-Specification-Version']
        del conf['headers']['Accept']

        response = utils.session.get('{0}/cdmi_objectid/{1}'.format(conf['host'], object_id))

        log_request(response)

        _assert(response.status_code == 200,
                'Expected HTTP status code {0} got {1} (8.5.7)'.format(200, response.status_code))
        _assert(conf['headers']['Content-Type'] in response.headers['Content-Type'],
                'Expected HTTP Content-Type "{0}" got "{1}" (8.5.5)'.format(conf['headers']['Content-Type'],
                                                                            response.headers['Content-Type']))
        _assert(response.text == sample_text,
                'Returned data is not what was expected.\n'
                'Expected: "{0}"\nGot: "{1}"'.format(sample_text, response.text))


def test_update_cdmi_content_by_name():
    """|sect| `CDMI_8.6`_ Tests valid update of a CDMI-encoded text file to the root collection. Then reads the
    contents of the file back from the CDMI server.

    :command: ``PUT /<file_name>.txt``

    :tests:
        * CDMI mimetype = text/plain
        * No CDMI mimetype

    :asserts:
        * HTTP status code == 204 |sect| `CDMI_8.6.7`_
        * HTTP status code == 200 |sect| `CDMI_8.4.7`_ (When reading file contents back)
        * returned object ID is the same as the original file's object ID |sect| `CDMI_8.6.1`_
        * CDMI value == sample text
    """
    cases = [
        {
            'name': 'CDMI mimetype: text/plain',
            'data': {
                'mimetype': 'text/plain',
                'metadata': {},
                'valuetransferencoding': 'base64',
                'value': b64encode(replacement_sample_text)
            },
            'params': None
        },
        {
            'name': 'No CDMI mimetype',
            'data': {
                'metadata': {},
                'valuetransferencoding': 'base64',
                'value': b64encode(replacement_sample_text)
            },
            'params': None
        }
    ]

    for case in cases:
        f = partial(_update_cdmi_content_by_name, case['data'], case['params'])
        test_update_cdmi_content_by_name.__name__ = 'test_update_cdmi_content_by_name <{0}>'.format(case['name'])
        yield f


def _update_cdmi_content_by_name(data, params):
    conf = get_config('CDMI')
    conf['headers']['Accept'] = 'application/cdmi-object'
    conf['headers']['Content-Type'] = 'application/cdmi-object'
    file_name = shortuuid.uuid() + '.txt'

    create_data = {
        'mimetype': 'text/plain',
        'metadata': {},
        'valuetransferencoding': 'base64',
        'value': b64encode(sample_text)
    }

    with object_context(file_name, utils.session, conf, json.dumps(create_data)) as create_response, \
            assert_context() as _assert:
        _assert(create_response.status_code == 201,
                'Expected HTTP status code {0} got {1} (8.3.7)'.format(201, create_response.status_code))

        body = create_response.json()
        object_id = body['objectID']

        put_response = utils.session.put('{0}/{1}/{2}'.format(conf['host'], conf['object-container'], file_name),
                                         headers=conf['headers'],
                                         data=json.dumps(data),
                                         params=params)

        log_request(put_response)

        _assert(put_response.status_code == 204,
                'Expected HTTP status code {0} got {1} (8.6.7)'.format(204, put_response.status_code))

        # Read the object back.
        response = utils.session.get('{0}/{1}/{2}'.format(conf['host'], conf['object-container'], file_name),
                                     headers=conf['headers'])

        log_request(response)

        _assert(response.status_code == 200,
                'Expected HTTP status code {0} got {1} (8.4.7)'.format(200, response.status_code))

        body = response.json()

        _assert(body['objectID'] == object_id,
                'Expected CDMI objectID "{0}" got "{1}" (8.4.6)'.format(object_id, body['objectID']))

        value = b64decode(body['value'])
        _assert(value == replacement_sample_text,
                'Returned data is not what was expected.\n'
                'Expected: "{0}"\nGot: "{1}"'.format(replacement_sample_text, value))


def test_update_cdmi_content_by_id():
    """|sect| `CDMI_8.6`_ Tests valid update of a CDMI-encoded text file to the root collection, with its object ID.
    Then reads the contents of the file back from the CDMI server.

    :command: ``PUT /cdmi_objectid/<objectID>``

    :asserts:
        * HTTP status code == 204 |sect| `CDMI_8.6.7`_
        * HTTP status code == 200 |sect| `CDMI_8.4.7`_ (When reading file contents back)
        * returned object ID is the same as the original file's object ID |sect| `CDMI_8.6.1`_
        * CDMI value == sample text
    """
    conf = get_config('CDMI')
    conf['headers']['Accept'] = 'application/cdmi-object'
    conf['headers']['Content-Type'] = 'application/cdmi-object'
    file_name = shortuuid.uuid() + '.txt'
    params = {
        'mimetype': 'text/plain',
        'metadata': {},
        'valuetransferencoding': 'base64',
        'value': b64encode(sample_text)
    }

    with object_context(file_name, utils.session, conf, json.dumps(params)) as create_response, \
            assert_context() as _assert:
        _assert(create_response.status_code == 201,
                'Expected HTTP status code {0} got {1} (8.3.7)'.format(201, create_response.status_code))

        body = create_response.json()
        object_id = body['objectID']

        # Update the object.
        params = {
            'metadata': {},
            'valuetransferencoding': 'base64',
            'value': b64encode(replacement_sample_text)
        }

        response = utils.session.put('{0}/cdmi_objectid/{1}'.format(conf['host'], object_id),
                                     headers=conf['headers'],
                                     data=json.dumps(params))

        log_request(response)

        _assert(response.status_code == 204,
                'Expected HTTP status code {0} got {1} (8.6.7)'.format(204, response.status_code))

        # Read the object back.
        response = utils.session.get('{0}/{1}/{2}'.format(conf['host'], conf['object-container'], file_name),
                                     headers=conf['headers'])

        log_request(response)

        _assert(response.status_code == 200,
                'Expected HTTP status code {0} got {1} (8.4.7)'.format(200, response.status_code))

        body = response.json()

        _assert(body['objectID'] == object_id,
                'Expected CDMI objectID "{0}" got "{1}" (8.4.6)'.format(object_id, body['objectID']))

        value = b64decode(body['value'])
        _assert(value == replacement_sample_text,
                'Returned data is not what was expected.\n'
                'Expected: "{0}"\nGot: "{1}"'.format(replacement_sample_text, value))


def test_update_non_cdmi_content_by_name():
    """|sect| `CDMI_8.7`_ Tests valid update of a non CDMI-encoded text file to the root collection. Then reads the
    contents of the file back from the CDMI server.

    :command: ``PUT /<file_name>.txt``

    :asserts:
        * HTTP status code == 204 |sect| `CDMI_8.7.7`_
        * HTTP status code == 200 |sect| `CDMI_8.4.7`_ (When reading file contents back)
        * returned object ID is the same as the original file's object ID |sect| `CDMI_8.7.1`_
        * CDMI value == sample text
    """
    conf = get_config('CDMI')
    conf['headers']['Accept'] = 'application/cdmi-object'
    conf['headers']['Content-Type'] = 'application/cdmi-object'
    file_name = shortuuid.uuid() + '.txt'
    params = {
        'mimetype': 'text/plain',
        'metadata': {},
        'valuetransferencoding': 'base64',
        'value': b64encode(sample_text)
    }

    with object_context(file_name, utils.session, conf, json.dumps(params)) as create_response, \
            assert_context() as _assert:
        _assert(create_response.status_code == 201,
                'Expected HTTP status code {0} got {1} (8.3.7)'.format(201, create_response.status_code))

        body = create_response.json()
        object_id = body['objectID']

        # Update the object.
        conf['headers']['Content-Type'] = 'text/plain'
        del conf['headers']['X-CDMI-Specification-Version']
        del conf['headers']['Accept']

        response = utils.session.put('{0}/{1}/{2}'.format(conf['host'], conf['object-container'], file_name),
                                     headers=conf['headers'],
                                     data=replacement_sample_text)

        log_request(response)

        _assert(response.status_code == 204,
                'Expected HTTP status code {0} got {1} (8.7.7)'.format(204, response.status_code))

        # Read the object back.
        conf['headers']['Accept'] = 'application/cdmi-object'
        conf['headers']['X-CDMI-Specification-Version'] = \
            utils.config['CDMI']['headers']['X-CDMI-Specification-Version']
        response = utils.session.get('{0}/{1}/{2}'.format(conf['host'], conf['object-container'], file_name),
                                     headers=conf['headers'])

        log_request(response)

        _assert(response.status_code == 200,
                'Expected HTTP status code {0} got {1} (8.4.7)'.format(200, response.status_code))

        body = response.json()

        _assert(body['objectID'] == object_id,
                'Expected CDMI objectID "{0}" got "{1}" (8.4.6)'.format(object_id, body['objectID']))

        value = b64decode(body['value'])
        _assert(value == replacement_sample_text,
                'Returned data is not what was expected.\n'
                'Expected: "{0}"\nGot: "{1}"'.format(replacement_sample_text, value))


def test_update_non_cdmi_content_by_id():
    """|sect| `CDMI_8.7`_ Tests valid update of a non CDMI-encoded text file to the root collection, with its object ID.
    Then reads the contents of the file back from the CDMI server.

    :command: ``PUT /cdmi_objectid/<objectID>``

    :asserts:
        * HTTP status code == 204 |sect| `CDMI_8.7.7`_
        * HTTP status code == 200 |sect| `CDMI_8.4.7`_ (When reading file contents back)
        * returned object ID is the same as the original file's object ID |sect| `CDMI_8.7.1`_
        * CDMI value == sample text
    """
    conf = get_config('CDMI')
    conf['headers']['Accept'] = 'application/cdmi-object'
    conf['headers']['Content-Type'] = 'application/cdmi-object'
    file_name = shortuuid.uuid() + '.txt'
    params = {
        'mimetype': 'text/plain',
        'metadata': {},
        'valuetransferencoding': 'base64',
        'value': b64encode(sample_text)
    }

    with object_context(file_name, utils.session, conf, json.dumps(params)) as create_response, \
            assert_context() as _assert:
        _assert(create_response.status_code == 201,
                'Expected HTTP status code {0} got {1} (8.3.7)'.format(201, create_response.status_code))

        body = create_response.json()
        object_id = body['objectID']

        # Update the object.
        conf['headers']['Content-Type'] = 'text/plain'
        del conf['headers']['X-CDMI-Specification-Version']
        del conf['headers']['Accept']

        response = utils.session.put('{0}/cdmi_objectid/{1}'.format(conf['host'], object_id),
                                     headers=conf['headers'],
                                     data=replacement_sample_text)

        log_request(response)

        _assert(response.status_code == 204,
                'Expected HTTP status code {0} got {1} (8.7.7)'.format(204, response.status_code))

        # Read the object back.
        conf['headers']['Accept'] = 'application/cdmi-object'
        conf['headers']['X-CDMI-Specification-Version'] = \
            utils.config['CDMI']['headers']['X-CDMI-Specification-Version']
        response = utils.session.get('{0}/{1}/{2}'.format(conf['host'], conf['object-container'], file_name),
                                     headers=conf['headers'])

        log_request(response)

        _assert(response.status_code == 200,
                'Expected HTTP status code {0} got {1} (8.4.7)'.format(200, response.status_code))

        body = response.json()

        _assert(body['objectID'] == object_id,
                'Expected CDMI objectID "{0}" got "{1}" (8.4.6)'.format(object_id, body['objectID']))

        value = b64decode(body['value'])
        _assert(value == replacement_sample_text,
                'Returned data is not what was expected.\n'
                'Expected: "{0}"\nGot: "{1}"'.format(replacement_sample_text, value))


def test_delete_cdmi_content_by_name():
    """|sect| `CDMI_8.8`_ Tests valid deletion of a CDMI-encoded text file from the root collection.

    :command: ``DELETE /<file_name>.txt``

    :asserts: HTTP status code == 204 |sect| `CDMI_8.8.7`_
    """
    conf = get_config('CDMI')
    conf['headers']['Accept'] = 'application/cdmi-object'
    conf['headers']['Content-Type'] = 'application/cdmi-object'
    file_name = shortuuid.uuid() + '.txt'
    params = {
        'mimetype': 'text/plain',
        'metadata': {},
        'valuetransferencoding': 'base64',
        'value': b64encode(sample_text)
    }

    with object_context(file_name, utils.session, conf, json.dumps(params)) as create_response, \
            assert_context() as _assert:
        _assert(create_response.status_code == 201,
                'Expected HTTP status code {0} got {1} (8.3.7)'.format(201, create_response.status_code))

        response = utils.session.delete('{0}/{1}/{2}'.format(conf['host'], conf['object-container'], file_name),
                                        headers=conf['headers'])

        log_request(response)

        _assert(response.status_code == 204,
                'Expected HTTP status code {0} got {1} (8.8.7)'.format(204, response.status_code))


def test_delete_cdmi_content_by_id():
    """|sect| `CDMI_8.8`_ Tests valid deletion of a CDMI-encoded text file from the root collection by its object ID.

    :command: ``DELETE /cdmi_objectid/<objectID>``

    :asserts: HTTP status code == 204 |sect| `CDMI_8.8.7`_
    """
    conf = get_config('CDMI')
    conf['headers']['Accept'] = 'application/cdmi-object'
    conf['headers']['Content-Type'] = 'application/cdmi-object'
    file_name = shortuuid.uuid() + '.txt'
    params = {
        'mimetype': 'text/plain',
        'metadata': {},
        'valuetransferencoding': 'base64',
        'value': b64encode(sample_text)
    }

    with object_context(file_name, utils.session, conf, json.dumps(params)) as create_response, \
            assert_context() as _assert:
        _assert(create_response.status_code == 201,
                'Expected HTTP status code {0} got {1} (8.3.7)'.format(201, create_response.status_code))

        body = create_response.json()
        object_id = body['objectID']

        response = utils.session.delete('{0}/cdmi_objectid/{1}'.format(conf['host'], object_id),
                                        headers=conf['headers'])

        log_request(response)

        _assert(response.status_code == 204,
                'Expected HTTP status code {0} got {1} (8.8.7)'.format(204, response.status_code))


def test_delete_non_cdmi_content_by_name():
    """|sect| `CDMI_8.9`_ Tests valid deletion of a non CDMI-encoded text file from the root collection.

    :command: ``DELETE /<file_name>.txt``

    :asserts: HTTP status code == 204 |sect| `CDMI_8.9.7`_
    """
    conf = get_config('CDMI')
    conf['headers']['Accept'] = 'application/cdmi-object'
    conf['headers']['Content-Type'] = 'application/cdmi-object'
    file_name = shortuuid.uuid() + '.txt'
    params = {
        'mimetype': 'text/plain',
        'metadata': {},
        'valuetransferencoding': 'base64',
        'value': b64encode(sample_text)
    }

    with object_context(file_name, utils.session, conf, json.dumps(params)) as create_response, \
            assert_context() as _assert:
        _assert(create_response.status_code == 201,
                'Expected HTTP status code {0} got {1} (8.3.7)'.format(201, create_response.status_code))

        del conf['headers']['X-CDMI-Specification-Version']
        del conf['headers']['Accept']

        response = utils.session.delete('{0}/{1}/{2}'.format(conf['host'], conf['object-container'], file_name),
                                        headers=conf['headers'])

        log_request(response)

        _assert(response.status_code == 204,
                'Expected HTTP status code {0} got {1} (8.9.7)'.format(204, response.status_code))


def test_delete_non_cdmi_content_by_id():
    """|sect| `CDMI_8.9`_ Tests valid deletion of a non CDMI-encoded text file from the root collection by its object
    ID.

    :command: ``DELETE /cdmi_objectid/<objectID>``

    :asserts: HTTP status code == 204 |sect| `CDMI_8.9.7`_
    """
    conf = get_config('CDMI')
    conf['headers']['Accept'] = 'application/cdmi-object'
    conf['headers']['Content-Type'] = 'application/cdmi-object'
    file_name = shortuuid.uuid() + '.txt'
    params = {
        'mimetype': 'text/plain',
        'metadata': {},
        'valuetransferencoding': 'base64',
        'value': b64encode(sample_text)
    }

    with object_context(file_name, utils.session, conf, json.dumps(params)) as create_response, \
            assert_context() as _assert:
        _assert(create_response.status_code == 201,
                'Expected HTTP status code {0} got {1} (8.3.7)'.format(201, create_response.status_code))

        body = create_response.json()
        object_id = body['objectID']

        del conf['headers']['X-CDMI-Specification-Version']

        response = utils.session.delete('{0}/cdmi_objectid/{1}'.format(conf['host'], object_id),
                                        headers=conf['headers'])

        log_request(response)

        _assert(response.status_code == 204,
                'Expected HTTP status code {0} got {1} (8.8.7)'.format(204, response.status_code))


def test_read_non_existent_file_by_name():
    """|sect| `CDMI_8.4`_ Tests the reading of a data object that doesn't exist using CDMI content type.

    :command: ``GET /<file_name>.does_not_exist``

    :asserts: HTTP status code == 404 |sect| `CDMI_8.4.7`_
    """
    with assert_context() as _assert:
        conf = get_config('CDMI')
        conf['headers']['Accept'] = 'application/cdmi-object'
        conf['headers']['Content-Type'] = 'application/cdmi-object'
        file_name = shortuuid.uuid() + '.does_not_exist'

        response = utils.session.get('{0}/{1}/{2}'.format(conf['host'], conf['object-container'], file_name),
                                     headers=conf['headers'])

        log_request(response)

        _assert(response.status_code == 404,
                'Expected HTTP status code {0} got {1} (8.4.7)'.format(404, response.status_code))


def test_read_non_existent_file_by_id():
    """|sect| `CDMI_8.4`_ Tests the reading of a data object by an invalid ID using CDMI content type.

    :command: ``GET /cdmi_objectid/this_id_does_not_exist``

    :asserts: HTTP status code == 404 |sect| `CDMI_8.4.7`_
    """
    with assert_context() as _assert:
        conf = get_config('CDMI')
        conf['headers']['Accept'] = 'application/cdmi-object'
        conf['headers']['Content-Type'] = 'application/cdmi-object'

        response = utils.session.get('{0}/cdmi_objectid/this_id_does_not_exist'.format(conf['host']),
                                     headers=conf['headers'])

        log_request(response)

        _assert(response.status_code == 400,
                'Expected HTTP status code {0} got {1} (8.4.7)'.format(400, response.status_code))


def test_update_non_existent_file_by_id():
    """|sect| `CDMI_8.6`_ Tests the updating of a data object by an invalid ID using CDMI content type.

    :command: ``PUT /cdmi_objectid/this_id_does_not_exist``

    :asserts: HTTP status code == 404 |sect| `CDMI_8.6.7`_
    """
    with assert_context() as _assert:
        conf = get_config('CDMI')
        conf['headers']['Accept'] = 'application/cdmi-object'
        conf['headers']['Content-Type'] = 'application/cdmi-object'

        params = {
            'metadata': {},
            'valuetransferencoding': 'base64',
            'value': b64encode(sample_text)
        }

        response = utils.session.put('{0}/cdmi_objectid/0000A4EF0028440D000000000000000000000000000000000000000000000'
                                     '00000000000DEADBEEF'.format(conf['host']),
                                     headers=conf['headers'],
                                     data=json.dumps(params))

        log_request(response)

        _assert(response.status_code == 404,
                'Expected HTTP status code {0} got {1} (8.6.7)'.format(404, response.status_code))


def test_delete_non_existent_file_by_name():
    """|sect| `CDMI_8.8`_ Tests the deleting of a data object that doesn't exist using CDMI content type.

    :command: ``DELETE /<file_name>.does_not_exist``

    :asserts: HTTP status code == 404 |sect| `CDMI_8.8.7`_
    """
    with assert_context() as _assert:
        conf = get_config('CDMI')
        conf['headers']['Accept'] = 'application/cdmi-object'
        conf['headers']['Content-Type'] = 'application/cdmi-object'
        file_name = shortuuid.uuid() + '.does_not_exist'

        response = utils.session.delete('{0}/{1}/{2}'.format(conf['host'], conf['object-container'], file_name),
                                        headers=conf['headers'])

        log_request(response)

        _assert(response.status_code == 404,
                'Expected HTTP status code {0} got {1} (8.8.7)'.format(404, response.status_code))


def test_delete_file_by_invalid_id():
    """|sect| `CDMI_8.8`_ Tests the deleting of a data object by an invalid ID using CDMI content type.

    :command: ``GET /cdmi_objectid/this_id_does_not_exist``

    :asserts: HTTP status code == 404 |sect| `CDMI_8.8.7`_
    """
    with assert_context() as _assert:
        conf = get_config('CDMI')
        conf['headers']['Accept'] = 'application/cdmi-object'
        conf['headers']['Content-Type'] = 'application/cdmi-object'

        response = utils.session.delete('{0}/cdmi_objectid/this_id_does_not_exist'.format(conf['host']),
                                        headers=conf['headers'])

        log_request(response)

        _assert(response.status_code == 400,
                'Expected HTTP status code {0} got {1} (8.8.7)'.format(400, response.status_code))


def test_delete_non_existent_file_by_id():
    """|sect| `CDMI_8.8`_ Tests the deleting of a data object by a valid but non-existent ID using CDMI content type.

    :command: ``GET /cdmi_objectid/DEADBEEFBABEC0C0FAFF1337FA9907DECAF15BADB105F00DB16B00B5DEADC0DEFEE1DEADDABBAD00``

    :asserts: HTTP status code == 404 |sect| `CDMI_8.8.7`_
    """
    with assert_context() as _assert:
        conf = get_config('CDMI')
        conf['headers']['Accept'] = 'application/cdmi-object'
        conf['headers']['Content-Type'] = 'application/cdmi-object'
        bogus_id = '00ADBEEF00500000FAFF1337FA9907DECAF15BADB105F00DB16B00B5DEADC0DEFEE1DEADDABBAD00'
        crc = utils.crc_16(binascii.unhexlify(bogus_id))

        bogus_id_with_good_crc = bogus_id[:12] + hex(crc)[2:] + bogus_id[16:]

        response = utils.session.delete('{0}/cdmi_objectid/{1}'.format(conf['host'], bogus_id_with_good_crc),
                                        headers=conf['headers'])

        log_request(response)

        _assert(response.status_code == 400,
                'Expected HTTP status code {0} got {1} (8.8.7)'.format(400, response.status_code))


def test_delete_non_existent_file_by_id_invalid_crc():
    """|sect| `CDMI_8.8`_ Tests the deleting of a data object by a well-formed but with an invalid CRC using CDMI
    content type.

    :command: ``GET /cdmi_objectid/this_id_does_not_exist``

    :asserts: HTTP status code == 404 |sect| `CDMI_8.8.7`_
    """
    with assert_context() as _assert:
        conf = get_config('CDMI')
        conf['headers']['Accept'] = 'application/cdmi-object'
        conf['headers']['Content-Type'] = 'application/cdmi-object'
        bogus_id_with_bad_crc = 'DEADBEEFBABEC0C0FAFF1337FA9907DECAF15BADB105F00DB16B00B5DEADC0DEFEE1DEADDABBAD00'

        response = utils.session.delete('{0}/cdmi_objectid/{1}'.format(conf['host'], bogus_id_with_bad_crc),
                                        headers=conf['headers'])

        log_request(response)

        _assert(response.status_code == 404,
                'Expected HTTP status code {0} got {1} (8.8.7)'.format(404, response.status_code))


def test_read_range():
    """Tests returning a range of a file."""
    conf = get_config('CDMI')
    conf['headers']['Accept'] = 'application/cdmi-object'
    conf['headers']['Content-Type'] = 'application/cdmi-object'
    file_name = shortuuid.uuid() + '.txt'
    params = {
        'mimetype': 'text/plain',
        'metadata': {},
        'valuetransferencoding': 'base64',
        'value': b64encode(sample_text)
    }

    with object_context(file_name, utils.session, conf, json.dumps(params)) as create_response, \
            assert_context() as _assert:
        _assert(create_response.status_code == 201,
                'Expected HTTP status code {0} got {1} (8.3.7)'.format(201, create_response.status_code))

        body = create_response.json()
        object_id = body['objectID']

        # Read the object back.
        response = utils.session.get('{0}/{1}/{2}'.format(conf['host'], conf['object-container'], file_name),
                                     headers=conf['headers'],
                                     params={'value:19-38': ''})

        log_request(response)

        _assert(response.status_code == 200,
                'Expected HTTP status code {0} got {1} (8.4.7)'.format(200, response.status_code))

        body = response.json()

        _assert(body['objectID'] == object_id,
                'Expected CDMI objectID "{0}" got "{1}" (8.4.6)'.format(object_id, body['objectID']))

        value = b64decode(body['value'])
        _assert(value == sample_text[19:38],
                'Returned data is not what was expected.\n'
                'Expected: "{0}"\nGot: "{1}"'.format(sample_text[19:38], value))
