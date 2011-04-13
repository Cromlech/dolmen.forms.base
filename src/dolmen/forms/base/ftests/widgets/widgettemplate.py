"""
We are going to define a custom widget here which define its rendering
HTML using a template associated with Grok.

Let's grok our example:

  >>> from dolmen.forms.base.testing import grok
  >>> grok('dolmen.forms.base.ftests.widgets.widgettemplate')

So now should be to lookup our widget:

  >>> from dolmen.forms.base.ftests.widgets.widgettemplate import MyField
  >>> field = MyField("Cool Template Test")
  >>> field
  <MyField Cool Template Test>

  >>> from zope.publisher.browser import TestRequest
  >>> request = TestRequest()

  >>> from dolmen.forms.base.form import Form
  >>> form = Form(None, request)

  >>> from dolmen.forms.base import interfaces
  >>> from zope import component
  >>> widget = component.getMultiAdapter(
  ...     (field, form, request), interfaces.IWidget)
  >>> widget
  <MyWidget Cool Template Test>

And we are able now to call its render method:

  >>> print widget.render()
  <p>Nice template for Cool Template Test</p>


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
    """Custom widget to render my field.
    """
    grok.adapts(MyField, interfaces.IFormCanvas, Interface)
