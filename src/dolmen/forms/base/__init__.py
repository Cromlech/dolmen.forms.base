# -*- coding: utf-8 -*-

from zope.i18nmessageid import MessageFactory
_ = MessageFactory('dolmen.forms.base')

# translations
from os.path import join, dirname

from cromlech.i18n.translations import register_translations_directory

TRANSLATIONS_PATH = join(dirname(__file__), "i18n")

def register_translations(*args):
    register_translations_directory(TRANSLATIONS_PATH, *args)


# Interfaces
from dolmen.forms.base import interfaces, markers, errors

# Exposing limited dolmen.forms API
from dolmen.forms.base.actions import *
from dolmen.forms.base.fields import *
from dolmen.forms.base.components import *
from dolmen.forms.base.markers import *
from dolmen.forms.base.widgets import *
from dolmen.forms.base.datamanagers import *
from dolmen.forms.base.interfaces import ActionError

# Exposing package API
from dolmen.forms.base.interfaces import IForm
from dolmen.forms.base.components import cloneFormData
from dolmen.forms.base.utils import (
    extends, set_fields_data, notify_changes, apply_data_event)
from dolmen.forms.base.meta import form_component

# All
from crom.directives import name
from cromlech.browser import request, context
