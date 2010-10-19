#!/usr/bin/python
# -*- coding: utf-8 -*-

from grokcore.component import baseclass
from megrok.layout.components import UtilityView
from zeam.form.base.errors import Errors, Error
from zeam.form.base.interfaces import ICollection
from zeam.form.layout import Form
from zeam.form.ztk.validation import InvariantsValidation
from zope.i18n.interfaces import IUserPreferredLanguages
from zope.schema import interfaces




class ApplicationForm(Form, UtilityView):
    baseclass()

    dataValidators = [InvariantsValidation]

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
