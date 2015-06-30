# Indigo Development instructions [WIP]



## Installing

* Make a virtualenv and activate it

```
git clone git@bitbucket.org:archivea/indigo-web.git
cd indigo-web
pip install -r requirements.txt
```

## Syncing the database


```
./manage.py sync_cassandra
```

## Running the server

Because of a conflict between the Cassandra driver and Django, you *must* use runserver_plus to run your django app.

```
./manage.py runserver_plus
```


## Required environment variables

export CQLENG_ALLOW_SCHEMA_MANAGEMENT=1
export INDIGO_SCHEMA=/path/to/schema.json
export AGENT_CONFIG=/path/to/agentconfig