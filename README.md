# Moderation application for Social Tools project

This is an Django application for moderating polled content from social networks. Also, this application allows us to ban specific users.


## Dependencies

* [Scarlet CMS](https://github.com/ff0000/scarlet)


## Quick start

1. Add **moderation** to your *INSTALLED_APPS* settings like this:

        INSTALLED_APPS = (
            ....
            'moderation',
         )
2. Run **migrate** command to create *moderation* models. 