"""
We are going to define a simple form with an action.

Let's grok our example::

  >>> from dolmen.forms.base.testing import grok
  >>> grok('dolmen.forms.base.ftests.forms.simpleform')

We can now lookup our form by the name of its class::

  >>> from cromlech.browser.testing import TestRequest
  >>> request = TestRequest()

  >>> from zope.location import Location
  >>> context = Location()
  >>> from zope.interface import directlyProvides
  >>> from cromlech.browser.interfaces import IPublicationRoot
  >>> directlyProvides(context, IPublicationRoot)

  >>> from zope import component
  >>> form = component.getMultiAdapter(
  ...     (context, request), name='change')
  >>> form
  <dolmen.forms.base.ftests.forms.simpleform.Change object at ...>

  >>> len(form.fields)
  0
  >>> len(form.actions)
  1

And we can render it::

  >>> from cromlech.browser.testing import XMLDiff
  >>> response = form()
  >>> print XMLDiff(response.body, '''
  ... <html>
  ...   <head>
  ...   </head>
  ...   <body>
  ...     <form action="http://localhost/change"
  ...           enctype="multipart/form-data"
  ...           id="form"
  ...           method="post">
  ...       <h1>My form</h1>
  ...       <p>The description of my form</p>
  ...       <div class="actions">
  ...          <div class="action">
  ...             <input type="submit" id="form-action-change-me"
  ...                    name="form.action.change-me"
  ...                    value="Change Me"
  ...                    class="action" />
  ...          </div>
  ...       </div>
  ...     </form>
  ...   </body>
  ... </html>''')
  None


Integration tests
-----------------

Let's try to take a browser and submit that form::

  >>> app = makeApplication("change")
  >>> from infrae.testbrowser.browser import Browser
  >>> browser = Browser(app)
  >>> browser.options.handle_errors = False
  >>> browser.handleErrors = False

  >>> browser.open('http://localhost/change')
  200
  >>> form = browser.get_form(id='form')
  >>> action = form.get_control('form.action.change-me')
  >>> action.name, action.type
  ('form.action.change-me', 'submit')

  >>> action.click()
  200
  >>> 'I completely changed everything' in browser.contents
  True

"""

from cromlech.webob.response import Response
from dolmen.forms import base
from grokcore import component as grok
from zope.interface import Interface


class ChangeAction(base.Action):

    def __call__(self, submission):
        submission.status = u"I completely changed everything"


class Change(base.Form):
    grok.context(Interface)

    responseFactory = Response

    label = u"My form"
    description = u"The description of my form"
    actions = base.Actions(ChangeAction("Change Me"))
