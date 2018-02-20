from django.core.management.base import BaseCommand

from rest_mock_server import generator
from rest_mock_server import mock_server


class Command(BaseCommand):
    help = 'Starts mock server (generates file if necessary)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            dest='server_file',
            help='Express server file path'
        )

    def handle(self, *args, **options):
        server_file = options.get('server_file')

        if not server_file:
            generator.main()
            server_file = 'index.js'

        mock_server.main(server_file)
