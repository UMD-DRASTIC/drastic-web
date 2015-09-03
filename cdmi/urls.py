# from django.conf.urls import url, include
# 
# urlpatterns = [
#     url(r'^cdmi_capabilities(?P<path>.*)$', 'cdmi.views.capabilities', name='capabilities'),
#     
#     url(r'^cdmi_objectid/(?P<id>.*)$', 'cdmi.views.crud_id', name='crud_id'),
#     url(r'^(?P<path>.*)$', 'cdmi.views.crud', name='crud'),
#     
#     url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
# ]
# 
# 
# #url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))


from django.conf.urls import url, include
from django.contrib.auth.models import User
from rest_framework import routers, serializers, viewsets

# Serializers define the API representation.
class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'is_staff')

# ViewSets define the view behavior.
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'users', UserViewSet)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]