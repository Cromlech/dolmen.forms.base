# -*- coding: utf-8 -*-

from zeam.form.base.markers import NO_VALUE, NO_CHANGE
from zeam.form.base.interfaces import IDataManager
from zeam.form.base.datamanager import ObjectDataManager
from zope.event import notify
from zope.lifecycleevent import Attributes, ObjectModifiedEvent


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
        changes.setdefault(field.interface, []).append(identifier)

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
