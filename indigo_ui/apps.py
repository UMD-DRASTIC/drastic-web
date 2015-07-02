from django.apps import AppConfig

class IndigoAppConfig(AppConfig):
    name = 'indigo_ui'
    verbose_name = "Indigo"

    def ready(self):
        import activity.signals
        from indigo.models import initialise, Collection

        initialise("indigo")

        root = Collection.get_root_collection()
        if not root:
            print "Creating root collection"
            Collection.create(name="Home", path="/")
        else:
            print "Using existing root collection"

