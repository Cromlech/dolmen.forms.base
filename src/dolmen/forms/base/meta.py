# -*- coding: utf-8 -*-

from .interfaces import IFormView
from grokker import grokker, directive
from crom import target, name, registry
from cromlech.browser import IView, IRequest, request, context
from zope.interface import Interface


@grokker
@directive(context)
@directive(request)
@directive(target)
@directive(name)
@directive(registry)
def form_component(scanner, pyname,
         obj, registry,
         target=IView, context=Interface, request=IRequest, name=None):

    if name is None:
        name = obj.__name__.lower()

    obj.__component_name__ = name

    assert target.isOrExtends(IView)

    def register():
        registry.register((context, request), target, name, obj)

    scanner.config.action(
        discriminator=('form', (context, request), target, name, registry),
        callable=register
        )
