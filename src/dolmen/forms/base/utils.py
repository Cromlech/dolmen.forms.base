# -*- coding: utf-8 -*-

import sys
import operator
from cromlech.events import Attributes, ObjectModifiedEvent
from dolmen.forms.base.actions import Actions
from dolmen.forms.base.datamanagers import ObjectDataManager
from dolmen.forms.base.fields import Fields
from dolmen.forms.base.interfaces import IDataManager
from dolmen.forms.base.markers import NO_VALUE, NO_CHANGE
from zope.event import notify


def set_fields_data(fields, content, data):
    """Applies the values to the fields, if a change has been made and
    if the field is present in the given fields manager. It returns a
    dictionnary describing the changes applied with the name of the field
    and the interface from where it's from.
    """
    changes = {}
    if not IDataManager.providedBy(content):
        content = ObjectDataManager(content)

    for identifier, value in data.items():
        field = fields.get(identifier, default=None)
        if field is None or value is NO_VALUE or value is NO_CHANGE:
            continue

        content.set(identifier, value)
        changes.setdefault(field._field.interface, []).append(identifier)

    return changes


def notify_changes(content, changes, event=ObjectModifiedEvent):
    """Builds a list of descriptions, made of Attributes objects, defining
    the changes made on the content and the related interface.
    """
    assert event is not None

    if changes:
        descriptions = []
        for interface, names in changes.items():
            descriptions.append(Attributes(interface, *names))
        notify(event(content, *descriptions))
        return descriptions
    return None


def apply_data_event(fields, content, data, event=ObjectModifiedEvent):
    """ Updates the object with the data and sends an IObjectModifiedEvent
    """
    changes = set_fields_data(fields, content, data)
    if changes:
        if IDataManager.providedBy(content):
            notify_changes(content.content, changes, event)
        else:
            notify_changes(content, changes, event)
    return changes


def extends(*forms, **opts):
    # Extend a class with parents components
    field_type = opts.get('fields', 'all')

    def extendComponent(field_type):
        factory = {'actions': Actions, 'fields': Fields}.get(field_type)
        if factory is None:
            raise ValueError(u"Invalid parameter fields to extends")
        frame = sys._getframe(2)
        f_locals = frame.f_locals
        components = f_locals.setdefault(field_type, factory())
        components.extend(*map(operator.attrgetter(field_type), forms))

    if field_type == 'all':
        extendComponent('actions')
        extendComponent('fields')
    else:
        extendComponent(field_type)
