.. Moderation documentation master file, created by
   sphinx-quickstart on Wed Feb  5 20:53:13 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Moderation's documentation!
======================================

Contents:

.. toctree::
   :maxdepth: 2


Moderation
==========

**moderation** is a pluggable Django's application for moderating content. This
application uses the *registration pattern* for registering those models that
are going to be moderated.

When a new record for a registered model is created, *moderation* marks it to
be moderated. Administrator user can **approve** or **reject** each record.
*moderation* also allows us to flag records. By default, each record starts in
*pending* status.

*moderation* also provides specific models for working with banned words and
users.

This application can be integrated with **Scarlet** easily. Actually, the
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

You need to *register* each model you want to moderate. For example, the following code
register the existing *Comment* model::

    from moderation import moderator

    moderator.register(Comment)

Each model must be registered once. It's a good idea to register each model in
your *models.py* file.

Once your model is registered, you can work with each instance of this model. The
next code shows you how to approve a comment::

    comment = Comment(content='This is the comment')
    comment.save()

    comment.approve()

Previous stored records
------------------------

If you have records stored in DB before registering your model, you can create
moderation records for them in the moderation queue. You only need to execute
the following command::

    [comment.moderation_object_name for comment in Comment.objects.all()]

Actions
=======

The *moderation* applications allows you to execute the following main actions:

* **approve**: Approve the content
* **reject**: Reject the content
* **flag**: Flag for moderation
* **unflag**: Delete previous flag

Other methods provided by *moderation** are these:

* **is_approved**: Returns **True** if record has been approved.
* **is_rejected**: Returns **True** if record has been rejected.
* **is_pending**: Returns **True** if record is pending of moderation.
* **get_moderation_status_display**: Gets the current *status* of the record.

Also, each moderated record has a property called *moderation_status*, which has
three possible values:

* Approved
* Pending
* Rejected

Actions for users and words
----------------------------

The following actions are available for working with users moderation:

* **ban**: Bans a given user (using an username)
* **unban** Unbans a given user
* **flag**: Flags a given user
* **unflag**: Unflags a given user
* **get_flagged_users**: Gets a list of flagged users
* **get_banned_users**: Gets a list of banned users

The following actions are available for working with banned words:

* **get_banned_words**: Gets a list of banned words.
* **set_banned_words**: Sets a list of banned words.
* **passes_moderation**: Returns *True* if content passes moderation.
* **is_banned_word**: Returns *True* if given word is banned.

Available commands
==================

The *moderation* application offers you different commands to be invoked from
command line or from *cron* command:

* *delete_rejected_content*: Deletes those objects marked as *rejected* in the moderation queue.
* *create_default_banned_words*: Creates a set of default banned words.
* *approve_content*: Approves all pending content in moderation queue.

Tests
=====

Run the unit tests for *moderation* executing the following command::

    $ python run_tests.py


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

