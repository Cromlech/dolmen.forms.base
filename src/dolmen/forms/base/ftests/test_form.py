# -*- coding: utf-8 -*-

import doctest
import unittest
import dolmen.forms.base
import webob.dec
import cromlech.webob.request
from pkg_resources import resource_listdir
from zope.component.testlayer import LayerBase



class WSGIApplication(object):

    def __init__(self, formname):
        self.formname = formname

    @webob.dec.wsgify(RequestClass=cromlech.webob.request.Request)
    def __call__(self, req):
        context = object()
        form = getMultiAdapter((context, req), Interface, self.formname)
        return form()


class BrowserLayer(LayerBase):

    def testSetUp(self):
        LayerBase.testSetUp(self)
        self.application = WSGIApplication

    def makeApplication(self, formname):
        return self.application(formname)


FunctionalLayer = BrowserLayer(dolmen.forms.base)


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
        test = doctest.DocTestSuite(dottedname, optionflags=optionflags)
        suite.addTest(test)
    return suite


def test_suite():
    suite = unittest.TestSuite()
    for name in ['forms', 'widgets']:
        suite.addTest(suiteFromPackage(name))
    return suite
