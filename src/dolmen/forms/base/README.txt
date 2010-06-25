=================
dolmen.forms.base
=================

`dolmen.forms.base` is a package in charge of providing basic
functionalities to work with `zeam.form` Forms.


From the form to the field
==========================

``dolmen.forms.base`` provides few functions dedicated to the task of
applying dict datas to object fields and to trigger events in order to
inform handlers of the updates

Applying values
---------------

We create our test model::

  >>> from zope.schema import TextLine, Choice
  >>> from zope.interface import Interface, implements
  
  >>> class ICaveman(Interface):
  ...    name = TextLine(title=u'a name')
  ...    weapon = Choice(title=u'a weapon',
  ...                    values=[u'none', u'a club', u'a spear'])

  >>> class Neanderthal(object):
  ...    implements(ICaveman)
  ...    def __init__(self):
  ...       self.name = u"no name"
  ...       self.weapon = u"none"
  
  >>> moshe = Neanderthal()
  >>> moshe.name
  u'no name'
  >>> moshe.weapon
  u'none'

We can now use the first function, `set_fields_data`. It takes the
fields list, extracted thanks to the `Fields` collection, the content
and the data dictionnary. The result of this call is a dictionnary,
with the interface in which the field is defined and the field
identifier as a value::
 
  >>> from dolmen.forms.base import Fields, set_fields_data

  >>> fields = Fields(ICaveman)
  >>> for field in fields: print field
  <TextLineSchemaField a name>
  <ChoiceSchemaField a weapon>

  >>> data = {u'name': u'Grok', u'weapon': u'a club'}

  >>> changes = set_fields_data(fields, moshe, data)
  >>> print changes
  {<InterfaceClass __builtin__.ICaveman>: ['name', 'weapon']}

  >>> moshe.name
  u'Grok'
  >>> moshe.weapon
  u'a club'

Values of the data dict can contain markers, to warn of a possible
special case : the value is missing or there are no changes. In these
two cases, the value assignation is skipped::

  >>> from dolmen.forms.base import NO_VALUE, NO_CHANGE
  >>> data = {u'name': NO_VALUE, u'weapon': NO_CHANGE}

  >>> changes = set_fields_data(fields, moshe, data)
  >>> print changes
  {}

Generating changes Attributes for events
----------------------------------------

One advantage of generating a dict of changes is that you can trigger
event that are aware of a certain format of changes. The
IObjectModifiedEvent, for exemple, uses the changes log to trigger the
reindexation of the modified fields. The function `notify_changes` is
dedicated to notifying a given event of the applied changes. It takes
the content, the changes dict and an event as arguments. If the event
argument is omitted, ObjectModifiedEvent is used by default.

We first generate a changes dict::

  >>> data = {u'name': u'Grok', u'weapon': u'a club'}
  >>> changes = set_fields_data(fields, moshe, data)
  >>> print changes
  {<InterfaceClass __builtin__.ICaveman>: ['name', 'weapon']}

We can now set a logger for the IObjectModifiedEvent, in order to
check if the changes are being broadcasted::

  >>> from zope.component import adapter, provideHandler
  >>> from zope.lifecycleevent import IObjectModifiedEvent

  >>> logger = []

  >>> @adapter(ICaveman, IObjectModifiedEvent)
  ... def changes_broadcasted(content, event):
  ...    logger.append(event.descriptions)

  >>> provideHandler(changes_broadcasted)

We can now feed it to the function::

  >>> from dolmen.forms.base import notify_changes
  >>> change_log = notify_changes(moshe, changes)

The logger must have been trigged. We can check its value::

  >>> logger
  [(<zope.lifecycleevent.Attributes object at ...>,)]

  >>> for attrs in logger[0]:  
  ...     print attrs.interface, attrs.attributes
  <InterfaceClass __builtin__.ICaveman> ('name', 'weapon')


Field update event
==================

`dolmen.forms.base` also proposes the definition of a new component that
can be used to atomize the updating process of an object: `IFieldUpdate`.

To demonstrate this `IFieldUpdate`, we are going to implement a simple
usecase where we instanciate a content, change a value and notify the
`IFieldUpdate` components. For that, we'll use a basic logger object::

  >>> logger = []

Once this is done, we can define two `IFieldUpdate` components. We
implement them as named adapters. We'll retrieve them thanks to a
"getAdapters" call::

  >>> from zope.interface import implementer
  >>> from dolmen.forms.base import IFieldUpdate

  >>> @implementer(IFieldUpdate)
  ... @adapter(TextLine, ICaveman)
  ... def updated_title(field, context):
  ...    if field.__name__ == u"name":
  ...       logger.append('Name updated on %r with `%s`' %
  ...                     (context, getattr(context, field.__name__)))

  >>> @implementer(IFieldUpdate)
  ... @adapter(TextLine, Interface)
  ... def updated_textfield(field, context):
  ...    logger.append('A text field has been updated')


