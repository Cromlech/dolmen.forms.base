# -*- coding: utf-8 -*-

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
