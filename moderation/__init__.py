from django.db.models import signals
from django.contrib.contenttypes.models import ContentType

from .models import ModeratedObject
from .models import MODERATION_STATUS_APPROVED, MODERATION_STATUS_REJECTED, MODERATION_STATUS_PENDING


class ModerationRegistrationException(Exception):
    pass


class Moderator(object):
    def __init__(self):
        self._registry = {}

    def register(self, model):
        if model in self._registry.keys():
            raise ModerationRegistrationException("{0} has been already register".format(model))

        signals.post_save.connect(self._save_handler, sender=model)
        signals.pre_delete.connect(self._delete_handler, sender=model)

        self._add_fields(model)

        self._registry[model] = model

    def _add_fields(self, cls):

        def _get_moderation_object(self):
            """Simple accessor for moderated_object that caches the object"""
            if not hasattr(self, '_moderation_object_name'):
                self._moderation_object_name = ModeratedObject.objects.get_for_instance(self)
            return self._moderation_object_name

        def _get_moderation_status(self):
            """Simple accessor to moderation status"""
            if not hasattr(self, '_status'):
                return getattr(self, 'moderation_object_name').status
            return self._status

        def approve(self, reason=''):
            getattr(self, 'moderation_object_name').approve(reason)

        def reject(self, reason=''):
            getattr(self, 'moderation_object_name').reject(reason)

        def is_approved(self):
            return self.moderation_status == MODERATION_STATUS_APPROVED

        def is_rejected(self):
            return self.moderation_status == MODERATION_STATUS_REJECTED

        def is_pending(self):
            return self.moderation_status == MODERATION_STATUS_PENDING

        # Adding methods
        cls.add_to_class('moderation_object_name', property(_get_moderation_object))
        cls.add_to_class('moderation_status', property(_get_moderation_status))
        cls.add_to_class('approve', approve)
        cls.add_to_class('reject', reject)
        cls.add_to_class('is_approved', is_approved)
        cls.add_to_class('is_rejected', is_rejected)
        cls.add_to_class('is_pending', is_pending)

    def _save_handler(self, sender, instance, **kwargs):
        if kwargs.get('created', None):
            mo = ModeratedObject(content_object=instance)
            mo.save()

    def _delete_handler(self, sender, instance, **kwargs):
        try:
            ct = ContentType.objects.get_for_model(sender)
            mo = ModeratedObject.objects.get(content_type=ct, object_pk=instance.pk)
            mo.delete()
        except ModeratedObject.DoesNotExist:
            raise ModerationRegistrationException("object {0) for sender {1} doesn't exist".format(instance.id, sender))


moderator = Moderator()
