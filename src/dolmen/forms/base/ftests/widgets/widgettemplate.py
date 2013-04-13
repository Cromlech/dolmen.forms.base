"""
We are going to define a custom widget here which define its rendering
HTML using a template associated with Grok.

Let's configure our example:

  >>> from . import widgettemplate as module
  >>> from crom import configure
  >>> configure(module)

So now should be to lookup our widget:

  >>> field = MyField("Cool Template Test")
  >>> field
  <MyField Cool Template Test>

  >>> from cromlech.browser.testing import TestRequest
  >>> request = TestRequest()

  >>> from dolmen.forms.base import Form
  >>> form = Form(None, request)

  >>> widget = interfaces.IWidget(field, form, request)
  >>> widget
  <MyWidget Cool Template Test>

And we are able now to call its render method:

  >>> print widget.render()
  <p>Nice template for Cool Template Test</p>


"""

import crom
import os.path
from cromlech.browser import ITemplate
from dolmen.forms.base.fields import Field
from dolmen.forms.base.widgets import Widget
from dolmen.forms.base import interfaces
from dolmen.template import TALTemplate
from zope.interface import Interface


class MyField(Field):
    """A custom field.
    """


@crom.adapter
@crom.target(interfaces.IWidget)
@crom.sources(MyField, interfaces.IFormCanvas, Interface)
class MyWidget(Widget):
    """Custom widget to render my field.
    """


# TODO we shall provide a simpler decorator in the future
@crom.adapter
@crom.target(ITemplate)
@crom.sources(MyWidget, Interface)
def mywidget_template(view, request):
    return TALTemplate(filename=os.path.join(os.path.dirname(__file__),
                                    "widgettemplate_templates",
                                    "mywidget.pt", ))
