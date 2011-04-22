# -*- coding: utf-8 -*-

from zope.configuration.config import ConfigurationMachine
from grokcore.component import zcml


def grok(module_name):
    config = ConfigurationMachine()
    zcml.do_grok('grokcore.component.meta', config)
    zcml.do_grok('dolmen.view.meta', config)
    zcml.do_grok("dolmen.location", config)
    zcml.do_grok("dolmen.forms.base", config)
    zcml.do_grok(module_name, config)
    config.execute_actions()
