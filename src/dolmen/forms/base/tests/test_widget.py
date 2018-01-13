# -*- coding: utf-8 -*-

import pytest
import crom
import widget_fixture
from dolmen.forms.base import interfaces
from dolmen.forms.base import Form
from dolmen.forms.base.widgets import Widget
from cromlech.browser.testing import TestRequest as Request
from zope.interface.interfaces import ComponentLookupError


def test_widget_render():
    crom.configure(widget_fixture)
        
    field = widget_fixture.MyField("Cool Test")
    request = Request()
    form = Form(None, request)
        
    widget = interfaces.IWidget(field, form, request)
    assert isinstance(widget, Widget)
    assert widget.component is field

    assert widget.render() == (
        "<p>Too complicated widget for Cool Test</p>")
    
    field2 = widget_fixture.AnotherField("Bad Test")
    widget = interfaces.IWidget(field2, form, request)
    assert isinstance(widget, widget_fixture.NoRenderWidget)
        
    with pytest.raises(ComponentLookupError):
        # No template or render method defined
        # Error !
        widget.render()

        
    field = widget_fixture.YetAnotherField("Cool Template Test")
    request = Request()
    form = Form(None, request)
        
    widget = interfaces.IWidget(field, form, request)
    assert widget.component is field
    
    assert widget.render() == (
        """<p>Nice template for Cool Template Test</p>
""")
