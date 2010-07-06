# -*- coding: utf-8 -*-

from zope import schema
from zope.interface import Interface
from zope.configuration.fields import GlobalObject


class IFieldUpdate(Interface):
    """Defines a field update adapter. A field update adapter is called
    when an object is updated. It adapts the field itself and the object
    on which it has been modified. It allows high pluggability in forms
    treatments.
    """
    field = schema.Object(
        required=True,
        title=u"The field that has been updated.",
        schema=schema.interfaces.IField)

    object = GlobalObject(
        required=True,
        title=u"The object concerned by the field update.")
