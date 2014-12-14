# -*- coding: utf-8 -*-

import operator
from os import path

from cromlech.browser.interfaces import ILayout, IRenderable, IURL
from cromlech.browser.exceptions import HTTPRedirect, REDIRECTIONS
from cromlech.browser.utils import redirect_exception_response
from cromlech.i18n import getLocalizer

from dolmen.template import TALTemplate
from dolmen.forms.base import _
from dolmen.forms.base import interfaces
from dolmen.forms.base.actions import Actions
from dolmen.forms.base.datamanagers import ObjectDataManager
from dolmen.forms.base.errors import Errors, Error
from dolmen.forms.base.fields import Fields
from dolmen.forms.base.markers import NO_VALUE, INPUT
from dolmen.forms.base.widgets import Widgets, getWidgetExtractor
from dolmen.forms.base.interfaces import IFormView, ICollection, ISuccessMarker

from zope.interface import implementer, moduleProvides


PATH = path.join(path.dirname(__file__), 'default_templates')
default_template = TALTemplate(path.join(PATH, "formtemplate.pt"))

_marker = object()


def query_form_layout(form, interface=ILayout, name=""):
    """Returns a layout associated to the form's request and context.
    """
    assert IFormView.providedBy(form)
    assert interface.isOrExtends(ILayout)
    return interface(form.request, form.context, name=name)


def make_form_response(form, result, *args, **kwargs):
    response = form.responseFactory()
    response.write(result or u'')
    return response


def make_layout_response(form, result, name=None):
    if name is None:
        name = getattr(form, 'layoutName', "")
    layout = query_form_layout(form, name=name)
    if layout is not None:
        wrapped = layout(result, **{'form': form})
        response = form.responseFactory()
        response.write(wrapped or u'')
        return response
    raise RuntimeError(
        'Unable to resolve the layout (name: %r) for %r' % (name, form))


class cached(object):

    def __init__(self, key):
        self.key = key

    def __call__(self, func):
        def cached_or_not(component, value):
            cache = getattr(component, self.key)
            cached = cache.get(value, _marker)
            if cached is not _marker:
                return cached

            computed = func(component, value)
            cache[value] = computed
            return computed
        return cached_or_not


class Object(object):
    """Python object that takes argument to its __init__, in order to
    use super. This is required by Python 2.6.
    """

    def __init__(self, *args, **kwargs):
        pass


def cloneFormData(original, content=_marker, prefix=None):
    assert interfaces.IFieldExtractionValueSetting.providedBy(original)
    clone = FormData(original.context, original.request, content)
    clone.ignoreRequest = original.ignoreRequest
    clone.ignoreContent = original.ignoreContent
    clone.mode = original.mode
    clone.parent = original
    if prefix is None:
        clone.prefix = original.prefix
    else:
        clone.prefix = prefix

    # form submission related attributes
    clone.postOnly = original.postOnly
    clone.formMethod = original.formMethod
    clone.enctype = original.enctype

    # Unpiling the error stack
    errors = original.errors.get(clone.prefix, None)
    if errors is not None:
        clone.errors = errors
    return clone


class FieldsValues(dict):
    """Dictionary to contains values of fields. get default by default
    on the default value of a field.
    """

    def __init__(self, form, fields):
        self.form = form
        self.fields = fields

    def getWithDefault(self, key, default=None):
        value = super(FieldsValues, self).get(key, NO_VALUE)
        if value is NO_VALUE:
            value = self.fields[key].getDefaultValue(self.form)
            if value is NO_VALUE:
                return default
        return value


@implementer(interfaces.IFormData)
class FormData(Object):
    """This represent a submission of a form. It can be used to update
    widgets and run actions.
    """
    prefix = 'form'
    parent = None
    mode = INPUT
    dataManager = ObjectDataManager
    dataValidators = []
    postOnly = True
    formMethod = 'post'
    enctype = 'multipart/form-data'

    ignoreRequest = False
    ignoreContent = True

    status = u''

    def __init__(self, context, request, content=_marker):
        super(FormData, self).__init__(context, request)
        self.context = context
        self.request = request
        self.errors = Errors()  # This should move to FormCanvas
        self._extracted = {}
        self.__content = None
        if content is _marker:
            content = context
        self.setContentData(content)

    @property
    def formErrors(self):
        error = self.errors.get(self.prefix, None)

        if self.errors and error is None:
            # If the form has errors but no form specific ones
            # we have to add it. This could be overridable.
            error = Error(_(u"There were errors."), self.prefix)

        if error is not None:
            # If there's a form error, we need to make sure it's iterable.
            # Doing this, we can handle both Error and Errors.
            # Some forms can trigger more than one error, on failure.
            if ICollection.providedBy(error):
                return error
            else:
                return [error]
        return []

    def htmlId(self):
        return self.prefix.replace('.', '-')

    def getContent(self):
        # Shortcut for actions. You should not reimplement that method
        # but getContentData.
        return self.getContentData().getContent()

    def getContentData(self):
        return self.__content

    def setContentData(self, content):
        if not interfaces.IDataManager.providedBy(content):
            content = self.dataManager(content)
        self.__content = content

    def validateData(self, fields, data):
        errors = Errors()
        for factory in self.dataValidators:
            validator = factory(fields, self)
            for error in validator.validate(data):
                errors.append(Error(error.args[0], self.prefix))
        return errors

    @cached('_extracted')
    def extractData(self, fields):
        data = FieldsValues(self, fields)
        errors = Errors()

        for field in fields:
            if not field.available(self):
                continue

            # Widget extraction and validation
            extractor = getWidgetExtractor(field, self, self.request)
            if extractor is not None:
                value, error = extractor.extract()
                if error is None:
                    error = field.validate(value, self.context)
                if error is not None:
                    if not interfaces.IError.providedBy(error):
                        if interfaces.IErrors.providedBy(error):
                            # this is an Errors, not implementing IError
                            # "Make it so, number one !"
                            error = Errors(
                                *error, identifier=extractor.identifier)
                        else:
                            error = Error(
                                error, identifier=extractor.identifier)
                    errors.append(error)
                data[field.identifier] = value

        # Generic form validation
        validation_errors = self.validateData(fields, data)
        errors.extend(validation_errors)
        self.errors = errors
        return (data, errors)


