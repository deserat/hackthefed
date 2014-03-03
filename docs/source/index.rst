.. Moderation documentation master file, created by
   sphinx-quickstart on Wed Feb  5 20:53:13 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Moderation's documentation!
======================================

Contents:

.. toctree::
   :maxdepth: 2


Introduction
============

**moderation** is a pluggable Django's application for moderating content.

For moderating an object, you only need to make your model inherits from a
specific model implemented on *moderation* application. The *moderation* application
uses an *Abstract Base Class (ABC)*.

*moderation* also provides specific models for working with banned words and
users.

The application allows us to use two different approaches for moderation:

1. **Post-moderated**: Default behavior. The administrator (human) must check
moderation queue to *approve* or *reject* content.

2. **Pre-moderated**: The application will check if the content of each record
passes or not the moderation checking the *banned words*. If *content* passes
moderation then content will be *approved*, otherwise content will be *rejected*.

This application can be easily integrated with **Scarlet**. Actually, the
*cms_bundles.py* file allows you to build an administration interface displaying
a moderation queue.


Quick Start
===========

First, you should install this application as usual. Then, you'll need to add the
application to your *INSTALLED_APPS* variable in your *settings.py* file::


    INSTALLED_APPS = (
        ....
        'moderation',
    )

Make your models inherit from **ModeratedContent** model, for example::

    class Comment(ModeratedContent):
        username = models.TextField()
        content = models.TextField()

You can approve content invoking to *approve()* method as follows::

    comment = Comment(content='This is the content')
    comment.approve()

If you need to use the *pre-moderation* approach, you must set two different
properties (model class name and field with content to be moderated) in your
*settings.py* file::

    PRE_MODERATE_Comment = True
    PRE_MODERATE_Comment_content_field = 'content'

You can use a simple list (Python *set*) with all banned words, which will be
created when application starts. The variable resides on the
**moderation/__init__.py** file and it is called *banned_words**.

Actions
=======

The *moderation* applications allows you to execute the following main actions:

* **approve**: Approve the content
* **reject**: Reject the content
* **flag**: Flag content and users for moderation

Other methods provided by *moderation** are these:

Also, each moderated record has a property called *moderation_status*, which has
three possible values:

* Approved
* Pending
* Rejected

How to flag/unflag users
========================

If you need to flag/unflag a specific user, you can execute following methods::

  from moderation import flag_user, unflag_user

  flag_user('username 1')
  unflag_user('username 2')

Available commands
==================

The *moderation* application offers you different commands to be invoked from
command line or from *cron* command:

* *delete_rejected_content*: Deletes those objects of given models marked as *rejected* in the moderation queue.
* *approve_content*: Approves all pending content of given models in moderation queue.

Scarlet
========

You can use *moderation* application with *Scarlet CMS*. *moderation*
includes some *bundles* that you can use with your models. These *bundles* provide
two bulk actions: **approve** and **reject**.

If you want your models use *moderation* bundles, you'll need to write additional
wrapper *bundles* in your application. For example, using a *Comment*::

  class CommentModerationFilterBundle(ModerationFilterForm):
      class Meta:
          model = Comment


  class CommentModerationBundle(ModerationBundle):
      display_fields = ('name', 'created', 'public', 'post') + ModerationBundle.display_fields

      main = ModerationListView(
          display_fields=display_fields,
          filter_form=CommentModerationFilterBundle,
          model=Comment,
      )

      class Meta:
        model = Comment

The *display_fields* attribute indicates the fields you want to include in the
main list displayed by the *bundle*.

If you want to get a complete *bundle* for moderation, you can write some code
like the following one::

  class ModerationBundleBlog(ModerationMainBundle):
      dashboard = (
          ('banned_word', ),
          ('banned_user', ),
          ('flagged_user', ),
          ('post_moderation', 'Posts'),
          ('comment_moderation', 'Comments'),
      )

      post_moderation = PostModerationBundle.as_subbundle(name='post_moderation')
      comment_moderation = CommentModerationBundle.as_subbundle(name='comment_moderation')

  site.register('moderation', ModerationBundleBlog(name='moderation'), title='Moderation')

Basically, *moderation* application provides the following classes for writing your
own bundles:

* *ModerationFilterForm*
* *ModerationBundle*
* *ModerationBundleBlog*
* *ModerationMainBundle*

Tests
=====

Run the unit tests for *moderation* executing the following command::

    $ python run_tests.py


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

