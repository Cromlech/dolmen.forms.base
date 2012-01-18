"""
We are going to define a custom widget here which define its rendering
HTML using a template associated with Grok.

Let's grok our example:

  >>> from dolmen.forms.base.testing import grok
  >>> grok('dolmen.forms.base.ftests.widgets.widgettemplate')

So now should be to lookup our widget:

  >>> field = MyField("Cool Template Test")
  >>> field
  <MyField Cool Template Test>

  >>> from cromlech.io.testing import TestRequest
  >>> request = TestRequest()

  >>> from dolmen.forms.base import Form
  >>> form = Form(None, request)

  >>> from zope import component
  >>> widget = component.getMultiAdapter(
  ...     (field, form, request), interfaces.IWidget)
  >>> widget
  <MyWidget Cool Template Test>

And we are able now to call its render method:

  >>> print widget.render()
  <p>Nice template for Cool Template Test</p>


"""
import os.path
from cromlech.browser import ITemplate
from dolmen.forms.base.fields import Field
from dolmen.forms.base.widgets import Widget
from dolmen.forms.base import interfaces
from dolmen.template import TALTemplate
from zope.interface import Interface
from grokcore import component as grok


class MyField(Field):
    """A custom field.
    """


class MyWidget(Widget):
    """Custom widget to render my field.
    """
    grok.adapts(MyField, interfaces.IFormCanvas, Interface)


# TODO we shall provide a simpler decorator in the future
@grok.adapter(MyWidget, Interface)
@grok.implementer(ITemplate)
def mywidget_template(view, request):
    return TALTemplate(filename=os.path.join(os.path.dirname(__file__),
                                    "widgettemplate_templates",
                                    "mywidget.pt", ))
