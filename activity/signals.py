"""Activity Signals

This module simply handles signals that are triggered by
other events to generate activity data.

Copyright 2015 Archive Analytics Solutions

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""


from datetime import datetime

import django.dispatch
from django.dispatch import receiver
from  django.template.loader import get_template
from django.template import Context

#from indigo.models.activity import Activity

new_resource_signal = django.dispatch.Signal(providing_args=["user", "resource"])
edited_resource_signal = django.dispatch.Signal(providing_args=["user", "resource"])

new_collection_signal = django.dispatch.Signal(providing_args=["user", "collection"])
edited_collection_signal = django.dispatch.Signal(providing_args=["user", "collection"])

def render_template(name, context):
    from django.utils.html import escape
    template = get_template("activity/events/{}.html".format(name))
    c = Context(context)
    text = template.render(c)
    return unicode(text)

@receiver(new_resource_signal)
def new_resource_callback(sender=None, **kwargs):
    c = { "when": datetime.now() }
    c.update(kwargs)
    Activity.create(html=render_template("created_resource", c))

@receiver(new_collection_signal)
def new_collection_callback(sender=None, **kwargs):
    c = { "when": datetime.now() }
    c.update(kwargs)
    Activity.create(html=render_template("created_collection", c))

@receiver(edited_resource_signal)
def edited_resource_callback(sender=None, **kwargs):
    c = { "when": datetime.now() }
    c.update(kwargs)
    Activity.create(html=render_template("edited_resource", c))


@receiver(edited_collection_signal)
def edited_collection_callback(sender=None, **kwargs):
    c = { "when": datetime.now() }
    c.update(kwargs)
    Activity.create(html=render_template("edited_collection", c))
