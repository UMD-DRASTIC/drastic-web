from django.contrib.auth.models import AbstractBaseUser

import uuid
from cassandra.cqlengine import columns
from cassandra.cqlengine.models import Model


class User(AbstractBaseUser):

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = []

    id          = columns.UUID(primary_key=True, default=uuid.uuid4)
    username    = columns.Text(required=True, index=True)
    password    = columns.Text(required=True)
    full_name   = columns.Text(required=True)
