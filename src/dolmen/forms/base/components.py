# -*- coding: utf-8 -*-

import operator
from os import path
import binascii

from cromlech.browser.interfaces import IRenderable, IURL
from cromlech.browser.exceptions import HTTPRedirect, REDIRECTIONS
from cromlech.browser.utils import redirect_exception_response
from cromlech.i18n import ILanguage
from cromlech.browser import getSession

from dolmen.template import TALTemplate
from dolmen.view import View
from dolmen.forms.base import _
from dolmen.forms.base import interfaces
from dolmen.forms.base.actions import Actions
from dolmen.forms.base.datamanagers import ObjectDataManager
from dolmen.forms.base.errors import Errors, Error
from dolmen.forms.base.fields import Fields
from dolmen.forms.base.markers import NO_VALUE, INPUT
from dolmen.forms.base.widgets import Widgets, WidgetFactory
from dolmen.forms.base.interfaces import ICollection, ISuccessMarker
from dolmen.forms.base.interfaces import IError, InvalidCSRFToken
from dolmen.forms.base.interfaces import CSRFTokenGenerationError

from grokcore import component as grok
from zope import interface
from zope.component import queryMultiAdapter
from zope.cachedescriptors.property import Lazy


PATH = path.join(path.dirname(__file__), 'default_templates')
default_template = TALTemplate(path.join(PATH, "formtemplate.pt"))

_marker = object()





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
    clone.methods = original.methods
    clone.formMethod = original.formMethod
    clone.enctype = original.enctype
    clone.widgetFactoryFactory = original.widgetFactoryFactory
    
    # Unpiling the error stack
    errors = original.errors.get(clone.prefix, None)
    if errors is not None:
        # errors must be a dict-like iterable.
        # we use the convenient "Errors"
        if not ICollection.providedBy(errors):
            errors = Errors(errors)
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
        if not key in self:
            raise KeyError(key)
        value = super(FieldsValues, self).get(key, default)
        if value is NO_VALUE:
            value = self.fields[key].getDefaultValue(self.form)
            if value is NO_VALUE:
                return default
        return value

    def getDictWithDefault(self, default=None):
        result = {}
        for key in self.keys():
            result[key] = self.getWithDefault(key, default=default)
        return result

    # BBB
    getDefault = getWithDefault


@interface.implementer(interfaces.IFormData)
class FormData(Object):
    """This represent a submission of a form. It can be used to update
    widgets and run actions.
    """
    prefix = 'form'
    parent = None
    mode = INPUT
    dataManager = ObjectDataManager
    widgetFactoryFactory = WidgetFactory
    dataValidators = []

    formMethod = 'POST'
    enctype = 'multipart/form-data'
    methods = frozenset(('POST', 'GET'))
    
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

    @Lazy
    def widgetFactory(self):
        return self.widgetFactoryFactory(self, self.request)

    @property
    def formErrors(self):
        error = self.errors.get(self.prefix, None)
        if error is None:
            return []
        if ICollection.providedBy(error):
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

    def validateData(self, fields, data):
        errors = Errors()
        for factory in self.dataValidators:
            validator = factory(fields, self)
            for error in validator.validate(data):
                if not IError.providedBy(error):
                    error = Error(error, self.prefix)
                errors.append(error)
        return errors

    @cached('_extracted')
    def extractData(self, fields):
        # XXX to review this
        cached = self._extracted.get(fields)
        if cached is not None:
            return cached
        data = FieldsValues(self, fields)
        errors = Errors()
        self._extracted[fields] = (data, errors)

        for field in fields:
            if not field.available(self):
                continue

            # Widget extraction and validation
            extractor = self.widgetFactory.extractor(field)
            if extractor is not None:
                value, error = extractor.extract()
                if error is None:
                    error = field.validate(value, self)
                if error is not None:
                    if not IError.providedBy(error):
                        error = Error(error, extractor.identifier)
                    errors.append(error)
                data[field.identifier] = value

        # Generic form validation
        errors.extend(self.validateData(fields, data))
        if len(errors):
            # Add a form level error if not already present
            if self.prefix not in errors:
                errors.append(
                    Error(_(u"There were errors.", default=u"There were errors."),
                          self.prefix))
        self.errors = errors
        return (data, errors)


@interface.implementer(IRenderable, interfaces.ISimpleFormCanvas)
class FormCanvas(FormData):
    """This represent a simple form setup: setup some fields and
    actions, prepare widgets for it.
    """
    grok.baseclass()

    label = u''
    description = u''

    actions = Actions()
    fields = Fields()

    protected = False
    csrftoken = None
    
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

    def setUpToken(self, response):
        session = getSession()
        if session is None:
            raise CSRFTokenGenerationError("No session.")
        self.csrftoken = session.get('__csrftoken__')
        if self.csrftoken is None:
            self.csrftoken = str(binascii.hexlify(os.urandom(32)))
            session['__csrftoken__'] = self.csrftoken
        
    def checkToken(self):
        session = getSession()
        if session is None:
            raise CSRFTokenGenerationError("No session.")
        cookietoken = session.get('__csrftoken__')
        if cookietoken is None:
            raise InvalidCSRFToken(_('Invalid CSRF token'))
        if cookietoken != self.request.form.get('__csrftoken__', None):
            raise InvalidCSRFToken(_('Invalid CSRF token'))

    @property
    def target_language(self):
        return ILanguage(self.request, None)

    def update(self, *args, **kwargs):
        if self.protected:
            self.setUpToken()

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
        if action is not None and self.protected:
            # This form has CSRF protection enabled.
            self.checkToken()

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
        return self, None, None

    def updateWidgets(self):
        pass

    def updateForm(self):
        self.updateActions()
        self.updateWidgets()

    def __call__(self, *args, **kwargs):
        try:
            self.update(*args, **kwargs)
            self.updateForm()
            result = self.render(*args, **kwargs)
            return self.make_response(result, *args, **kwargs)
        except HTTPRedirect, exc:
            return redirect_exception_response(self.responseFactory, exc)


@interface.implementer(interfaces.ISimpleForm)
class Form(FormCanvas, StandaloneForm):
    """A full simple standalone form.
    """
    grok.baseclass()


def extends(*forms, **opts):
    # Extend a class with parents components
    field_type = opts.get('fields', 'all')

    def extendComponent(field_type):
        factory = {'actions': Actions, 'fields': Fields}.get(field_type)
        if factory is None:
            raise ValueError(u"Invalid parameter fields to extends")
        frame = sys._getframe(2)
        f_locals = frame.f_locals
        components = f_locals.setdefault(field_type, factory())
        components.extend(*map(operator.attrgetter(field_type), forms))

    if field_type == 'all':
        extendComponent('actions')
        extendComponent('fields')
    else:
        extendComponent(field_type)


interface.moduleProvides(interfaces.IFormComponents)
__all__ = list(interfaces.IFormComponents)
