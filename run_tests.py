import os
import sys

from django.conf import settings


def setup_test_environment():
    """
    Specific settings for testing
    """
    MIDDLEWARES = (
        'django.middleware.common.CommonMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
    )
    apps = [
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.admin',
        'django.contrib.sites',
        'moderation',
        'moderation.tests',
    ]
    settings_dict = {
        'DATABASES': {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': 'test_moderation.db'
            }
        },
        'SITE_ID': 1,
        'MIDDLEWARE_CLASSES': MIDDLEWARES,
        'INSTALLED_APPS': apps,
        'STATIC_URL': '/static/',
        'ROOT_URLCONF': '',
        'USE_TZ': True,
        'PRE_MODERATE_Post': True,
        'PRE_MODERATE_Post_content_field': 'content'
    }
    settings.configure(**settings_dict)


def runtests(*test_args):
    """
    Build a test environment and a test_runner specifically for moderation testing
    """
    setup_test_environment()
    parent = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, parent)
    try:
        from django.test.simple import DjangoTestSuiteRunner

        def run_tests(test_args, verbosity, interactive):
            runner = DjangoTestSuiteRunner(
                verbosity=verbosity, interactive=interactive,
                failfast=True
            )
            return runner.run_tests(test_args)
    except ImportError:
        from django.test.simple import run_tests

    failures = run_tests(test_args, verbosity=1, interactive=True)
    sys.exit(failures)

if __name__ == "__main__":
    runtests('moderation')
