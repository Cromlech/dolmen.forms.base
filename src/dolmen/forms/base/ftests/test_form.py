
import doctest
import unittest
from pkg_resources import resource_listdir


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
