# -*- coding: utf-8 -*-

import crom
import extends_fixture
from cromlech.browser import IView
from cromlech.browser.testing import TestRequest as Request


def test_extends():

    crom.configure(extends_fixture)

    request = Request()
    context = object()
    form = IView(context, request, name='othernameform')

    assert isinstance(form, extends_fixture.OtherNameForm)
    assert len(form.fields) == 1
    assert list(form.fields)[0].title == "Name"
    
    assert len(form.actions) == 2
    assert [a.title for a in form.actions] == ['Register', 'Kill']
