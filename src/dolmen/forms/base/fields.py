# -*- coding: utf-8 -*-

from dolmen.collection import Component, Collection
from dolmen.forms.base import markers, interfaces
from zope.interface import implements, moduleProvides
from zope.i18nmessageid import MessageFactory


class Field(Component):
    implements(interfaces.IField)

    description = u''
    required = False
    prefix = 'field'
    readonly = False

    ignoreContent = markers.DEFAULT
    ignoreRequest = markers.DEFAULT
    mode = markers.DEFAULT
    defaultValue = markers.NO_VALUE

    def available(self, form):
        return True

    def getDefaultValue(self, form):
        if callable(self.defaultValue):
            return self.defaultValue(form)
        return self.defaultValue

    def isEmpty(self, value):
        return value is NO_VALUE

    def validate(self, value, context=None):
        if self.required and self.isEmpty(value):
            return _(u"Missing required value.")
        return None


class Fields(Collection):
    implements(interfaces.IFields)

    type = interfaces.IField
    factory = interfaces.IFieldFactory


moduleProvides(interfaces.IFieldsAPI)
__all__ = list(interfaces.IFieldsAPI)
