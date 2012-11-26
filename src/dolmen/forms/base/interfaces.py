# -*- coding: utf-8 -*-

from zope import schema
from zope.interface import Interface, Attribute
from zope.configuration.fields import GlobalObject
from cromlech.browser.interfaces import IRenderable, IView, IForm
from dolmen.collection import (
    ICollection, IComponent, IComponentFactory, IMutableCollection)


class IModeMarker(Interface):
    """This interface identifies a form mode and defines if it allows
    data extraction.
    """
    extractable = Attribute(
        u"Boolean allowing or not the extraction of the data,"
        u" for components in that mode.")


class ISuccessMarker(Interface):
    """This interface identifies a form action result marker.
    Please note that 'code' and 'url' can be overlooked by the form.
    They are merey 'recommandations' from the action. To enforce a
    redirection in the action and possibly skip the form treatment,
    a HTTPRediction error can be raised instead.
    """
    success = Attribute(u"Boolean result of the form action.")
    code = Attribute(u"The redirection or response code recommanded.")
    url = Attribute(u"The URL to use for the recommanded redirection.")

    def __non_zero__():
        """The marker must be able to resolve itself into a boolean.
        """


class IPrefixable(Interface):
    """An object with a prefix.
    """
    prefix = Attribute("Prefix")


class IRenderableComponent(IPrefixable, IComponent):
    """A component that can be rendered with the help of a widget.
    """
    mode = Attribute(u"Mode should be used to render the component")

    def available(form):
        """Return a boolean to qualify if the component wants to be
        rendered in the given context (i.e. form).
        """


class IFieldExtractionValueSetting(IPrefixable):
    """Setting to extract field values.
    """
    ignoreRequest = Attribute(u"Ignore request values")
    ignoreContent = Attribute(u"Ignore content values")
    mode = Attribute(u"Mode should be used to render all the widgets")


class IDataManager(Interface):
    """A data manager let you access content.
    """

    def __init__(content):
        """Initialize the data manager for the given content.
        """

    def getContent():
        """Return the content managed by this data manager.
        """

    def get(identifier):
        """Return content value associated to the given identifier or
        raise KeyError.
        """

    def set(identifier, value):
        """Modifiy content value associated to the given identifier.
        """


class IFormData(IFieldExtractionValueSetting, IForm):
    """Form data processing facilities.
    """
    dataManager = Attribute(u"Data manager class used to access content.")
    status = Attribute(u"Form status message.")

    errors = Attribute(
        u"Iterable of the errors that occured during the form processing.")
    formErrors = Attribute(
        u"Main errors that occurred during the form processing.")

    def getContentData():
        """Returns the content that will be used for the form processing.
        """

    def setContentData(content):
        """Sets the content that will be used as the form processing context.
        """

    def validateData(fields, data):
        """Validates the form in a global way and returns a collection
        of errors (if any occured) or None.
        """

    def extractData(fields):
        """Returns the form data and errors for the given fields.
        """


class ActionError(Exception):
    """A error happening while processing the form.
    """


class IAction(IRenderableComponent):
    """A form action.
    """
    description = Attribute(u"Describe the action")

    def validate(form):
        """Self validation of values in order to run.
        """

    def __call__(form):
        """Execute the action.
        """


class IActions(ICollection):
    """A list of actions.
    """

    def process(form, request):
        """Execute actions.
        """


class IField(IRenderableComponent, IFieldExtractionValueSetting):
    """A form field.
    """
    description = Attribute(u"Field description")
    required = Attribute(u"Boolean indicating if the field is required")
    readonly = Attribute(u"Boolean indicating if the field is read-only")

    def getDefaultValue(form):
        """Return the default value.
        """

    def validate(value, context=None):
        """Validate that the given value fullfil the field
        requirement.
        """


class IFieldFactory(IComponentFactory):
    """Factory to create zeam.form Fields from other components than
    zeam.form ones.
    """


class IFields(ICollection):
    """A collection of fields.
    """


class IError(IComponent):
    """A error.
    """


class IErrors(IMutableCollection):
    """A collection of errors.
    """


class IWidget(IComponent):
    """Display a form component on the page.
    """

    def htmlId():
        """Return the HTML id of the HTML component representing the
        widget.
        """

    def htmlClass():
        """Return an HTML class to mark the widget with.
        """

    def render():
        """Return the rendered HTML of the widget.
        """


class IFieldWidget(IWidget):
    """Widget for fields.
    """
    description = Attribute(u"Description of the field")
    error = Attribute(u"Field error, or None")
    required = Attribute(u"Boolean indicating if the field is required")
    readonly = Attribute(u"Boolean indicating if field is read-only")


