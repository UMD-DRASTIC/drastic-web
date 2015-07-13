import copy
import logging
from contextlib import contextmanager

from django.template import Template

config = {}
session = None

crc_table = (
    0x0000, 0xc0c1, 0xc181, 0x0140, 0xc301, 0x03c0, 0x0280, 0xc241,
    0xc601, 0x06c0, 0x0780, 0xc741, 0x0500, 0xc5c1, 0xc481, 0x0440,
    0xcc01, 0x0cc0, 0x0d80, 0xcd41, 0x0f00, 0xcfc1, 0xce81, 0x0e40,
    0x0a00, 0xcac1, 0xcb81, 0x0b40, 0xc901, 0x09c0, 0x0880, 0xc841,
    0xd801, 0x18c0, 0x1980, 0xd941, 0x1b00, 0xdbc1, 0xda81, 0x1a40,
    0x1e00, 0xdec1, 0xdf81, 0x1f40, 0xdd01, 0x1dc0, 0x1c80, 0xdc41,
    0x1400, 0xd4c1, 0xd581, 0x1540, 0xd701, 0x17c0, 0x1680, 0xd641,
    0xd201, 0x12c0, 0x1380, 0xd341, 0x1100, 0xd1c1, 0xd081, 0x1040,
    0xf001, 0x30c0, 0x3180, 0xf141, 0x3300, 0xf3c1, 0xf281, 0x3240,
    0x3600, 0xf6c1, 0xf781, 0x3740, 0xf501, 0x35c0, 0x3480, 0xf441,
    0x3c00, 0xfcc1, 0xfd81, 0x3d40, 0xff01, 0x3fc0, 0x3e80, 0xfe41,
    0xfa01, 0x3ac0, 0x3b80, 0xfb41, 0x3900, 0xf9c1, 0xf881, 0x3840,
    0x2800, 0xe8c1, 0xe981, 0x2940, 0xeb01, 0x2bc0, 0x2a80, 0xea41,
    0xee01, 0x2ec0, 0x2f80, 0xef41, 0x2d00, 0xedc1, 0xec81, 0x2c40,
    0xe401, 0x24c0, 0x2580, 0xe541, 0x2700, 0xe7c1, 0xe681, 0x2640,
    0x2200, 0xe2c1, 0xe381, 0x2340, 0xe101, 0x21c0, 0x2080, 0xe041,
    0xa001, 0x60c0, 0x6180, 0xa141, 0x6300, 0xa3c1, 0xa281, 0x6240,
    0x6600, 0xa6c1, 0xa781, 0x6740, 0xa501, 0x65c0, 0x6480, 0xa441,
    0x6c00, 0xacc1, 0xad81, 0x6d40, 0xaf01, 0x6fc0, 0x6e80, 0xae41,
    0xaa01, 0x6ac0, 0x6b80, 0xab41, 0x6900, 0xa9c1, 0xa881, 0x6840,
    0x7800, 0xb8c1, 0xb981, 0x7940, 0xbb01, 0x7bc0, 0x7a80, 0xba41,
    0xbe01, 0x7ec0, 0x7f80, 0xbf41, 0x7d00, 0xbdc1, 0xbc81, 0x7c40,
    0xb401, 0x74c0, 0x7580, 0xb541, 0x7700, 0xb7c1, 0xb681, 0x7640,
    0x7200, 0xb2c1, 0xb381, 0x7340, 0xb101, 0x71c0, 0x7080, 0xb041,
    0x5000, 0x90c1, 0x9181, 0x5140, 0x9301, 0x53c0, 0x5280, 0x9241,
    0x9601, 0x56c0, 0x5780, 0x9741, 0x5500, 0x95c1, 0x9481, 0x5440,
    0x9c01, 0x5cc0, 0x5d80, 0x9d41, 0x5f00, 0x9fc1, 0x9e81, 0x5e40,
    0x5a00, 0x9ac1, 0x9b81, 0x5b40, 0x9901, 0x59c0, 0x5880, 0x9841,
    0x8801, 0x48c0, 0x4980, 0x8941, 0x4b00, 0x8bc1, 0x8a81, 0x4a40,
    0x4e00, 0x8ec1, 0x8f81, 0x4f40, 0x8d01, 0x4dc0, 0x4c80, 0x8c41,
    0x4400, 0x84c1, 0x8581, 0x4540, 0x8701, 0x47c0, 0x4680, 0x8641,
    0x8201, 0x42c0, 0x4380, 0x8341, 0x4100, 0x81c1, 0x8081, 0x4040
)


