from django.core.management.base import BaseCommand

from rest_mock_server.builder import build


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

        if server_file is None:
            express = build()
            server_file = 'index.js'
        express.generate(file_path=server_file)
        express.start_server(file_path=server_file)
