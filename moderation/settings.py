from django.conf import settings


POST_MODEL = getattr(settings, 'SOCIAL_POST_MODEL', 'posts.Post')
