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

## The Drastic CLI

Management of an Drastic instance is done via the `drastic` command line interface, which is available from inside the previously created virtualenv.   See <https://github.com/UMD-DRASTIC/drastic> for more information on running the commands.