@implementer(IRenderable, interfaces.ISimpleFormCanvas)
class FormCanvas(FormData):
    """This represent a simple form setup: setup some fields and
    actions, prepare widgets for it.
    """
    label = u''
    description = u''

    actions = Actions()
    fields = Fields()

    __component_name__ = ''
    template = default_template

    @property
    def action_url(self):
        url = IURL(self.context, self.request, default=None)
        if url is not None:
            return u"%s/%s" % (url, self.__component_name__)
        return u""

    def __init__(self, context, request, **kwargs):
        super(FormCanvas, self).__init__(context, request, **kwargs)
        self.actionWidgets = Widgets(form=self, request=self.request)
        self.fieldWidgets = Widgets(form=self, request=self.request)
        self._updated = False

    @property
    def translate(self):
        localizer = getLocalizer()
        if localizer is not None:
            return localizer.translate
        return None

    def update(self, *args, **kwargs):
        pass

    def namespace(self):
        namespace = {}
        namespace['context'] = self.context
        namespace['request'] = self.request
        namespace['form'] = self
        namespace['view'] = self
        return namespace

    def extractData(self, fields=None):
        if fields is None:
            fields = self.fields
        return super(FormCanvas, self).extractData(fields)

    def haveRequiredFields(self):
        return reduce(
            operator.or_,
            [False] + map(operator.attrgetter('required'), self.fields))

    def updateActions(self):
        action, result = self.actions.process(self, self.request)
        if ISuccessMarker.providedBy(result) and result.url is not None:
            code = result.code or 302
            exception = REDIRECTIONS[code]
            raise exception(result.url)
        return action, result

    def updateWidgets(self):
        self.fieldWidgets.extend(self.fields)
        self.actionWidgets.extend(self.actions)

        self.fieldWidgets.update()
        self.actionWidgets.update()

    def render(self, *args, **kwargs):
        """This is the default render method.
        Not providing a template will make it fails.
        Override this method, if needed (eg: return a string)
        """
        if self.template is None:
            raise NotImplementedError("Template is not defined.")
        return self.template.render(
            self, translate=self.translate, **self.namespace())


@implementer(IFormView)
class StandaloneForm(object):
    """This is a base for a standalone form, process the form.
    """
    template = default_template
    responseFactory = None  # subclass has to provide one.
    make_response = make_form_response

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def namespace(self):
        """Returns a dictionary of namespaces that the template
        implementation expects to always be available.
        """
        return {
            'view': self,
            'form': self,
            'context': self.context,
            'request': self.request,
            }

    @property
    def translate(self):
        localizer = getLocalizer()
        if localizer is not None:
            return localizer.translate
        return None

    def render(self):
        """This is the default render method.
        Not providing a template will make it fails.
        Override this method, if needed (eg: return a string)
        """
        if self.template is None:
            raise NotImplementedError("Template is not defined.")
        return self.template.render(
            self, translate=self.translate, **self.namespace())

    def update(self):
        """Update is called prior to any rendering. This method is left
        empty on purpose, so it can be overriden easily.
        """
        pass

    def updateActions(self):
        return None, None

    def updateWidgets(self):
        pass

    def updateForm(self):
        if self._updated is False:
            self.updateActions()
            self.updateWidgets()
            self._updated = True

    def __call__(self, *args, **kwargs):
        try:
            self.update(*args, **kwargs)
            self.updateForm()
            result = self.render(*args, **kwargs)
            return self.make_response(result, *args, **kwargs)
        except HTTPRedirect as exc:
            return redirect_exception_response(self.responseFactory, exc)


@implementer(interfaces.ISimpleForm)
class Form(FormCanvas, StandaloneForm):
    """A full simple standalone form.
    """
    def __init__(self, context, request, **kwargs):
        content = kwargs.get('content', context)
        FormCanvas.__init__(self, context, request, content=content)

    def update(self, *args, **kwargs):
        FormCanvas.update(self, *args, **kwargs)
        StandaloneForm.update(self, *args, **kwargs)


moduleProvides(interfaces.IFormComponents)
__all__ = list(interfaces.IFormComponents)
