from . import utils
from .utils import log_request, assert_context, get_config, role_context


def test_create_role():
    conf = get_config('authz')

    role_name = 'test_runner'

    with role_context(role_name, utils.session, conf) as response, assert_context() as _assert:
        _assert(response.status_code == 201,
                u'Expected HTTP status code {0} got {1}'.format(201, response.status_code))

        _assert(response.headers['Content-Type'] == 'application/json',
                u'Expected HTTP Content-Type {0} got {1}'.format('application/json', response.headers['Content-Type']))

        body = response.json()

        _assert(body.get('name') == role_name,
                u'Expected authz name "{0}" got "{1}', format(role_name, body.get('name')))

        _assert(body.get('members') == [],
                u'Expected authz members "{0}" got "{1}', format([], body.get('members')))


def test_create_duplicate_role():
    conf = get_config('authz')

    role_name = 'test_runner'

    with role_context(role_name, utils.session, conf) as create_response, assert_context() as _assert:
        _assert(create_response.status_code == 201,
                u'Expected HTTP status code {0} got {1}'.format(201, create_response.status_code))

        response = utils.session.post('{0}/roles/{1}'.format(conf['host'], role_name),
                                      headers=conf['headers'], auth=(conf['username'], conf['password']))

        log_request(response)

        _assert(response.status_code == 409,
                u'Expected HTTP status code {0} got {1}'.format(409, response.status_code))


def test_read_role():
    conf = get_config('authz')

    role_name = 'test_runner'

    with role_context(role_name, utils.session, conf) as create_response, assert_context() as _assert:
        _assert(create_response.status_code == 201,
                u'Expected HTTP status code {0} got {1}'.format(201, create_response.status_code))

        response = utils.session.get('{0}/roles/{1}'.format(conf['host'], role_name),
                                     headers=conf['headers'], auth=(conf['username'], conf['password']))

        log_request(response)

        _assert(response.status_code == 200,
                u'Expected HTTP status code {0} got {1}'.format(200, response.status_code))


def test_read_non_existent_role():
    conf = get_config('authz')

    role_name = 'test_runner'
    bogus_role_name = 'this_is_not_a_role'

    with role_context(role_name, utils.session, conf) as create_response, assert_context() as _assert:
        _assert(create_response.status_code == 201,
                u'Expected HTTP status code {0} got {1}'.format(201, create_response.status_code))

        response = utils.session.get('{0}/roles/{1}'.format(conf['host'], bogus_role_name),
                                     headers=conf['headers'], auth=(conf['username'], conf['password']))

        log_request(response)

        _assert(response.status_code == 404,
                u'Expected HTTP status code {0} got {1}'.format(404, response.status_code))


def test_delete_role():
    conf = get_config('authz')

    role_name = 'test_runner'

    with role_context(role_name, utils.session, conf) as create_response, assert_context() as _assert:
        _assert(create_response.status_code == 201,
                u'Expected HTTP status code {0} got {1}'.format(201, create_response.status_code))

        response = utils.session.delete('{0}/roles/{1}'.format(conf['host'], role_name),
                                        headers=conf['headers'], auth=(conf['username'], conf['password']))

        log_request(response)

        _assert(response.status_code == 204,
                u'Expected HTTP status code {0} got {1}'.format(204, response.status_code))


def test_delete_non_existent_role():
    conf = get_config('authz')

    role_name = 'test_runner'
    bogus_role_name = 'this_is_not_a_role'

    with role_context(role_name, utils.session, conf) as create_response, assert_context() as _assert:
        _assert(create_response.status_code == 201,
                u'Expected HTTP status code {0} got {1}'.format(201, create_response.status_code))

        response = utils.session.delete('{0}/roles/{1}'.format(conf['host'], bogus_role_name),
                                        headers=conf['headers'], auth=(conf['username'], conf['password']))

        log_request(response)

        _assert(response.status_code == 404,
                u'Expected HTTP status code {0} got {1}'.format(404, response.status_code))


def test_delete_role_with_members():
    pass


def test_add_user():
    pass


def test_add_duplicate_user():
    pass


def test_read_user():
    pass


def test_add_user_to_role():
    pass
