from django.db.models import get_model
from django.core.exceptions import ImproperlyConfigured

from .. import settings


def get_post_model():
    try:
        app_label, model_name = settings.POST_MODEL.rsplit('.', 1)
    except ValueError:
        raise ImproperlyConfigured("POST_MODEL must be of the form 'app_label.model_name'")
    post_model = get_model(app_label, model_name)
    if post_model is None:
        raise ImproperlyConfigured("POST_MODEL refers to model '%s' that has not been installed" % settings.POST_MODEL)
    return post_model
