"""
A widget for showing/retrieving key value pairs from a
form.

Source: http://www.huyng.com/posts/django-custom-form-widget-for-dictionary-and-tuple-key-value-pairs/

"""
import json
from django.forms import Widget
from django.utils.encoding import force_unicode
from django.utils.safestring import mark_safe
from django.forms.widgets import flatatt

class JsonPairInputs(Widget):
    """A widget that displays JSON Key Value Pairs
    as a list of text input box pairs

    Usage (in forms.py) :
    examplejsonfield = forms.CharField(label  = "Example JSON Key Value Field", required = False,
                                       widget = JsonPairInputs(val_attrs={'size':35},
                                                               key_attrs={'class':'large'}))

    """

    def __init__(self, *args, **kwargs):
        """A widget that displays JSON Key Value Pairs
        as a list of text input box pairs

        kwargs:
        key_attrs -- html attributes applied to the 1st input box pairs
        val_attrs -- html attributes applied to the 2nd input box pairs

        """
        self.key_attrs = {}
        self.val_attrs = {}
        if "key_attrs" in kwargs:
            self.key_attrs = kwargs.pop("key_attrs")
        if "val_attrs" in kwargs:
            self.val_attrs = kwargs.pop("val_attrs")
        Widget.__init__(self, *args, **kwargs)

    def render(self, name, value, attrs=None):
        """Renders this widget into an html string

        args:
        name  (str)  -- name of the field
        value (str)  -- a json string of a two-tuple list automatically passed in by django
        attrs (dict) -- automatically passed in by django (unused in this function)
        """

        if value is None or value.strip() is '': value = '{}'
        twotuple = json.loads(force_unicode(value))
        if isinstance(twotuple, dict):
            twotuple = [(k,v,) for k,v in twotuple.iteritems()]
        ret = ''
        if value and len(value) > 0:
            for k, v in twotuple:
                ctx = {'key':k,
                       'value':v,
                       'fieldname':name,
                       'key_attrs': flatatt(self.key_attrs),
                       'val_attrs': flatatt(self.val_attrs) }
                ret += '<div class="form-group">'
                ret += '<input class="col-md-offset-1 col-md-4" type="text" name="json_key[%(fieldname)s]" value="%(key)s" %(key_attrs)s> \
                <div class="col-md-1"><center>=</center></div> \
                <input class="col-md-4" type="text" name="json_value[%(fieldname)s]" value="%(value)s" %(val_attrs)s><br />' % ctx
                ret += '</div>'
        return mark_safe(ret)

    def value_from_datadict(self, data, files, name):
        """
        Returns the json representation of the key-value pairs
        sent in the POST parameters

        args:
        data  (dict)  -- request.POST or request.GET parameters
        files (list)  -- request.FILES
        name  (str)   -- the name of the field associated with this widget

        """
        if data.has_key('json_key[%s]' % name) and data.has_key('json_value[%s]' % name):
            keys     = data.getlist("json_key[%s]" % name)
            values   = data.getlist("json_value[%s]" % name)
            twotuple = []
            for key, value in zip(keys, values):
                if len(key) > 0:
                    twotuple += [(key,value)]
            jsontext = json.dumps(twotuple)
        return jsontext