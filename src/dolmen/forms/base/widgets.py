# -*- coding: utf-8 -*-

import os.path
from cromlech.browser import ITemplate
from cromlech.i18n import ILanguage
from dolmen.collection import Component, Collection
from dolmen.forms.base import interfaces
from dolmen.forms.base.interfaces import IModeMarker, IWidgetFactory
from dolmen.forms.base.markers import NO_VALUE, HIDDEN, getValue
from dolmen.template import TALTemplate
from grokcore import component as grok
from zope.component import getMultiAdapter, queryMultiAdapter
from zope.interface import Interface, moduleProvides, implementer
from dolmen.collection import ICollection


here = os.path.dirname(__file__)
WIDGETS = os.path.join(here, 'widgets_templates')


def widgetId(form, component):
    """Create an unique ID for a widget.
    """
    return '.'.join(
        (iditem for iditem in
         (str(form.prefix), component.prefix, component.identifier,)
         if iditem))


def getWidgetExtractor(field, form, request):
    warnings.warn(
        u"getWidgetExtractor is deprecated in favor of "
        u"form.widgetFactory.extractor", DeprecationWarning)
    return form.widgetFactory.extractor(field)


@implementer(IWidgetFactory)
class WidgetFactory(object):
    """Generic API to create widgets and extractors.
    """

    def __init__(self, form, request):
        self.form = form
        self.request = request

    def widget(self, field):
        """Create a widget for the given field.
        """
        if not field.available(self.form):
            return None
        mode = str(getValue(field, 'mode', self.form))
        return getMultiAdapter(
            (field, self.form, self.request),
            interfaces.IWidget,
            name=mode)

    def extractor(self, field):
        """Create a widget extractor for the given field.
        """
        mode = getValue(field, 'mode', self.form)

        # The field mode should be extractable or we skip it.
        if (IModeMarker.providedBy(mode) and mode.extractable is False):
            return None

        extractor = queryMultiAdapter(
            (field, self.form, self.request),
            interfaces.IWidgetExtractor,
            name=str(mode))
        if extractor is not None:
            return extractor
        # Default to the default extractor
        return getMultiAdapter(
            (field, self.form, self.request),
            interfaces.IWidgetExtractor)


@implementer(interfaces.IWidgets)
class Widgets(Collection):

    type = interfaces.IWidget

    def extend(self, *args):
        if not args:
            return

        # Ensure the user created us with the right options
        assert self.__dict__.get('form', None) is not None
        factory = self.form.widgetFactory.widget

        for arg in args:
            if interfaces.IWidgets.providedBy(arg):
                for widget in arg:
                    self.append(widget)
            elif interfaces.ICollection.providedBy(arg):
                for field in arg:
                    widget = factory(field)
                    if widget is not None:
                        self.append(widget)
            elif interfaces.IWidget.providedBy(arg):
                self.append(arg)
            elif interfaces.IRenderableComponent.providedBy(arg):
                widget = factory(arg)
                if widget is not None:
                    self.append(widget)
            else:
                raise TypeError(u'Invalid type', arg)

    def update(self):
        for widget in self:
            widget.update()


@implementer(interfaces.IWidget)
class Widget(Component, grok.MultiAdapter):
    grok.baseclass()
    grok.provides(interfaces.IWidget)

    defaultHtmlAttributes = set(['required', 'readonly', 'placeholder',
                                 'autocomplete', 'size', 'maxlength',
                                 'pattern', 'style'])
    defaultHtmlClass = ['field']
    alternateLayout = False

    def __init__(self, component, form, request):
        identifier = widgetId(form, component)
        super(Widget, self).__init__(component.title, identifier)
        self.component = component
        self.form = form
        self.request = request
        self._htmlAttributes = {}

    def clone(self, new_identifier=None):
        raise NotImplementedError

    def htmlId(self):
        # Return an identifier suitable for CSS usage
        return self.identifier.replace('.', '-')

    def htmlClass(self):
        result = self.defaultHtmlClass
        if self.required:
            result = result + ['field-required',]
        return ' '.join(result)

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

    def isVisible(self):
        return not self.component.mode == HIDDEN

    def namespace(self):
        namespace = {'widget': self,
                     'request': self.request}
        return namespace

    def update(self):
        pass

    @property
    def target_language(self):
        """Returns the prefered language by adapting the request.
        If no adapter thus no language is found, None is returned.
        None will, most of the time, mean 'no translation'.
        """
        return ILanguage(self.request, None)
    
    def render(self):
        template = getattr(self, 'template', None)
        if template is None:
            template = getMultiAdapter((self, self.request), ITemplate)
        return template.render(
            self, target_language=self.target_language, **self.namespace())


