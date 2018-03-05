'''
Extracts all endpoints and their corresponding view docstrings to retrieve
the expected JSON responses.

Example
=======

Given a view::

    class SomeView(APIView):
        """
        URL: /api/some/view/__key?param1[int]&param2[str]
        """

        def get(self, request, *args, **kwargs):
            """
            ```
            {
                "__key": "<id:int>",
                "__key_position": "url",
                "__mockcount": 5,
                "data": "Hello, world",
                "id": "<sha256::10>"
            }
            ```
            """
            pass

The Extractor can parse the docstrings of the view class and the request handler method.
The query parameters and expected type should be parsed from the view class docstring.

'''

import re

import django
from django.conf import settings
from django.core.exceptions import ViewDoesNotExist


if django.VERSION >= (2, 0):
    from django.urls import URLPattern, URLResolver

    class RegexURLPattern:
        pass

    class RegexURLResolver:
        pass

    class LocaleRegexURLResolver:
        pass

    def describe_pattern(p):
        return str(p.pattern)
else:
    try:
        from django.urls import RegexURLPattern, RegexURLResolver, LocaleRegexURLResolver
    except ImportError:
        from django.core.urlresolvers import RegexURLPattern, RegexURLResolver, LocaleRegexURLResolver

    class URLPattern:
        pass

    class URLResolver:
        pass

    def describe_pattern(p):
        return p.regex.pattern


METHODS = ['get', 'post', 'put', 'patch', 'delete']


class Extractor:

    def __init__(self):
        self._urlconf = __import__(getattr(settings, 'ROOT_URLCONF'))
        self.url_details = []
        self._load_url_details()  # Load all urlpatterns & corresponding view classes/functions

    def _get_view_details(self, urlpatterns, parent=''):
        """Recursive function to extract all url details"""
        for pattern in urlpatterns:
            if isinstance(pattern, (URLPattern, RegexURLPattern)):
                try:
                    d = describe_pattern(pattern)
                    docstr = pattern.callback.__doc__
                    method = None
                    expected_json_response = ''

                    expected_url = ''
                    if docstr:
                        # Get expected URL
                        u = re.findall(r'URL: (.*)', docstr, flags=re.DOTALL)
                        if u:
                            expected_url = u[0]

                    # Get all possible methods
                    if 'view_class' not in dir(pattern.callback):
                        continue

                    possible_methods = [m for m in dir(pattern.callback.view_class) if m in METHODS]

                    for method in possible_methods:
                        view_method_docstr = getattr(pattern.callback.view_class, method).__doc__
                        if view_method_docstr:
                            # Check if method is modifier
                            if method in ['put', 'patch', 'delete']:
                                self.url_details.append({
                                    'url': expected_url,
                                    'method': method
                                })
                                continue
                            # Extract request method and JSON response from docstring of request method
                            j = re.findall(r'```(.*)```', view_method_docstr, flags=re.DOTALL)
                            if j is not None:
                                for match in j:
                                    expected_json_response = match.strip()
                                    # Only add the details if all 3 values are filled
                                    if method is not None and expected_json_response and expected_url:
                                        self.url_details.append({
                                            'url': expected_url,
                                            'method': method,
                                            'response': expected_json_response
                                        })
                                        continue

                except ViewDoesNotExist:
                    pass

            elif isinstance(pattern, (URLResolver, RegexURLResolver)):
                try:
                    patterns = pattern.url_patterns
                except ImportError:
                    continue

                d = describe_pattern(pattern)
                current_full_url = parent + d
                self._get_view_details(patterns, current_full_url)

    def _load_url_details(self):
        root_urls = self._urlconf.urls.urlpatterns
        self._get_view_details(root_urls)
