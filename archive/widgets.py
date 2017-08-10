""""Archive Widget

A widget for showing/retrieving key value pairs from a
form.

Source:
    http://www.huyng.com/posts/django-custom-form-widget-for-dictionary-and-tuple-key-value-pairs/


"""
__copyright__ = "Copyright (C) 2016 University of Maryland"
__license__ = "GNU AFFERO GENERAL PUBLIC LICENSE, Version 3"


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
        import logging
        logging.debug('json form field: {0} {1}'.format(name, str(value)))
        #  metadata {"foo": ["bar", "barr"]}
        if (not value) or value.strip() is '':
            value = '{"":""}'
        twotuple = json.loads(force_unicode(value))

        if isinstance(twotuple, dict):
            twotuple = [(k, v,) for k, v in twotuple.iteritems()]
        if not twotuple:
            twotuple = [("", "")]

        ret = ''
        if value and len(value) > 0:
            for k, values in twotuple:
                ret += """<div class="form-group" id="">"""
                if not isinstance(values, list):
                    values = [values]
                for v in values:
                    ctx = {'key': k,
                           'value': v,
                           'fieldname': name,
                           'key_attrs': flatatt(self.key_attrs),
                           'val_attrs': flatatt(self.val_attrs)}
                    ret += """
                            <div class="col-md-4">
                                <input placeholder="Key" class="form-control" type="text" name="json_key[%(fieldname)s]" value="%(key)s" %(key_attrs)s>
                            </div>
                            <div class="col-md-1" style="font-size: 2em; text-align: center;">
                            =
                            </div>
                            <div class="col-md-5">
                                <input placeholder="Value"  class="form-control" type="text" name="json_value[%(fieldname)s]" value="%(value)s" %(val_attrs)s>
                            </div>
                            <div class="col-md-2 btn-group" role="group" aria-label="...">
                                <a class="btn btn-large btn-success">
                                    <i class="glyphicon glyphicon-plus"></i>
                                </a>
                                <a class="btn btn-large btn-danger">
                                    <i class="glyphicon glyphicon-minus"></i>
                                </a>
                            </div>
                            <div class="clearfix"></div>
                            """ % ctx
                ret += """</div>"""
        ret = '<span id="metadata_fields">' + ret + '</span>'
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
        jsontext = ""
        if data.has_key('json_key[%s]' % name) and data.has_key('json_value[%s]' % name):
            keys = data.getlist("json_key[%s]" % name)
            values = data.getlist("json_value[%s]" % name)
            twotuple = []
            for key, value in zip(keys, values):
                if len(key) > 0:
                    twotuple += [(key, value)]
            jsontext = json.dumps(twotuple)
        return jsontext
