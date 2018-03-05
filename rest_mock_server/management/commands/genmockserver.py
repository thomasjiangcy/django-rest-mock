from django.core.management.base import BaseCommand

from rest_mock_server.builder import build


class Command(BaseCommand):
    help = 'Generates an Express server file for mocking endpoint responses'

    def add_arguments(self, parser):
        parser.add_argument(
            '--output',
            dest='output_file',
            help='Custom output file name'
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
        output = options.get('output_file')
        if output is None:
            output = 'index.js'
        port = options.get('port')
        if port is None:
            port = 8000
        fixtures = options.get('fixtures')
        if fixtures is not None:
            fixtures = fixtures.split(',')
        express = build(port, fixtures)
        express.generate(file_path=output)
