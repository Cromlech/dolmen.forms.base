"""
We are going to define a simple form with an action.

Let's configure our example::

  >>> from . import simpleform as module
  >>> from crom import configure
  >>> configure(module)

We can now lookup our form by the name of its class::

  >>> from cromlech.browser.testing import TestRequest
  >>> request = TestRequest()

  >>> from zope.location import Location
  >>> context = Location()
  >>> from zope.interface import directlyProvides
  >>> from cromlech.browser.interfaces import IPublicationRoot
  >>> directlyProvides(context, IPublicationRoot)

  >>> from cromlech.browser import IForm
  >>> form = IForm(context, request, name='change')
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
  ...     <form action=""
  ...           id="form"
  ...           method="post"
  ...           enctype="multipart/form-data">
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


class ChangeAction(base.Action):

    def __call__(self, submission):
        submission.status = u"I completely changed everything"


@base.form_component
class Change(base.Form):

    responseFactory = Response

    label = u"My form"
    description = u"The description of my form"
    actions = base.Actions(ChangeAction("Change Me"))
