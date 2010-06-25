#!/usr/bin/python
# -*- coding: utf-8 -*-

from grokcore.component import baseclass
from megrok.layout.components import UtilityView
from zeam.form.base.errors import Errors, Error
from zeam.form.base.interfaces import ICollection
from zeam.form.base.markers import NOT_EXTRACTED
from zeam.form.base.widgets import getWidgetExtractor
from zeam.form.layout import Form
from zeam.form.ztk.validation import InvariantsValidation
from zope.i18n.interfaces import IUserPreferredLanguages


class ApplicationForm(Form, UtilityView):
    baseclass()

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

    @property
    def formError(self):
        error = self.errors.get(self.prefix, None)
        if error is None or ICollection.providedBy(error):
            return error
        return [error]

    def extractData(self, fields=None):
        if fields is None:
            fields = self.fields

        if self._FormData__extracted is not NOT_EXTRACTED:
            return (self._FormData__extracted, self.errors)
        self._FormData__extracted = data = dict()

        for field in fields:
            # Global extraction and data dict creation
            extractor = getWidgetExtractor(field, self, self.request)
            value, error = extractor.extract()
            if error is None:
                error = field.validate(value, self.context)

            if error is not None:
                self.errors.append(Error(error, field.identifier))
            data[field.identifier] =  value

        # Invariants validation
        invalids = InvariantsValidation(fields).validate(data)
        if len(invalids):
            self.errors.append(Errors(
                *[Error(invalid.message) for invalid in invalids],
                identifier=self.prefix))

        if len(self.errors):
            return (data, self.errors)
        return (data, None)
