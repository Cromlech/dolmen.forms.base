# -*- coding: utf-8 -*-

from zope.configuration.config import ConfigurationMachine
from grokcore.component import zcml
from dolmen.view.testing import grok as view_grok


def grok(module_name):
    config = ConfigurationMachine()
    zcml.do_grok('grokcore.component.meta', config)
    zcml.do_grok('grokcore.security.meta', config)
    zcml.do_grok('dolmen.view.meta', config)
    zcml.do_grok('dolmen.view.security', config)
    zcml.do_grok('cromlech.webob', config)
    zcml.do_grok("dolmen.forms.base.form_templates", config)
    zcml.do_grok("dolmen.forms.base.widgets", config)
    zcml.do_grok(module_name, config)
    config.execute_actions()
