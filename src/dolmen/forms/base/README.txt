=================
dolmen.forms.base
=================

`dolmen.forms.base` is a package in charge of exposing all the
functionalities of `z3c.form` and `megrok.z3cform`, to allow an easy
import. This package, developed for the Dolmen project, makes it
easier to change the underlying form framework. In the long run,
`z3c.form` and `megrok.z3cform` might be replaced by `zeam.form`.


Field update
============

`dolmen.forms.base` also proposes the definition of a new component that
can be used to atomize the updating process of an object: `IFieldUpdate`.

To demonstrate this `IFieldUpdate`, we are going to implement a simple
usecase where we instanciate a content, change a value and notify the
`IFieldUpdate` components. For that, we'll use a basic logger object::

  >>> logger = []

We create our test model::

  >>> from zope.schema import TextLine
  >>> from zope.interface import Interface, implements
  
  >>> class IContent(Interface):
  ...    title = TextLine(title=u'a title')

  >>> class Item(object):
  ...    implements(IContent)

Once this is done, we can define two `IFieldUpdate` components. We
implement them as named adapters. We'll retrieve them thanks to a
"getAdapters" call::

  >>> from zope.component import adapter
  >>> from zope.interface import implementer
  >>> from dolmen.forms.base import IFieldUpdate

  >>> @implementer(IFieldUpdate)
  ... @adapter(TextLine, IContent)
  ... def updated_title(field, context):
  ...    if field.__name__ == u"title":
  ...       logger.append('Title updated on %r with `%s`' %
  ...                     (context, getattr(context, field.__name__)))

  >>> @implementer(IFieldUpdate)
  ... @adapter(TextLine, Interface)
  ... def updated_textfield(field, context):
  ...    logger.append('A text field has been updated')


The components need to be named since they are adapters: we don't want
them to override each other. For the example, we want them both. let's
register them::

  >>> from zope.component import provideAdapter
  >>> provideAdapter(updated_title, name="updatetitle")
  >>> provideAdapter(updated_textfield, name="updatetext")


Now, we develop the small scenarii : we instanciate a Content,
add a value for the 'title' attribute and call the adapters:: 

  >>> item = Item()
  >>> item.title = "Some value"

  >>> from zope.component import getAdapters
  >>> adapters = getAdapters((IContent['title'], item), IFieldUpdate)
  >>> for adapter in adapters:
  ...   # We run through the generator
  ...   pass

  >>> for line in logger: print line
  Title updated on <Item object at ...> with `Some value`
  A text field has been updated

It works.
