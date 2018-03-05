from pathlib import Path

from django.core.management.base import BaseCommand

from rest_mock_server.builder import build
from rest_mock_server.core.express import ExpressServer


class Command(BaseCommand):
    help = 'Starts mock server (generates file if necessary)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            dest='server_file',
            help='Express server file path'
        )
        parser.add_argument(
            '--port',
            dest='port',
            help='Custom port to be exposed'
        )
        parser.add_argument(
            '--fixtures',
            dest='fixtures',
            help='Directory where fixtures can be extracted from'
        )

    def handle(self, *args, **options):
        server_file = options.get('server_file')
        if server_file is None:
            server_file = 'index.js'
            port = options.get('port')
            if port is None:
                port = 8000
            fixtures = options.get('fixtures')
            if fixtures is not None:
                fixtures = fixtures.split(',')
            express = build(port, fixtures)
            express.generate(file_path=server_file)
            express.start_server(file_path=server_file)
        else:
            express = ExpressServer()
            express.start_server(file_path=server_file)
