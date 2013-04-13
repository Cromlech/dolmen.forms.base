# -*- coding: utf-8 -*-

import crom
import doctest
import unittest
import dolmen.forms.base
from crom import testing


def setUp(test):
    testing.setup()
    crom.configure(dolmen.forms.base)


def tearDown(test):
    testing.teardown()
    

def test_suite():
    optionflags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
    globs = {}

    suite = unittest.TestSuite()
    for filename in ['components.txt', 'actions.txt', 'fields.txt',
                     'forms.txt', 'widgets.txt', 'isempty_typeerror.txt']:
        test = doctest.DocFileSuite(
            filename,
            setUp=setUp,
            tearDown=tearDown,
            optionflags=optionflags,
            globs=globs)
        suite.addTest(test)

    return suite
