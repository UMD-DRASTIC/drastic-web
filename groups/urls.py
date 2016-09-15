""""Groups UI URLs

"""
__copyright__ = "Copyright (C) 2016 University of Maryland"
__license__ = "GNU AFFERO GENERAL PUBLIC LICENSE, Version 3"


from django.conf.urls import url

urlpatterns = [
    url(r'^$', 'groups.views.home', name='home'),
    
    url(r'^new/group', 'groups.views.new_group', name='new_group'),
    url(r'^delete/group/(?P<name>.*)$', 'groups.views.delete_group', name='delete_group'),
    url(r'^edit/group/(?P<name>.*)$', 'groups.views.edit_group', name='edit_group'),
    
    url(r'^rm/(?P<name>.*)/(?P<uname>.*)$', 'groups.views.rm_user', name='rm_user'),
    url(r'^add/(?P<name>.*)$', 'groups.views.add_user', name='add_user'),

    url(r'^(?P<name>.*)$', 'groups.views.group_view', name='view'),
    

]
