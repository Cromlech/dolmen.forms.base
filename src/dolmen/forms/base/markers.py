# -*- coding: utf-8 -*-

from dolmen.forms.base.interfaces import IMarkersAPI
from dolmen.forms.base.interfaces import IModeMarker, ISuccessMarker
from zope.interface import implementer, moduleProvides


class Marker(object):
    """Marker object, designed to be used as singleton (like None,
    True, False).
    """

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name.lower()

    def __repr__(self):
        return '<Marker %s>' % (self.name.upper())


@implementer(IModeMarker)
class ModeMarker(Marker):
    """A Marker defining a form mode. It has a specific attribute,
    extractable, that defines if the mode allows the data extraction
    """

    def __init__(self, name, extractable=True):
        Marker.__init__(self, name)
        self.extractable = extractable


@implementer(ISuccessMarker)
class SuccessMarker(Marker):
    """A marker defining an action result. It can be True or False,
    meaning Success or Failure.
    """

    def __init__(self, name, success, url=None, code=None):
        Marker.__init__(self, name)
        self.success = success

        if url is not None and code is None:
            code = 302  # Default to a HTTPFound.

        self.code = code  # used to cook a response
        self.url = url  # used for a redirection info.

    def __nonzero__(self):
        return bool(self.success)


class HiddenMarker(ModeMarker):
    """A marker that hides a field.
    """
    pass


# Data extraction markers
DEFAULT = Marker('DEFAULT')
NO_VALUE = Marker('NO_VALUE')
NO_CHANGE = Marker('NO_CHANGE')

# Action result markers
SUCCESS = SuccessMarker('SUCCESS', True)
FAILURE = SuccessMarker('FAILURE', False)
NOTHING_DONE = SuccessMarker('NOTHING_DONE', True)

# Mode markers
DISPLAY = ModeMarker('DISPLAY', extractable=False)
INPUT = ModeMarker('INPUT')
HIDDEN = HiddenMarker('HIDDEN')


def getValue(object, attr, default_object):
    """Retrieve the attr value from object. If it's DEFAULT, try to
    look up it on the default_object.
    """
    value = getattr(object, attr, DEFAULT)
    if value is DEFAULT:
        value = getattr(default_object, attr)
    return value


moduleProvides(IMarkersAPI)
__all__ = list(IMarkersAPI)
