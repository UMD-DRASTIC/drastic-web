"""The tests are written using Python's `unittest <http://docs.python.org/2/library/unittest.html>`_ framework and
executed through `Nose <http://readthedocs.org/docs/nose/>`_.

Running tests
-------------
Jenkins will report all the failed tests, marking them as failed if they have never been fixed, or regression if they
passed the last time the test was run but not this time.

The output for each failed test will generally be::

    Test <n>: <Failure message> (<CDMI spec reference>)

Where ``<n>`` is the sequential assertion number for the given test, ``<Failure message>`` is an informative message
about what was expected and what was actually returned, and ``<CDMI spec reference>`` is the section of the CDMI
specification that deals with that assertion, where appropriate.

Following the line above will usually be the request (or requests in the case of a multi-part test) headers and body,
and the response headers and body. The bodies will be truncated to 2048 bytes (this can be changed in config.yaml)
for the purposes of reporting if necessary.

Some tests are run multiple times with different parameters using Nose's test generators. The function that does the
testing is called by a wrapper function. By default Nose names each test by its parameters, which can get unwieldy
with large amounts of data, so the test function is created as a Python partial function with all the parameters
bound, and the ``__name__`` of the function is changed to something sane. For example::

    def test_update_cdmi_content_by_name():
        parameters = {
            'CDMI mimetype: text/plain': {
                'mimetype': 'text/plain',
                'metadata': {},
                'valuetransferencoding': 'base64',
                'value': b64encode(sample_text)
            },
            'No CDMI mimetype': {
                'metadata': {},
                'valuetransferencoding': 'base64',
                'value': b64encode(sample_text)
            }
        }

        for title, param in parameters.iteritems():
            f = partial(_update_cdmi_content_by_name, param)
            test_update_cdmi_content_by_name.__name__ = 'test_update_cdmi_content_by_name <{0}>'.format(title)
            yield f


    def _update_cdmi_content_by_name(params):
        ...

Bug reporting
-------------
Bitbucket bug reports should have the full test name for the title followed by the assertion number. E.g.::

    functional_tests.test_data_object.test_update_cdmi_content_by_name:2

The body of the bug report should contain any extra information that might be useful in tracking the bug down, as well
as the full error report as generated by Jenkins.
"""
import logging

import requests
import yaml

from . import utils


def setup_package():
    # Stop the requests module from logging every time it makes a connection. We have our own more detailed logging.
    logging.getLogger('requests').setLevel(logging.WARNING)

    try:
        with open('tests/config.yaml', 'r') as f:
            utils.config = yaml.load(f)
    except IOError:
        with open('config.yaml', 'r') as f:
            utils.config = yaml.load(f)

    utils.session = requests.Session()
    utils.session.verify = utils.config['verify-certificate']