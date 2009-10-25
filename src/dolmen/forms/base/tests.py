import unittest
from zope.testing import doctest


def test_suite():
    """Testing suite.
    """
    readme = doctest.DocFileSuite('README.txt',
        optionflags=(doctest.ELLIPSIS + doctest.NORMALIZE_WHITESPACE),
        )

    suite = unittest.TestSuite()
    suite.addTest(readme)
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
