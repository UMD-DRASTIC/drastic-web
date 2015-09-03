# Indigo

Indigo is a data management solution written in Python that allows users to upload and archive data resources.  Data is managed in a Cassandra database, and the associated Indigo Agent is responsible for post-processing on uploaded content.  

The primary interface to Indigo is the Django application in this repository.


## Installing

* Make a virtualenv and activate it

```
git clone git@bitbucket.org:archivea/indigo-web.git
cd indigo-web
pip install -r requirements.txt
```

Before starting the server, you should set the following environment variables.

```
export CQLENG_ALLOW_SCHEMA_MANAGEMENT=1
export INDIGO_SCHEMA=/path/to/schema.json
export AGENT_CONFIG=/path/to/agentconfig
```

The server can then be started (for development) with

```
./manage.py runserver
```

## Customising the Schema

It is possible to customise the optional metadata for collections (folders) and resources (data files) by providing a custom schema.json file.  The JSON object in the schema file should be dictionary with two keys - collections and resources.  Each of these keys will contain a list of dictionaries, where each dictionary defines a single metadata element to be included when editing or creating a resource or collection.  

Each direction must have at least two keys (name and required) and optionally a third (choices).

| Key name | Required? | Description | Example |
|----------|-----------|-------------|---------|
| name  | yes  | The name of the metadata field | Type |
| required | yes| Whether the field is required | true |
| choices | no | A list of valid options, if present the user *must* enter one of these values (or empty if required=false)| ["a", "b", "c""] |


## The Indigo CLI

Management of an Indigo instance is done via the ```indigo``` command line interface, which is available from inside the previously created virtualenv.   See <https://bitbucket.org/archivea/indigo> for more information on running the commands.