request_template = u"""

**Request URL:** {{ request.url }}

**Request Method:** {{ request.method }}

**Status Code:** {{ response.status_code }}

Request
-------
**Header**
{% for k, v in request.headers.iteritems() %}
* **{{ k }}:** {{ v }}{% endfor %}
{% if request.body %}
**Body**

    {{ request.body|truncate(max_body_length)|indent }}

{% endif %}
Response
--------
**Header**
{% for k, v in response.headers.iteritems() %}
* **{{ k }}:** {{ v }}{% endfor %}
{% if response.content %}
**Body**

    {{ response.content|truncate(max_body_length)|indent }}

{% endif %}
"""


def log_request(response):
    """Pretty-prints the HTTP request and response to logging.INFO in the style of Chrome's developer tools. The
    non-header portions are truncated (to 2048 bytes by default) to avoid spamming the logfile when we upload and
    download large files.

    :param Requests.Response response: A Requests response object.
    """
    template = Template(request_template)
    logging.info(template.render(request=response.request, response=response, max_body_length=config['log-max-size']))


def crc_16(data):
    """Caclulates the CRC-16 checksum of a string of bytes according to the CDMI spec for object IDs in
    |sect| `CDMI_5.11`_

    :param string data: The data to calculate the checksum for.
    :return: The checksum.
    """
    crc = 0

    for c in data:
        crc = (crc_table[(crc ^ ord(c)) & 0xff] ^ (crc >> 8)) & 0xffff

    return crc & 0xffff


@contextmanager
def assert_context():
    counter = [0]

    def _assert(test, message):
        counter[0] += 1
        assert test, 'Test {0}\n======\n{1}\n\n'.format(counter[0], message)

    yield _assert


@contextmanager
def object_context(name, sesh, conf, data=None, params=None):
    """Creates a CDMI object with the given file name, and deletes it when the ``with`` context exits.

    Does no testing of return codes or any sort of validity. It does only call delete if the status code was 201
    however.

    To use it::

        with object_context(u'wibble.txt', session, config, some_data) as response:
            if response.status_code == 201:
                print('Hooray!')

    :param string name: File name of the object to create. This can be a path.
    :param Requests.Session sesh: The create/delete has to be part of a session.
    :param dict conf: Configuration values containing a ``host`` key with the full URL of the host, and a ``headers``
        key containing a dictionary of custom HTTP header fields.
    :param data: (Optional) Dictionary, bytes, or file-like object to send as the body of the object.
    :param params: (optional) Dictionary or bytes to be sent in the query string.

    :rtype: Requests.Response object.
    """
    response = sesh.put('{0}/{1}/{2}'.format(conf['host'], conf['object-container'], name),
                        headers=conf['headers'], data=data, params=params)
    log_request(response)

    try:
        yield response
    except:
        raise
    finally:
        if response.status_code == 201:
            sesh.delete('{0}/{1}/{2}'.format(conf['host'], conf['object-container'], name), headers=conf['headers'])


@contextmanager
def role_context(role_name, sesh, conf):
    response = sesh.post('{0}/roles/{1}'.format(conf['host'], role_name),
                         headers=conf['headers'], auth=(conf['username'], conf['password']))

    log_request(response)

    try:
        yield response
    except:
        raise
    finally:
        if response.status_code == 201:
            sesh.delete('{0}/roles/{1}'.format(conf['host'], role_name),
                        headers=conf['headers'], auth=(conf['username'], conf['password']))


@contextmanager
def user_context(user_name, sesh, conf):
    response = sesh.post('{0}/users/{1}'.format(conf['host'], user_name),
                         headers=conf['headers'], auth=(conf['username'], conf['password']))

    log_request(response)

    try:
        yield response
    except:
        raise
    finally:
        if response.status_code == 201:
            sesh.delete('{0}/users/{1}'.format(conf['host'], user_name),
                        headers=conf['headers'], auth=(conf['username'], conf['password']))


def get_config(section=None):
    """Returns a deep copy of the configuration settings."""
    if section is None:
        return copy.deepcopy(config)
    else:
        return copy.deepcopy(config[section])


def compare_metadata(expected, sample):
    """Compares the keys and values of ``expected`` with the keys and values of ``sample``

    :param dict expected: The dictionary containing the expected metadata.
    :param dict sample: The dictionary of metadata which must be a complete superset of the expected metadata.
    :return: Whether ``expected`` is a complete and equal subset of ``sample``.
    :rtype: bool
    """
    for k, v in expected.items():
        if k not in sample or v != sample[k]:
            return False

    return True