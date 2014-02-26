import logging
from optparse import make_option

from django.core.management.base import BaseCommand, CommandError
from django.db.models.loading import get_model

from moderation.models import MODERATION_STATUS_REJECTED


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    args = '<app_name>.<model_name> <app_name>.<model_name> ... <app_name>.<model_name>'
    help = 'Delete original content which has been rejected by moderation'

    option_list = BaseCommand.option_list + (
        make_option('--dry-run',
                    action='store_true',
                    dest='dry_run',
                    default=False,
                    help='Report what will be deleted without actually doing it', ),
        make_option('--no-confirmation',
                    action='store_true',
                    dest='no_confirmation',
                    default=False,
                    help='Delete content without asking for confirmation')
    )

    def handle(self, *args, **options):
        if len(args) < 1:
            raise CommandError('Please, provide a model name')

        dry_run = options['dry_run']
        no_confirmation = options['no_confirmation']

        if not dry_run and not no_confirmation:
            input_msg = 'Content is going to be deleted. Continue [Y/n]? '
            input_msg = raw_input(input_msg)
            if input_msg not in ('Y', 'n'):
                raise CommandError("Please, choose 'Y' or 'n'")
            if input_msg == 'n':
                raise CommandError('Command aborted')

        for arg in args:
            app_name = arg.split('.')[0]
            model_name = arg.split('.')[1]
            model = get_model(app_name, model_name)
            if model is None:
                raise CommandError('Cannot import given model: {0}'.format(arg))
            rejected_records = model.objects.filter(m_status=MODERATION_STATUS_REJECTED)
            if dry_run:
                logger.info('{0} are going to be deleted for {1}'.format(rejected_records.count(), arg))
            else:
                rejected_records.using('default').delete()
                logger.info('{0} has been deleted for {1}'.format(rejected_records.count(), arg))
