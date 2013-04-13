# -*- coding: utf-8 -*-

import sys

from dolmen.forms.base import interfaces, markers, errors
from dolmen.collection import Component, Collection
from zope.interface import implementer, alsoProvides, moduleProvides


@implementer(interfaces.IAction)
class Action(Component):
    """A form action.
    """
    prefix = 'action'
    # By default an action is always in input mode (there is not much
    # sense otherwise).
    mode = 'input'
    description = None
    accesskey = None
    postOnly = markers.DEFAULT

    def available(self, form):
        return True

    def validate(self, form):
        return True

    def __call__(self, submission):
        raise NotImplementedError


@implementer(interfaces.IActions)
class Actions(Collection):
    """A list of form action.
    """
    type = interfaces.IAction

    def process(self, form, request):
        for action in self:
            extractor = interfaces.IWidgetExtractor(action, form, request)

            value, error = extractor.extract()
            if value is not markers.NO_VALUE:
                isPostOnly = markers.getValue(action, 'postOnly', form)
                if isPostOnly and request.method != 'POST':
                    form.errors.append(
                        errors.Error('This form was not submitted properly',
                                     form.prefix))
                    return None, markers.FAILURE
                try:
                    if action.validate(form):
                        return action, action(form)
                except interfaces.ActionError, error:
                    form.errors.append(errors.Error(
                        error.args[0], form.prefix))
                    return action, markers.FAILURE
        return None, markers.NOTHING_DONE


# Convience API, decorator to add action

class DecoratedAction(Action):
    """An action created by a decorator.
    """

    def __init__(self, title, callback,
                 identifier=None, description=None, accesskey=None,
                 validator=None, available=None):
        super(Action, self).__init__(title, identifier)
        self._callback = callback
        self._validator = validator
        self._available = available
        self.accesskey = accesskey
        self.description = description

    def validate(self, form):
        if self._validator is not None:
            return self._validator(form)
        return True

    def available(self, form):
        if self._available is not None:
            return self._available(form)
        return True

    def __call__(self, form, *args, **kwargs):
        assert self._callback is not None
        return self._callback(form, *args, **kwargs)


# More convienent, extract the data before calling the action

class ExtractedDecoratedAction(DecoratedAction):

    def __call__(self, form):
        data, errors = form.extractData()
        if errors:
            return markers.FAILURE
        # We directly give data.
        return super(ExtractedDecoratedAction, self).__call__(form, data)


def action(title, identifier=None, description=None, accesskey=None,
           validator=None, available=None, implements=None,
           factory=DecoratedAction, category='actions'):
    def createAction(callback):
        new_action = factory(
            title, callback, identifier, description, accesskey,
            validator, available)
        if implements is not None:
            alsoProvides(new_action, implements)

        # Magic to access the parent action list to add the action
        frame = sys._getframe(1)
        f_locals = frame.f_locals
        actions = f_locals.setdefault(category, Actions())

        actions.append(new_action)

        # We keep the same callback, so we can do super in
        # subclass. Registering it is enough, we do not need something
        # else.
        return callback
    return createAction


moduleProvides(interfaces.IActionsAPI)
__all__ = list(interfaces.IActionsAPI)
