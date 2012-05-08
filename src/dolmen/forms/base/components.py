# -*- coding: utf-8 -*-

import operator
from os import path

from cromlech.browser.interfaces import IRenderable, IURL
from cromlech.browser.exceptions import HTTPRedirect, REDIRECTIONS
from cromlech.browser.utils import redirect_exception_response
from cromlech.i18n import ILanguage

from dolmen.template import TALTemplate
from dolmen.view import View
from dolmen.forms.base import _
from dolmen.forms.base import interfaces
from dolmen.forms.base.actions import Actions
from dolmen.forms.base.datamanagers import ObjectDataManager
from dolmen.forms.base.errors import Errors, Error
from dolmen.forms.base.fields import Fields
from dolmen.forms.base.markers import NO_VALUE, INPUT
from dolmen.forms.base.widgets import Widgets, getWidgetExtractor
from dolmen.forms.base.interfaces import ICollection, ISuccessMarker

from grokcore import component as grok
from zope import interface
from zope.component import queryMultiAdapter


PATH = path.join(path.dirname(__file__), 'default_templates')
default_template = TALTemplate(path.join(PATH, "formtemplate.pt"))

_marker = object()


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
    clone.postOnly = original.postOnly
    clone.formMethod = original.formMethod
    clone.enctype = original.enctype
    clone.mode = original.mode
    clone.parent = original
    if prefix is None:
        clone.prefix = original.prefix
    else:
        clone.prefix = prefix
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


class FormData(Object):
    """This represent a submission of a form. It can be used to update
    widgets and run actions.
    """
    grok.implements(interfaces.IFormData)

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
        self.__extracted = {}
        self.__content = None
        if content is _marker:
            content = context
        self.setContentData(content)

    @property
    def formErrors(self):
        error = self.errors.get(self.prefix, None)
        if error is None or ICollection.providedBy(error):
            return error
        return [error]

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

    def validateData(self, fields, data, errors):
        for factory in self.dataValidators:
            validator = factory(fields, self)
            for error in validator.validate(data):
                errors.append(Error(error.args[0], self.prefix))
        if len(errors):
            if self.prefix not in errors:
                errors.append(Error(_(u"There were errors."), self.prefix))
        return errors

    def extractData(self, fields):
        # XXX to review this
        cached = self.__extracted.get(fields)
        if cached is not None:
            return cached
        data = FieldsValues(self, fields)
        errors = Errors()
        self.__extracted[fields] = (data, errors)

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
                    errors.append(Error(error, field.identifier))
                data[field.identifier] = value

        # Generic form validation
        errors = self.validateData(fields, data, errors)
        self.errors = errors
        return (data, errors)


class FormCanvas(FormData):
    """This represent a simple form setup: setup some fields and
    actions, prepare widgets for it.
    """
    grok.baseclass()
    grok.implements(IRenderable, interfaces.ISimpleFormCanvas)

    label = u''
    description = u''

    actions = Actions()
    fields = Fields()

    __component_name__ = ''
    template = default_template

    @property
    def action_url(self):
        url = queryMultiAdapter((self.context, self.request), IURL)
        if url is not None:
            return u"%s/%s" % (url, self.__component_name__)
        return u""

    def __init__(self, context, request):
        super(FormCanvas, self).__init__(context, request)
        self.actionWidgets = Widgets(form=self, request=self.request)
        self.fieldWidgets = Widgets(form=self, request=self.request)
        self._updated = False

    @property
    def target_language(self):
        return ILanguage(self.request, None)

    def update(self, *args, **kwargs):
        pass

    def namespace(self):
        namespace = {}
        namespace['context'] = self.context
        namespace['request'] = self.request
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
            self, target_language=self.target_language, **self.namespace())


class StandaloneForm(View):
    """This is a base for a standalone form, process the form.
    """
    grok.baseclass()
    template = default_template

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
        except HTTPRedirect, exc:
            return redirect_exception_response(self.responseFactory, exc)


class Form(FormCanvas, StandaloneForm):
    """A full simple standalone form.
    """
    grok.baseclass()
    grok.implements(interfaces.ISimpleForm)

    def update(self, *args, **kwargs):
        FormCanvas.update(self, *args, **kwargs)
        StandaloneForm.update(self, *args, **kwargs)


interface.moduleProvides(interfaces.IFormComponents)
__all__ = list(interfaces.IFormComponents)
