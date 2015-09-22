from indigo.models.collection import Collection


class CDMIContainer(Collection):

    class Meta:
        ordering = ('container','name',)

