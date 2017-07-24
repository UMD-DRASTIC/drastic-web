# Overview

Drastic is a data management solution written in Python that allows users to upload, describe, and archive data resources.  Data is managed in a distributed Cassandra database. All changes to data in the repository are followed by a message that describes the change. By responding to messages, the usual repository functions may be extended to include arbitrary workflow. For more information, please see the [project website](https://umd-drastic.github.io/).

# drastic-web

The primary interface to Drastic is the Django application in this repository. It includes a web-based user interface, as well as the CDMI and WEBDAV APIs.

# Documentation

* [AGPL 3 License](https://github.com/drastic-deploy/tree/master/LICENSE)
* [Install Guide](https://github.com/drastic-deploy/tree/master/docs/INSTALL.md)
* [Developer Guide](https://github.com/drastic-deploy/tree/master/docs/CONTRIBUTING.md)
* [All Documentation](https://github.com/drastic-deploy/tree/master/docs/)

# Community

We aim to make the DRAS-TIC project as participatory as possible. We will make announcements via Twitter at [@DRASTIC_Repo](https://twitter.com/DRASTIC_Repo). You can also find news and updates on the [DRAS-TIC project site](https://umd-drastic.github.io).

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
