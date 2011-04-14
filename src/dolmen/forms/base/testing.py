# -*- coding: utf-8 -*-

from zope.configuration.config import ConfigurationMachine
from grokcore.component import zcml


def grok(module_name):
    config = ConfigurationMachine()
    zcml.do_grok("dolmen.forms.base.form_templates", config)
    zcml.do_grok("dolmen.forms.base.widgets", config)
    zcml.do_grok(module_name, config)
    config.execute_actions()
