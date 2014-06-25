#!/usr/bin/python
# -*- coding: utf-8 -*-

import grokcore.message
from grokcore.component import baseclass
from grokcore.layout.components import LayoutAware
from grokcore.site.util import getApplication
from grokcore.view.util import url

from zeam.form.base.errors import Errors, Error
from zeam.form.base.interfaces import ICollection
from zeam.form.layout import Form
from zeam.form.ztk.validation import InvariantsValidation
from zope.i18n.interfaces import IUserPreferredLanguages
from zope.schema import interfaces


class ApplicationForm(Form, LayoutAware):
    baseclass()

    dataValidators = [InvariantsValidation]

    def application_url(self, name=None, data={}):
        """Return the URL of the nearest enclosing `grok.Application`.
        """
        return url(request, getApplication(), name, data)

    
    def flash(self, message, type='message'):
        """Send a short message to the user.
        """
        grokcore.message.send(message, type=type, name='session')
    
    @property
    def i18nLanguage(self):
        prefs = IUserPreferredLanguages(self.request, None)
        if prefs is not None:
            languages = prefs.getPreferredLanguages()
            if languages:
                try:
                    return languages[0]
                except IndexError:
                    pass
        return None
