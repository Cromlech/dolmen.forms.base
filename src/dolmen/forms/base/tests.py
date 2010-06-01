#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest
from zope.testing import doctest
from zeam.form.ztk.testing import FunctionalLayer


def test_suite():
    """Testing suite.
    """
    readme = doctest.DocFileSuite(
        'README.txt',              
        optionflags=(doctest.ELLIPSIS + doctest.NORMALIZE_WHITESPACE))
    readme.layer = FunctionalLayer
    suite = unittest.TestSuite()
    suite.addTest(readme)
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