class IWidgetExtractor(Interface):
    """The counterpart of the Widget, used to extract widget value
    from the request.
    """

    def extract():
        """Return a tuple (value, error). Value must be a valid field
        value. If error is not None, value is discarded.
        """

    def extractRaw():
        """Return request entries needed for the widget to redisplay
        the same information in case of validation failure.
        """


class IWidgets(ICollection):
    """A collection of widgets.
    """


class IFormCanvas(IPrefixable, IFieldExtractionValueSetting, IRenderable):
    """Definition of a form structure.
    Form presentation : label, description
    Form contents and actions : fields, actions and their related methods.
    """
    label = Attribute(u"Form title")
    description = Attribute(u"Form description")

    actions = Attribute(u"Form actions")
    fields = Attribute(u"Form fields")

    action_url = Attribute(u"Url for form submission")

    def htmlId():
        """Return an identifier that can be used in the HTML code to
        identify the form.
        """

    def haveRequiredFields():
        """Return an boolean True if any of the fields are required.
        """

    def updateActions():
        """Set up and run form actions.
        """

    def updateWidgets():
        """Set up rendering field / action widgets and their value to
        display.
        """


class ISimpleFormCanvas(IFormCanvas, IFormData):
    """A simple form canvas with only fields and actions.
    """
    actionWidgets = Attribute(u"Form widgets")
    fieldWidgets = Attribute(u"Form widgets")


class IForm(IView, IFormCanvas):
    """Regular form containing fields and actions, that you can call,
    and will be updated and rendered.
    """

    def updateForm():
        """Update the form mechanism (setup fields, actions, run
        actions, setup widgets).
        """

    def __call__():
        """Update and render the form.
        """


class ISimpleForm(IForm, ISimpleFormCanvas):
    """A simple form, with fields and actions.
    """


class IFieldUpdate(Interface):
    """Defines a field update adapter. A field update adapter is called
    when an object is updated. It adapts the field itself and the object
    on which it has been modified. It allows high pluggability in forms
    treatments.
    """
    field = schema.Object(
        required=True,
        title=u"The field that has been updated.",
        schema=schema.interfaces.IField)

    object = GlobalObject(
        required=True,
        title=u"The object concerned by the field update.")


class IActionsAPI(Interface):
    Action = Attribute(u"A form action")
    Actions = Attribute(u"A collection of actions")
    action = Attribute(u"Decorator to use a form method as an Action")


class IFieldsAPI(Interface):
    Field = Attribute(u"A form field")
    Fields = Attribute(u"A collection of fields")


class IWidgetsAPI(Interface):
    Widgets = Attribute(u"A collection of widgets")


class IDirectivesAPI(Interface):
    name = Attribute(u"Form name used in the registration.")
    context = Attribute(u"Context discriminant for the registration.")
    request = Attribute(u"Request discriminant for the registration.")
    require = Attribute(u"Permission to access and render the form.")


class IDataManagersAPI(Interface):
    ObjectDataManager = Attribute(
        u"Data manager to work with values as attribute of an object")
    DictDataManager = Attribute(
        u"Data manager to work with values in dictionary")
    NoneDataManager = Attribute(
        u"Data manager to work directly with a value")
    makeAdaptiveDataManager = Attribute(
        u"Data manager to work with from an simple adapter")


class IMarkersAPI(Interface):
    Marker = Attribute(u"Base class for forms markers.")
    ModeMarker = Attribute(u"Base class for form modes markers.")
    SuccessMarker = Attribute(u"Base class form action result markers.")

    DEFAULT = Attribute(u"Use the default value.")
    NO_VALUE = Attribute(u"No value to use.")
    NO_CHANGE = Attribute(u"No modifications.")

    DISPLAY = Attribute(u"Mode Marker to get display widgets.")
    INPUT = Attribute(u"Mode Marker to get input widgets.")
    HIDDEN = Attribute(u"Mode Marker to get hidden widgets.")

    SUCCESS = Attribute(u"Action return : action was successful.")
    FAILURE = Attribute(u"Action return : a failure occured.")
    NOTHING_DONE = Attribute(u"Action return : nothing has been done.")


class IFormComponents(Interface):
    FormCanvas = Attribute(u"The base structure of a Form.")
    FormData = Attribute(u"A configuration object to render fields as widgets")
    Form = Attribute(u"A basic and simple Form")


class IDolmenFormsBaseAPI(
    IActionsAPI, IFieldsAPI, IWidgetsAPI, IDirectivesAPI,
    IDataManagersAPI, IMarkersAPI, IFormComponents):
    """Base form API.
    """
