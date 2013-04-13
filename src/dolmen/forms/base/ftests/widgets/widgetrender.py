"""
We are going to define a custom widget here which define its rendering
HTML using a render method.

Let's configure our example::

  >>> from . import widgetrender as module
  >>> from crom import configure
  >>> configure(module)

So now should be to lookup our widget::

  >>> from dolmen.forms.base.ftests.widgets.widgetrender import MyField
  >>> field = MyField("Cool Test")
  >>> field
  <MyField Cool Test>

  >>> from cromlech.browser.testing import TestRequest
  >>> request = TestRequest()

  >>> from dolmen.forms.base import Form
  >>> form = Form(None, request)

  >>> from dolmen.forms.base import interfaces
  >>> widget = interfaces.IWidget(field, form, request)
  >>> widget
  <MyWidget Cool Test>

And we are able now to call its render method::

  >>> print widget.render()
  <p>Too complicated widget for Cool Test</p>

Note that defining a template or a render method is mandatory ::

  >>> field2 = AnotherField("Bad Test")
  >>> widget = interfaces.IWidget(field2, form, request)
  >>> widget
  <NoRenderWidget Bad Test>
  >>> print widget.render()
  Traceback (most recent call last):
  ...
  ComponentLookupError...

"""

import crom
from dolmen.forms.base.fields import Field
from dolmen.forms.base.widgets import Widget
from dolmen.forms.base import interfaces
from zope.interface import Interface


class MyField(Field):
    """A custom field.
    """


@crom.adapter
@crom.target(interfaces.IWidget)
@crom.sources(MyField, interfaces.IFormCanvas, Interface)
class MyWidget(Widget):
    """Custom widget to render my field
    """
    def render(self):
        return u"<p>Too complicated widget for %s</p>" % (
            self.component.title)


class AnotherField(Field):
    """A custom field.
    """


@crom.adapter
@crom.target(interfaces.IWidget)
@crom.sources(AnotherField, interfaces.IFormCanvas, Interface)
class NoRenderWidget(Widget):
    """Custom widget to render my field
    """
    pass
