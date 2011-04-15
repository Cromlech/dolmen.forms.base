# -*- coding: utf-8 -*-

import doctest
import unittest
from grokcore.component import testing

def setUp(test):
    testing.grok('dolmen.forms.base')


def test_suite():
    optionflags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
    globs= {}

    suite = unittest.TestSuite()
    for filename in ['components.txt', 'actions.txt', 'fields.txt',
                     'forms.txt', 'widgets.txt', '../README.txt']:
        test = doctest.DocFileSuite(
            filename,
            setUp=setUp,
            optionflags=optionflags,
            globs=globs)
        suite.addTest(test)

    return suite
