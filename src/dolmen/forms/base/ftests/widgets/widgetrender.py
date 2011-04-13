"""
We are going to define a custom widget here which define its rendering
HTML using a render method.

Let's grok our example:

  >>> from dolmen.forms.base.testing import grok
  >>> grok('dolmen.forms.base.ftests.widgets.widgetrender')

So now should be to lookup our widget:

  >>> from dolmen.forms.base.ftests.widgets.widgetrender import MyField
  >>> field = MyField("Cool Test")
  >>> field
  <MyField Cool Test>

  >>> from zope.publisher.browser import TestRequest
  >>> request = TestRequest()

  >>> from dolmen.forms.base.form import Form
  >>> form = Form(None, request)

  >>> from dolmen.forms.base import interfaces
  >>> from zope import component
  >>> widget = component.getMultiAdapter(
  ...     (field, form, request), interfaces.IWidget)
  >>> widget
  <MyWidget Cool Test>

And we are able now to call its render method:

  >>> print widget.render()
  <p>Too complicated widget for Cool Test</p>

"""

from dolmen.forms.base.fields import Field
from dolmen.forms.base.widgets import Widget
from dolmen.forms.base import interfaces
from zope.interface import Interface
from grokcore import component as grok


class MyField(Field):
    """A custom field.
    """


class MyWidget(Widget):
    """Custom widget to render my field
    """
    grok.adapts(MyField, interfaces.IFormCanvas, Interface)

    def render(self):
        return u"<p>Too complicated widget for %s</p>" % (
            self.component.title)