The components need to be named since they are adapters: we don't want
them to override each other. For the example, we want them both. let's
register them::

  >>> from zope.component import provideAdapter
  >>> provideAdapter(updated_title, name="updatetitle")
  >>> provideAdapter(updated_textfield, name="updatetext")

Now, we develop the small scenarii : we instanciate a Content,
add a value for the `name` attribute and call the adapters:: 

  >>> manfred = Neanderthal()
  >>> manfred.name = u"Manfred the Mighty"

  >>> from zope.component import getAdapters
  >>> adapters = getAdapters((ICaveman['name'], manfred), IFieldUpdate)
  >>> for adapter in adapters:
  ...   # We run through the generator
  ...   pass

  >>> for line in logger: print line
  Name updated on <Neanderthal object at ...> with `Manfred the Mighty`
  A text field has been updated


The form model
==============

``dolmen.forms.base`` provides a form baseclass defining several
useful methods and overriding some default behavior from
``zeam.form``.

  >>> from zope.interface import implementedBy
  >>> from dolmen.forms.base import ApplicationForm
  
The provided component, ``ApplicationForm``, inherits from the base
``zeam.form`` components and implements some extra methods, allowing
it to fit into your application, such as ``flash``, to emit messages
to given sources. It's also layout aware::

  >>> for interface in implementedBy(ApplicationForm):
  ...     print interface
  <InterfaceClass megrok.layout.interfaces.IPage>
  <InterfaceClass zeam.form.base.interfaces.ISimpleForm>
  <InterfaceClass zeam.form.base.interfaces.ISimpleFormCanvas>
  <InterfaceClass zeam.form.base.interfaces.IGrokViewSupport>
  <InterfaceClass zeam.form.base.interfaces.IFormData>
  <InterfaceClass zope.publisher.interfaces.browser.IBrowserPage>
  <InterfaceClass zope.browser.interfaces.IBrowserView>
  <InterfaceClass zope.location.interfaces.ILocation>

As ``zeam.form`` uses Chameleon as a template engine, it is import we
are able to compute the current request locale, in order to get the
right translation environment::

  >>> from grokcore.component import Context
  >>> from zope.publisher.browser import TestRequest

  >>> item = Context()
  >>> request = TestRequest()

  >>> form = ApplicationForm(item, request)
  >>> print form.i18nLanguage
  None

  >>> request = TestRequest(environ={'HTTP_ACCEPT_LANGUAGE': "en,fr"})
  >>> form = ApplicationForm(item, request)
  >>> print form.i18nLanguage
  en

Further more, the `ApplicationForm` overrides the ``extractData``
method from the ``zeam.form`` Form in order to compute the interfaces
invariants.


Declaring the invariants
------------------------

  >>> from zope.schema import Password
  >>> from zope.interface import invariant, Interface
  >>> from zope.interface.exceptions import Invalid

  >>> class IPasswords(Interface):
  ...     passwd = Password(
  ...         title=u"Password",
  ...         description=u"Type the password.",
  ...         required=True)
  ...
  ...     verify = Password(
  ...         title=u"Password checking",
  ...         description=u"Retype the password.",
  ...         required=True)
  ...
  ...     @invariant
  ...     def check_pass(data):
  ...         if data.passwd != data.verify:
  ...             raise Invalid(u"Mismatching passwords!")

  >>> from zeam.form.base import Fields
  >>> from grokcore.component import testing

  >>> class MyForm(ApplicationForm):
  ...     ignoreContent = True
  ...     ignoreRequest = False
  ...     fields = Fields(IPasswords)


Default behavior
----------------

  >>> form = MyForm(item, request)
  >>> form.update()
  >>> form.updateForm()
  >>> data, errors = form.extractData()

  >>> print data
  {'passwd': <Marker NO_VALUE>, 'verify': <Marker NO_VALUE>}

  >>> print form.formError
  None


Errors computing
----------------

  >>> post = TestRequest(form = {'form.field.passwd': u'test',
  ...                            'form.field.verify': u'fail'})
  >>> form = MyForm(item, post)
  >>> form.update()
  >>> form.updateForm()
  >>> data, errors = form.extractData()

  >>> print data
  {'passwd': u'test', 'verify': u'fail'}

The returned error is a collection of Error components. Using the form
prefix as an identifier, it logically wraps all the errors created by
the invariants validation::

  >>> print form.formError
  <Errors for 'form'>

  >>> for error in form.formError:
  ...     print error.title
  Mismatching passwords!

  >>> form.errors.get(form.prefix) == form.formError 
  True
