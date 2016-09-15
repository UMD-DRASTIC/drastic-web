# Drastic

Drastic is a data management solution written in Python that allows users to upload and archive data resources.  Data is managed in a Cassandra database, and the associated Drastic Agent is responsible for post-processing on uploaded content.

The primary interface to Drastic is the Django application in this repository.


## Installing

Drastic deployment is automated using Ansible. Ensure
your `/etc/ansible/hosts` file contains the following:

```ini
[drastic-databases]
127.0.0.1

[drastic-webservers]
127.0.0.1

[drastic:children]
drastic-databases
drastic-webservers
```

Replace 127.0.0.1 with the address of the server(s) you want to deploy on.

From the command line, run:

`ansible-playbook deploy_standalone.yml`

To install just the web server component, run:

`ansible-playbook webservers.yml`

The Drastic web server role comes with some sensible defaults for deploying to a machine, but
if you feel the need to tweak something you can change a few things in `roles/drastic-web/vars` or
better still use the command line:

`ansible-playbook webservers.yml --extra-vars default_user_name=joey_bloggs default_password=supersecret`

See [the Ansible documentation](http://docs.ansible.com/ansible/) for more information.

## Enabling LDAP Authentication

Authentication is currently handled in users/views.py, taking server and DN pattern from drastic_ui/settings.py. In order to enable LDAP authentication via a simple bind, you must supply to environment variables to the drastic web process (via drastic-web.conf usually). This
may also be configured via ansible host variables.

Environment variables:
* AUTH_LDAP_SERVER_URI - an LDAP server (ldap://ldap.example.com)
* AUTH_LDAP_USER_DN_TEMPLATE - a string formatting template for the DN to be used for BIND (uid=%(user)s,ou=users,dc=example,dc=com) - the user variable will be replaced.

Ansible group variables:
* LDAP_SERVER_URI (same as above)
* LDAP_USER_DN_TEMPLATE (same as above)

If provisioning with Ansible, these LDAP settings will be included in drastic-web.conf and passed to the python process.

## Customising the schema

It is possible to customise the optional metadata for collections (folders) and resources (data files) by providing a custom schema.json file.  The JSON object in the schema file should be dictionary with two keys - collections and resources.  Each of these keys will contain a list of dictionaries, where each dictionary defines a single metadata element to be included when editing or creating a resource or collection.

Each direction must have at least two keys (name and required) and optionally a third (choices).

| Key name | Required? | Description | Example |
|----------|-----------|-------------|---------|
| name  | yes  | The name of the metadata field | Type |
| required | yes| Whether the field is required | true |
| choices | no | A list of valid options, if present the user *must* enter one of these values (or empty if required=false)| ["a", "b", "c""] |


## The Drastic CLI

Management of an Drastic instance is done via the `drastic` command line interface, which is available from inside the previously created virtualenv.   See <https://github.com/UMD-DRASTIC/drastic> for more information on running the commands.
