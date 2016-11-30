# -*- coding: utf-8 -*-

import crom
import sys
if sys.version > '3':
    unicode = str

import os.path
from cromlech.browser import ITemplate
from cromlech.i18n import ILanguage
from dolmen.collection import Component, Collection
from dolmen.forms.base import interfaces
from dolmen.forms.base.interfaces import IModeMarker
from dolmen.forms.base.markers import NO_VALUE, HIDDEN, getValue
from dolmen.template import TALTemplate
from zope.interface import Interface, moduleProvides, implementer, provider


here = os.path.dirname(__file__)
WIDGETS = os.path.join(here, 'widgets_templates')


def widget_id(form, component):
    """Create an unique ID for a widget.
    """
    return '.'.join(
        (iditem for iditem in
         (str(form.prefix), component.prefix, component.identifier,)
         if iditem))


@implementer(interfaces.IWidget)
@provider(interfaces.IWidget)
class Widget(Component):

    template = None

    defaultHtmlAttributes = set(['required', 'readonly', 'placeholder',
                                 'autocomplete', 'size', 'maxlength',
                                 'pattern', 'style'])
    defaultHtmlClass = ['field']
    
    def __init__(self, component, form, request):
        identifier = widget_id(form, component)
        super(Widget, self).__init__(component.title, identifier)
        self.component = component
        self.form = form
        self.request = request
        self._htmlAttributes = {}

    def copy(self):
        raise NotImplementedError

    def htmlId(self):
        # Return an identifier suitable for CSS usage
        return self.identifier.replace('.', '-')

    def htmlClass(self):
        return 'field'

    def htmlAttribute(self, name=None):
        value = self._htmlAttributes.get(name)
        if value:
            # Boolean return as value the name of the property
            if isinstance(value, bool):
                return name
            return value
        return None

    def htmlAttributes(self):
        attributes = {}
        for key, value in self._htmlAttributes.items():
            if (value and
                (key.startswith('data-') or key in self.defaultHtmlAttributes)):
                if isinstance(value, bool):
                    attributes[key] = key
                else:
                    attributes[key] = str(value)
        return attributes
    
    @property
    def visible(self):
        return self.component.mode != HIDDEN

    def namespace(self):
        namespace = {'widget': self, 'request': self.request}
        return namespace

    @property
    def target_language(self):
        return ILanguage(self.request, default=None)

    def update(self):
        pass

    def render(self):
        template = getattr(self, 'template', None)
        if template is None:
            template = ITemplate(self, self.request)
        return template.render(
            self, target_language=self.target_language, **self.namespace())


@crom.adapter
@crom.target(interfaces.IWidgetExtractor)
@crom.sources(interfaces.IRenderableComponent,
              interfaces.IFieldExtractionValueSetting,
              Interface)
@implementer(interfaces.IWidgetExtractor)
class WidgetExtractor(object):

    def __init__(self, component, form, request):
        self.identifier = widget_id(form, component)
        self.component = component
        self.form = form
        self.request = request

    def extract(self):
        # default behaviour is NO_VALUE means value not even mentionned
        value = self.request.form.get(self.identifier, NO_VALUE)
        return (value, None)

    def extractRaw(self):
        entries = {}
        sub_identifier = self.identifier + '.'
        for key, value in self.request.form.items():
            if key.startswith(sub_identifier) or key == self.identifier:
                entries[key] = value
        return entries


@crom.adapter
@crom.name('hidden')
@crom.target(interfaces.IWidgetExtractor)
@crom.sources(interfaces.IRenderableComponent,
              interfaces.IFieldExtractionValueSetting,
              Interface)
@implementer(interfaces.IWidgetExtractor)
class HiddenWidgetExtractor(WidgetExtractor):
    pass


@crom.adapter
@crom.name('readonly')
@crom.target(interfaces.IWidgetExtractor)
@crom.sources(interfaces.IRenderableComponent,
              interfaces.IFieldExtractionValueSetting,
              Interface)
@implementer(interfaces.IWidgetExtractor)
class ReadOnlyWidgetExtractor(WidgetExtractor):
    pass


def createWidget(field, form, request):
    """Create a widget (or return None) for the given form and
    request.
    """
    if not field.available(form):
        return None
    mode = str(getValue(field, 'mode', form))
    return interfaces.IWidget(field, form, request, name=mode)


@implementer(interfaces.IWidgets)
class Widgets(Collection):

    type = interfaces.IWidget

    def extend(self, *args):
        if not args:
            return

        # Ensure the user created us with the right options
        assert self.__dict__.get('form', None) is not None
        assert self.__dict__.get('request', None) is not None

        for arg in args:
            if interfaces.IWidgets.providedBy(arg):
                for widget in arg:
                    self.append(widget)
            elif interfaces.ICollection.providedBy(arg):
                for field in arg:
                    widget = createWidget(field, self.form, self.request)
                    if widget is not None:
                        self.append(widget)
            elif interfaces.IWidget.providedBy(arg):
                self.append(arg)
            elif interfaces.IRenderableComponent.providedBy(arg):
                widget = createWidget(arg, self.form, self.request)
                if widget is not None:
                    self.append(widget)
            else:
                raise TypeError(u'Invalid type', arg)

    def update(self):
        for widget in self:
            widget.update()


