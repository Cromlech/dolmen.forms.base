# -*- coding: utf-8 -*-

from dolmen.collection import Component, Collection
from dolmen.collection.components import IGNORE
from dolmen.forms.base import interfaces
from dolmen.forms.base.markers import NO_VALUE, DEFAULT, Marker
from zope.schema.interfaces import IContextAwareDefaultFactory
from zope.interface import implementer, moduleProvides
from zope.i18nmessageid import MessageFactory

_ = MessageFactory('dolmen.forms.base')


@implementer(interfaces.IField)
class Field(Component):

    description = u''
    required = False
    prefix = 'field'
    readonly = False
    htmlAttributes = {}
    interface = None
    ignoreContent = DEFAULT
    ignoreRequest = DEFAULT
    mode = DEFAULT
    defaultValue = NO_VALUE

    def __init__(self,
                 title=None,
                 identifier=None,
                 description=u"",
                 required=False,
                 readonly=False,
                 defaultFactory=None,
                 defaultValue=NO_VALUE,
                 constrainValue=None,
                 interface=None,
                 **htmlAttributes):
        super(Field, self).__init__(title, identifier)
        self.description = description
        self.required = required
        self.readonly = readonly
        self.defaultFactory = defaultFactory
        self.defaultValue = defaultValue
        self.interface = interface
        if constrainValue is not None:
            self.constrainValue = constrainValue
        self.htmlAttributes = self.htmlAttributes.copy()
        self.htmlAttributes.update(htmlAttributes)

    def clone(self, new_identifier=None):
        copy = self.__class__(title=self.title, identifier=self.identifier)
        copy.__dict__.update(self.__dict__)
        if new_identifier is not None:
            copy.identifier = new_identifier
        return copy

    def available(self, form):
        return True

    def isRequired(self, form):
        if callable(self.required):
            return self.required(form)
        return self.required

    def isEmpty(self, value):
        return value is NO_VALUE

    def getDefaultValue(self, form):
        if self.defaultValue is NO_VALUE:
            if self.defaultFactory is not None:
                if IContextAwareDefaultFactory.providedBy(self.defaultFactory):
                    return self.defaultFactory(form)
                return self.defaultFactory()
        elif callable(self.defaultValue):
            return self.defaultValue(form)
        return self.defaultValue

    def constrainValue(self, value):
        return True

    def validate(self, value, form):
        if self.isEmpty(value):
            if self.isRequired(form):
                return _(u"Missing required value.",
                         default=u"Missing required value.")
        elif not isinstance(value, Marker):
            try:
                if not self.constrainValue(value):
                    return _(u"The constraint failed.",
                             default=u"The constraint failed.")
            except Exception as error:
                if hasattr(error, 'doc'):
                    return error.doc()
                return _(u"The constraint failed.",
                         default=u"The constraint failed.")
        return None


@implementer(interfaces.IFields)
class Fields(Collection):

    type = interfaces.IField
    factory = interfaces.IFieldFactory
    behavior = IGNORE


moduleProvides(interfaces.IFieldsAPI)
__all__ = list(interfaces.IFieldsAPI)
