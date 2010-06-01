#!/usr/bin/python
# -*- coding: utf-8 -*-

from grokcore.component import baseclass
from megrok.layout.components import UtilityView
from zeam.form.layout import Form


class ApplicationForm(Form, UtilityView):
    baseclass()