@implementer(interfaces.IWidgetExtractor)
class WidgetExtractor(grok.MultiAdapter):
    grok.provides(interfaces.IWidgetExtractor)
    grok.adapts(
        interfaces.IRenderableComponent,
        interfaces.IFieldExtractionValueSetting,
        Interface)

    def __init__(self, component, form, request):
        self.identifier = widgetId(form, component)
        self.component = component
        self.form = form
        self.request = request

    def extract(self):
        value = self.request.form.get(self.identifier)
        if value is None:
            value = NO_VALUE
        return (value, None)

    def extractRaw(self):
        entries = {}
        sub_identifier = self.identifier + '.'
        for key, value in self.request.form.iteritems():
            if key.startswith(sub_identifier) or key == self.identifier:
                entries[key] = value
        return entries


class FieldWidgetExtractor(WidgetExtractor):
    grok.adapts(
        interfaces.IField,
        interfaces.IFieldExtractionValueSetting,
        Interface)

    def extract(self):
        value = self.request.form.get(self.identifier)
        # The value is empty only if the field is required.
        if (value is None or
            (not len(value) and self.component.isRequired(self.form))):
            value = NO_VALUE
        return (value, None)


# After follow the implementation of some really generic default
# widgets

class ActionWidget(Widget):
    grok.name('input')
    grok.adapts(
        interfaces.IAction,
        interfaces.IFieldExtractionValueSetting,
        Interface)

    template = TALTemplate(os.path.join(WIDGETS, 'action.pt'))
    defaultHtmlAttributes = set(['accesskey', 'formnovalidate', 'style'])
    defaultHtmlClass = ['action']

    def __init__(self, component, form, request):
        super(ActionWidget, self).__init__(component, form, request)
        self.description = component.description
        self._htmlAttributes.update({
                'accesskey': component.accesskey,
                'formnovalidate': not component.html5Validation})
        self._htmlAttributes.update(component.htmlAttributes)

    def htmlClass(self):
        return 'action'


@implementer(interfaces.IFieldWidget)
class FieldWidget(Widget):
    grok.name('input')
    grok.adapts(
        interfaces.IField,
        interfaces.IFormData,
        Interface)

    template = TALTemplate(os.path.join(WIDGETS, 'fieldwidget.pt'))
    
    def __init__(self, component, form, request):
        super(FieldWidget, self).__init__(component, form, request)
        self.description = component.description
        self.required = component.isRequired(form)
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
            extractor = self.form.widgetFactory.extractor(self.component)
            if extractor is not None:
                value = extractor.extractRaw()
                if value:
                    return self.prepareRequestValue(value, extractor)

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

    def prepareRequestValue(self, value, extractor):
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


class DisplayFieldWidget(FieldWidget):
    grok.name('display')
    template = TALTemplate(os.path.join(WIDGETS, 'display.pt'))


class HiddenFieldWidget(FieldWidget):
    grok.name('hidden')
    template = TALTemplate(os.path.join(WIDGETS, 'hidden.pt'))


class ReadOnlyFieldWidget(FieldWidget):
    grok.name('readonly')
    template = TALTemplate(os.path.join(WIDGETS, 'readonly.pt'))


moduleProvides(interfaces.IWidgetsAPI)
__all__ = list(interfaces.IWidgetsAPI)