# After follow the implementation of some really generic default
# widgets

@crom.adapter
@crom.name('input')
@crom.target(interfaces.IWidget)
@crom.sources(interfaces.IAction,
        interfaces.IFieldExtractionValueSetting,
        Interface)
class ActionWidget(Widget):

    defaultHtmlAttributes = set(['accesskey', 'formnovalidate', 'style'])
    defaultHtmlClass = ['action']
    
    template = TALTemplate(os.path.join(WIDGETS, 'action.pt'))
    
    def __init__(self, component, form, request):
        super(ActionWidget, self).__init__(component, form, request)
        self.description = component.description
        self._htmlAttributes.update({
                'accesskey': component.accesskey,
                'formnovalidate': not component.html5Validation})
        self._htmlAttributes.update(component.htmlAttributes)

    def htmlClass(self):
        return 'action'


def getWidgetExtractor(field, form, request):
    mode = str(getValue(field, 'mode', form))

    # The field mode should be extractable or we skip it.
    if (IModeMarker.providedBy(field.mode) and
        field.mode.extractable is False):
        return None

    extractor = interfaces.IWidgetExtractor(
        field, form, request, name=mode, default=None)
    if extractor is not None:
        return extractor

    return interfaces.IWidgetExtractor(field, form, request)


@crom.adapter
@crom.name('input')
@crom.target(interfaces.IWidget)
@crom.sources(interfaces.IField, interfaces.IFormData, Interface)
@implementer(interfaces.IFieldWidget)
class FieldWidget(Widget):

    template = TALTemplate(os.path.join(WIDGETS, 'fieldwidget.pt'))

    def __init__(self, component, form, request):
        super(FieldWidget, self).__init__(component, form, request)
        self.description = component.description
        self.required = component.required
        self._htmlAttributes.update(component.htmlAttributes)
        self._htmlAttributes.update({
            'readonly': component.readonly,
            'required': self.required})

    @property
    def error(self):
        return self.form.errors.get(self.identifier, None)

    def computeValue(self):
        # First lookup the request
        ignoreRequest = getValue(self.component, 'ignoreRequest', self.form)
        if not ignoreRequest:
            extractor = getWidgetExtractor(
                self.component, self.form, self.request)
            if extractor is not None:
                value = extractor.extractRaw()
                if value:
                    return self.prepareRequestValue(value)

        # After, the context
        ignoreContent = getValue(self.component, 'ignoreContent', self.form)
        if not ignoreContent:
            data = self.form.getContentData()
            try:
                value = data.get(self.component.identifier)
                # XXX: Need review
                if value is None:
                    value = NO_VALUE
                return self.prepareContentValue(value)
            except KeyError:
                # No value on the content for field, continue.
                pass

        # Take any default value
        value = self.component.getDefaultValue(self.form)
        return self.prepareContentValue(value)

    def valueToUnicode(self, value):
        return unicode(value)

    def prepareRequestValue(self, value):
        return value

    def prepareContentValue(self, value):
        formatted_value = u''
        if value is not NO_VALUE:
            formatted_value = self.valueToUnicode(value)
        return {self.identifier: formatted_value}

    def inputValue(self, id=None):
        if id is not None:
            id = '%s.%s' % (self.identifier, id)
        else:
            id = self.identifier
        return self.value.get(id, '')

    def update(self):
        self.value = self.computeValue()


@crom.adapter
@crom.name('display')
@crom.target(interfaces.IWidget)
@crom.sources(interfaces.IField, interfaces.IFormData, Interface)
@implementer(interfaces.IFieldWidget)
class DisplayFieldWidget(FieldWidget):
    template = TALTemplate(os.path.join(WIDGETS, 'display.pt'))


@crom.adapter
@crom.name('hidden')
@crom.target(interfaces.IWidget)
@crom.sources(interfaces.IField, interfaces.IFormData, Interface)
@implementer(interfaces.IFieldWidget)
class HiddenFieldWidget(FieldWidget):
    template = TALTemplate(os.path.join(WIDGETS, 'hidden.pt'))


@crom.adapter
@crom.name('readonly')
@crom.target(interfaces.IWidget)
@crom.sources(interfaces.IField, interfaces.IFormData, Interface)
@implementer(interfaces.IFieldWidget)
class ReadOnlyFieldWidget(FieldWidget):
    template = TALTemplate(os.path.join(WIDGETS, 'readonly.pt'))


moduleProvides(interfaces.IWidgetsAPI)
__all__ = list(interfaces.IWidgetsAPI)
