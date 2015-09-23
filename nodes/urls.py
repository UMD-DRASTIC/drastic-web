"""Node URLs

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


from django.conf.urls import url

urlpatterns = [
    url(r'^$', 'nodes.views.home', name='home'),
    url(r'^new$', 'nodes.views.new', name='new'),
    url(r'^(?P<id>.*)/edit$', 'nodes.views.edit', name='edit'),
    url(r'^(?P<id>.*)/check$', 'nodes.views.check', name='check'),
    url(r'^(?P<id>.*)/log$', 'nodes.views.logview', name='logview'),
    url(r'^(?P<id>.*)/metrics$', 'nodes.views.metrics', name='metrics'),
]
