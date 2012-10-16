#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest
from zeam.form import ztk
from zope.testing import doctest
from zope.component import eventtesting
from zeam.form.ztk.testing import FunctionalLayer
from zope.app.wsgi.testlayer import BrowserLayer


class MyFunctionalLayer(BrowserLayer):

    def setUp(self):
        super(MyFunctionalLayer, self).setUp()
        eventtesting.setUp()


def test_suite():
    """Testing suite.
    """
    readme = doctest.DocFileSuite(
        'README.txt',
        optionflags=(doctest.ELLIPSIS + doctest.NORMALIZE_WHITESPACE))
    readme.layer = MyFunctionalLayer(ztk)
    suite = unittest.TestSuite()
    suite.addTest(readme)
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
