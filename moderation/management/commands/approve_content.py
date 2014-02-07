import logging
from optparse import make_option

from fabric.colors import green

from django.core.management.base import BaseCommand

from moderation.models import ModeratedObject, MODERATION_STATUS_PENDING, MODERATION_STATUS_APPROVED


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Approve all pending content for moderation'

    option_list = BaseCommand.option_list + (
        make_option('--dry-run',
                    action='store_true',
                    dest='dry_run',
                    default=False,
                    help='Report what will be approved without actually doing it', ),
    )

    def handle(self, *args, **options):
        dry_run = options['dry_run']

        pending_objects = ModeratedObject.objects.filter(status=MODERATION_STATUS_PENDING)

        total_pending = pending_objects.count()

        if dry_run:
            output_msg = '{0} pending records are going to be approved'
        else:
            pending_objects.update(status=MODERATION_STATUS_APPROVED)
            output_msg = '{0} pending records has been approved'
            logger.info(output_msg.format(total_pending))
        print(green(output_msg.format(total_pending)))
