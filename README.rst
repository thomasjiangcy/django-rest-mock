Django REST Mock
================

Mock Express server generated based on your views, that can come in handy when developing REST APIs with Django.


Requirements
============
Requires Django 1.11 or later and Node.js.


Installation
============

Using pip::

    $ pip install django-rest-mock


Usage
=====

Generates an ExpressJS file::

    $ python manage.py genmockserver

Starts an ExpressJS server (it will generate an ExpressJS file if necessary)::

    $ python manage.py startmockserver [--file]

--file (Optional): Specifies ExpressJS file to be used


Example
=======

Let's say you have an app with the following `views.py`, you will need to include the following syntax in your docstrings::

    class SomeView(APIView):
        """
        URL: /some-view/
        """

        def get(self, request, *args, **kwargs):
            """
            ```
            {
                "data": "Hello, world!"
            }
            ```
            """
            pass

And then you run `python manage.py genmockserver`, you will get an `index.js` generated in your current directory
