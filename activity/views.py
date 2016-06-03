"""Activity Views

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

from django import template
from django.shortcuts import render
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required

from indigo.models import (
    Collection,
    Group,
    Notification,
    Resource,
    User
)
from indigo.models.notification import (
    OBJ_RESOURCE,
    OBJ_COLLECTION,
    OBJ_USER,
    OBJ_GROUP,

    OP_CREATE,
    OP_DELETE,
    OP_UPDATE,
    OP_INDEX,
    OP_MOVE
)



@login_required
def home(request):
    notifications = Notification.recent(10)
    activities = []
    for notif in notifications:
        t = template.Template(notif['tmpl'])
        
        obj_uuid = notif['object_uuid']
        object = None
        if notif['object_type'] == OBJ_RESOURCE:
            object = Resource.find(obj_uuid)
            if object:
                object_dict = object.to_dict()
            else:
                object_dict = {'name': obj_uuid}
        elif notif['object_type'] == OBJ_COLLECTION:
            object = Collection.find(obj_uuid)
            if object:
                object_dict = object.to_dict()
            else:
                object_dict = {'name': obj_uuid}
        elif notif['object_type'] == OBJ_USER:
            object = User.find(obj_uuid)
            if object:
                object_dict = object.to_dict()
            else:
                # User has been deleted it can't be find by uuid
                # look in payload of the message to get the name
                if notif['operation'] in [OP_CREATE, OP_UPDATE]:
                    name = notif['payload']['post']['name']
                else: # OP_DELETE
                    name = notif['payload']['pre']['name']
                object_dict = {'name': name}
        elif notif['object_type'] == OBJ_GROUP:
            object = Group.find(obj_uuid)
            if object:
                object_dict = object.to_dict()
            else:
                # User has been deleted it can't be find by uuid
                # look in payload of the message to get the name
                if notif['operation'] in [OP_CREATE, OP_UPDATE]:
                    name = notif['payload']['post']['name']
                else: # OP_DELETE
                    name = notif['payload']['pre']['name']
                object_dict = {'uuid': obj_uuid,
                               'name': name}
        user_dict = {}
        if notif['username']:
            user = User.find(notif['username'])
            if user:
                user_dict = user.to_dict()
            

        variables = {
            'user': user_dict,
            'when': notif['when'],
            'object': object_dict
        }
        
        ctx = template.Context(variables)
        activities.append({'html': t.render(ctx)})
    
    return render(request, 'activity/index.html', {'activities': activities})

