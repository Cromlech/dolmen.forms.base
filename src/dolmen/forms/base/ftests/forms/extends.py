"""
Test the extends directive

Let's configure our example:

  >>> from . import extends as module
  >>> from crom import configure
  >>> configure(module)

We can look for the extended form, it will contains fields and action
of the original one:

  >>> from cromlech.browser.testing import TestRequest
  >>> request = TestRequest()
  >>> context = object()

  >>> from cromlech.browser import IForm
  >>> form = IForm(context, request, name='othernameform')

  >>> form
  <dolmen.forms.base.ftests.forms.extends.OtherNameForm object at ...>

  >>> len(form.fields)
  1
  >>> list(form.fields)
  [<Field Name>]

  >>> len(form.actions)
  2
  >>> list(form.actions)
  [<DecoratedAction Register>, <DecoratedAction Kill>]

"""

from dolmen.forms.base import Form, Field, Fields
from dolmen.forms.base import form_component, extends, action


@form_component
class NameForm(Form):

    label = u"Name"
    description = u"Name form"
    fields = Fields(Field("Name"))
    fields['name'].description = 'Name of the candidate'
    fields['name'].required = True

    @action(u"Register")
    def register(self):
        data, errors = self.extractData()
        if errors:
            return
        # In case of success we don't keep request value in the form
        self.ignoreRequest = True
        self.status = u"Registered %(name)s" % data


@form_component
class OtherNameForm(NameForm):
    extends(NameForm)

    @action(u"Kill")
    def kill(self):
        data, errors = self.extractData()
        if errors:
            return
        self.status = u"Dead man you are %(name)s" % data
