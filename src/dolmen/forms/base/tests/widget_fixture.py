# -*- coding: utf-8 -*-

import crom
import os.path

from cromlech.browser import ITemplate
from dolmen.forms.base import Field
from dolmen.forms.base import interfaces
from dolmen.forms.base.widgets import Widget
from dolmen.template import TALTemplate
from zope.interface import Interface


class MyField(Field):
    pass


@crom.adapter
@crom.target(interfaces.IWidget)
@crom.sources(MyField, interfaces.IFormCanvas, Interface)
class MyWidget(Widget):

    def render(self):
        return u"<p>Too complicated widget for %s</p>" % (
            self.component.title)


class AnotherField(Field):
    pass


class YetAnotherField(Field):
    pass


@crom.adapter
@crom.target(interfaces.IWidget)
@crom.sources(AnotherField, interfaces.IFormCanvas, Interface)
class NoRenderWidget(Widget):
    pass


@crom.adapter
@crom.target(interfaces.IWidget)
@crom.sources(YetAnotherField, interfaces.IFormCanvas, Interface)
class TemplateWidget(Widget):
    pass


@crom.adapter
@crom.target(ITemplate)
@crom.sources(TemplateWidget, Interface)
def mywidget_template(view, request):
    return TALTemplate(filename=os.path.join(os.path.dirname(__file__),
                                    "widgettemplate_templates",
                                    "mywidget.pt", ))
