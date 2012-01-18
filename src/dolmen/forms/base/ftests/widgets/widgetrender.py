"""
We are going to define a custom widget here which define its rendering
HTML using a render method.

Let's grok our example::

  >>> from dolmen.forms.base.testing import grok
  >>> grok('dolmen.forms.base.ftests.widgets.widgetrender')

So now should be to lookup our widget::

  >>> from dolmen.forms.base.ftests.widgets.widgetrender import MyField
  >>> field = MyField("Cool Test")
  >>> field
  <MyField Cool Test>

  >>> from cromlech.io.testing import TestRequest
  >>> request = TestRequest()

  >>> from dolmen.forms.base import Form
  >>> form = Form(None, request)

  >>> from dolmen.forms.base import interfaces
  >>> from zope import component
  >>> widget = component.getMultiAdapter(
  ...     (field, form, request), interfaces.IWidget)
  >>> widget
  <MyWidget Cool Test>

And we are able now to call its render method::

  >>> print widget.render()
  <p>Too complicated widget for Cool Test</p>

Note that defining a template or a render method is mandatory ::

  >>> field2 = AnotherField("Bad Test")
  >>> widget = component.getMultiAdapter(
  ...     (field2, form, request), interfaces.IWidget)
  >>> widget
  <NoRenderWidget Bad Test>
  >>> print widget.render()
  Traceback (most recent call last):
  ...
  ComponentLookupError: ((<NoRenderWidget Bad Test>,
           <cromlech.io.testing.TestRequest object at 0x...>),
           <InterfaceClass cromlech.browser.interfaces.ITemplate>, u'')

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


class AnotherField(Field):
    """A custom field.
    """


class NoRenderWidget(Widget):
    """Custom widget to render my field
    """
    grok.adapts(AnotherField, interfaces.IFormCanvas, Interface)
