import logging
from optparse import make_option

from fabric.colors import green, red

from django.core.management.base import BaseCommand

from moderation.models import ModeratedObject, MODERATION_STATUS_REJECTED


logger = logging.getLogger(__name__)


class Command(BaseCommand):
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
        output_msg = "{0} content objects has been deleted"
        dry_run = options['dry_run']
        no_confirmation = options['no_confirmation']

        if not dry_run and not no_confirmation:
            input_msg = 'Content is going to be deleted. Continue [Y/n]? '
            input_msg = raw_input(input_msg)
            if input_msg not in ('Y', 'n'):
                exit(red("Please, choose 'Y' or 'n'"))
            if input_msg == 'n':
                exit(red('Command aborted'))

        deleted_objects = 0

        rejected_objects = ModeratedObject.objects.filter(status=MODERATION_STATUS_REJECTED)
        for rejected in rejected_objects:
            content_object = rejected.content_object
            if not dry_run:
                #content_object.delete()
                logger.info(u'content_object {0} has been deleted'.format(content_object))
            deleted_objects += 1

        if dry_run:
            output_msg = "{0} content objects are going to be deleted"
        print(green(output_msg.format(deleted_objects)))
