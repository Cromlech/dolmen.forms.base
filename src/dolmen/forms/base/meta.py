# -*- coding: utf-8 -*-

from grokker import grokker, directive
from crom import target, name, registry
from cromlech.browser import IForm, IRequest, request, context
from zope.interface import Interface


@grokker
@directive(context)
@directive(request)
@directive(target)
@directive(name)
@directive(registry)
def form_component(scanner, pyname,
         obj, registry,
         target=IForm, context=Interface, request=IRequest, name=None):

    if name is None:
        name = obj.__name__.lower()

    obj.__component_name__ = name

    assert target.isOrExtends(IForm)

    def register():
        registry.register((context, request), target, name, obj)
        
    scanner.config.action(
        discriminator=('form', (context, request), target, name, registry),
        callable=register
        )
