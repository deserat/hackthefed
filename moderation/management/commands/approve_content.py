import logging
from optparse import make_option


from django.core.management.base import BaseCommand, CommandError
from django.db.models.loading import get_model

from moderation.models import MODERATION_STATUS_PENDING, MODERATION_STATUS_APPROVED


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    args = '<app_name>.<model_name> <app_name>.<model_name> ... <app_name>.<model_name>'
    help = 'Approve pending content for records of given models'

    option_list = BaseCommand.option_list + (
        make_option('--dry-run',
                    action='store_true',
                    dest='dry_run',
                    default=False,
                    help='Report what will be approved without actually doing it', ),
    )

    def handle(self, *args, **options):
        if len(args) < 1:
            raise CommandError('Please, provide a model name')

        dry_run = options['dry_run']

        for arg in args:
            app_name = arg.split('.')[0]
            model_name = arg.split('.')[1]
            model = get_model(app_name, model_name)
            if model is None:
                raise CommandError('Cannot import given model: {0}'.format(arg))
            pending_records = model.objects.filter(m_status=MODERATION_STATUS_PENDING)
            if dry_run:
                logger.info('{0} are going to be approved for {1}'.format(pending_records.count(), arg))
            else:
                pending_records.update(m_status=MODERATION_STATUS_APPROVED)
                logger.info('{0} has been updated for {1}'.format(pending_records.count(), arg))
