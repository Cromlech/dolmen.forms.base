# -*- coding: utf-8 -*-

import crom
import dolmen.forms.base
import pytest
import webob.dec

from crom import testing
from cromlech.browser.interfaces import IPublicationRoot
from cromlech.webob import Request
from zope.interface import Interface, directlyProvides
from zope.location import Location


def crom_setup():
    testing.setup()
    crom.configure(dolmen.forms.base)


def crom_teardown():
    testing.teardown()


class WSGIApplication(object):

    def __init__(self, formname):
        self.formname = formname

    @webob.dec.wsgify(RequestClass=Request)
    def __call__(self, req):
        context = Location()
        directlyProvides(context, IPublicationRoot)
        form = Interface(context, req, name=self.formname)
        return form()


@pytest.fixture(autouse=True, scope="module")
def crom_environ():
    crom_setup()
    yield
    crom_teardown()


@pytest.fixture(scope='session')
def wsgi_application(request):
    return WSGIApplication
