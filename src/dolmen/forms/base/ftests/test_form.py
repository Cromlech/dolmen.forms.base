# -*- coding: utf-8 -*-

import crom
import cromlech.webob.request
import doctest
import dolmen.forms.base
import unittest
import webob.dec

from crom import testing
from cromlech.browser.interfaces import IPublicationRoot
from pkg_resources import resource_listdir
from zope.interface import Interface, directlyProvides
from zope.location import Location


def setUp(test):
    testing.setup()
    crom.configure(dolmen.forms.base)


def tearDown(test):
    testing.teardown()


class WSGIApplication(object):

    def __init__(self, formname):
        self.formname = formname

    @webob.dec.wsgify(RequestClass=cromlech.webob.request.Request)
    def __call__(self, req):
        context = Location()
        directlyProvides(context, IPublicationRoot)
        form = Interface(context, req, name=self.formname)
        return form()


def suiteFromPackage(name):
    optionflags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
    files = resource_listdir(__name__, name)
    suite = unittest.TestSuite()
    for filename in files:
        if not filename.endswith('.py'):
            continue
        if filename.endswith('_fixture.py'):
            continue
        if filename == '__init__.py':
            continue

        dottedname = 'dolmen.forms.base.ftests.%s.%s' % (name, filename[:-3])
        test = doctest.DocTestSuite(dottedname,
            optionflags=optionflags,
            setUp=setUp,
            tearDown=tearDown,
            extraglobs=dict(makeApplication=WSGIApplication))
        suite.addTest(test)
    return suite


def test_suite():
    suite = unittest.TestSuite()
    for name in ['forms', 'widgets']:
        suite.addTest(suiteFromPackage(name))
    return suite
