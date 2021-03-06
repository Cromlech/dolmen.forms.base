# -*- coding: utf-8 -*-

from dolmen.collection import Component, Collection
from dolmen.collection.components import IGNORE
from dolmen.forms.base import markers, interfaces, _
from zope.interface import implementer, moduleProvides


def test_len(value):
    """TypeError resistant test on len != 0
    """
    if hasattr(value, '__len__'):
        try:
            return bool(len(value))
        except TypeError:
            return True  # considered as not having a __len__
    return True


@implementer(interfaces.IField)
class Field(Component):

    description = u''
    required = False
    prefix = 'field'
    readonly = False
    htmlAttributes = {}
    
    ignoreContent = markers.DEFAULT
    ignoreRequest = markers.DEFAULT
    mode = markers.DEFAULT
    defaultValue = markers.NO_VALUE

    def __init__(self, *args, **kwargs):
        self.htmlAttributes = self.htmlAttributes.copy()
        if 'htmlAttributes' in kwargs:
            self.htmlAttributes.update(kwargs.pop('htmlAttributes'))
        super(Field, self).__init__(*args, **kwargs)

    def available(self, form):
        return True

    def getDefaultValue(self, form):
        if callable(self.defaultValue):
            return self.defaultValue(form)
        return self.defaultValue

    def isEmpty(self, value):
        return (value is markers.NO_VALUE or not test_len(value))

    def validate(self, value, context=None):
        if self.required and self.isEmpty(value):
            return _(u"Missing required value.",
                     default=u"Missing required value.")
        return None


@implementer(interfaces.IFields)
class Fields(Collection):

    type = interfaces.IField
    factory = interfaces.IFieldFactory
    behavior = IGNORE


moduleProvides(interfaces.IFieldsAPI)
__all__ = list(interfaces.IFieldsAPI)
