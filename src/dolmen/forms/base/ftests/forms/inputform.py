"""
We define here a simple form with two fields and one action registered
with a decorator.

Let's grok our example::

  >>> from dolmen.forms.base.testing import grok
  >>> grok('dolmen.forms.base.ftests.forms.inputform')

We can now lookup our form by the name of its class::

  >>> from cromlech.io.testing import TestRequest
  >>> request = TestRequest()

  >>> from zope.location import Location
  >>> context = Location()

  >>> from zope import component
  >>> form = component.getMultiAdapter(
  ...     (context, request), name='registration')
  >>> form
  <dolmen.forms.base.ftests.forms.inputform.Registration object at ...>

  >>> len(form.fields)
  2
  >>> len(form.actions)
  1

Integration tests
-----------------


  >>> app = makeApplication("registration")
  >>> from infrae.testbrowser.browser import Browser
  >>> browser = Browser(app)
  >>> browser.handleErrors = False

Empty submission
~~~~~~~~~~~~~~~~

We are going just to submit the form without giving any required
information, and we should get an error::

  >>> browser.open('http://localhost/registration')
  200
  >>> form = browser.get_form(id='form')
  >>> action = form.get_control('form.action.register')
  >>> action.name, action.type
  ('form.action.register', 'submit')

  >>> action.click()
  200

  >>> 'Missing required value' in browser.contents
  True
  >>> 'Registered' in browser.contents
  False

Valid submission
~~~~~~~~~~~~~~~~

Let's get our control for fields and filled them, and submit the form::

  >>> browser.open('http://localhost/registration')
  200
  >>> form = browser.get_form(id='form')
  >>> name = form.get_control('form.field.name')
  >>> name.name, name.type
  ('form.field.name', 'text')
  >>> name.value = 'Sylvain Viollon'
  >>> job = form.get_control('form.field.job')
  >>> job.name, job.type
  ('form.field.job', 'text')
  >>> job.value = 'Developer'

  >>> form.get_control('form.action.register').click()
  200

  >>> 'Registered Sylvain Viollon as Developer' in browser.contents
  True

Our action says that you can ignore the request if it succeed (and it
is the case here)::

  >>> form = browser.get_form(id='form')
  >>> form.get_control('form.field.name').value
  ''
  >>> form.get_control('form.field.job').value
  ''

Incomplete submission
~~~~~~~~~~~~~~~~~~~~~

In case of an incomplete submission, fields should keep the value they
got for that submission::

  >>> browser.open('http://localhost/registration')
  200
  >>> form = browser.get_form(id='form')
  >>> job = form.get_control('form.field.job')
  >>> job.name, job.type
  ('form.field.job', 'text')
  >>> job.value = 'Designer'

  >>> form.get_control('form.action.register').click()
  200
  >>> 'Missing required value' in browser.contents
  True
  >>> 'Registered' in browser.contents
  False

  >>> form = browser.get_form(id='form')
  >>> new_job = form.get_control('form.field.job')
  >>> new_job.value
  'Designer'

And so now we can finish to submit the form, and form values should be
gone (as we successfully submit the form)::

  >>> form.get_control('form.field.name').value = 'Wim Boucqueart'
  >>> form.get_control('form.action.register').click()
  200
  >>> 'Missing required value' in browser.contents
  False
  >>> 'Registered Wim Boucqueart as Designer' in browser.contents
  True

  >>> form = browser.get_form(id='form')
  >>> form.get_control('form.field.name').value
  ''
  >>> form.get_control('form.field.job').value
  ''


"""


from dolmen.forms import base
from grokcore import component as grok
from zope.interface import Interface
from cromlech.webob.response import Response


class Registration(base.Form):

    grok.context(Interface)

    responseFactory = Response

    label = u"My form"
    description = u"The description of my form"
    fields = base.Fields(base.Field("Name"), base.Field("Job"))
    fields['name'].description = 'Name of the candidate'
    fields['name'].required = True

    @base.action(u"Register")
    def register(self):
        data, errors = self.extractData()
        if errors:
            return
        # In case of success we don't keep request value in the form
        self.ignoreRequest = True
        self.status = u"Registered %(name)s as %(job)s" % data
