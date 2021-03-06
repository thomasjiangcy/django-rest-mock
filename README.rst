Django REST Mock
================

Mock Express server generated based on your views, that can come in handy when developing REST APIs with Django.

Typically, the Django developer can first create all the views with docstrings and pass on the project to the front-end developer who can work with the mock server which outputs what is already expected. This allows frontend devs to work with a stable and predictable API.


Requirements
============
Requires Django 1.11 or later and Node.js.

Note that this requires views to be Class-based Views.


Installation
============

Using pip::

    $ pip install django-rest-mock


Then include ``rest_mock_server`` into your ``INSTALLED_APPS``::

    INSTALLED_APPS = (
        ...
        'rest_mock_server',
        ...
    )


Usage
=====

After including docstrings for the views you wish to generate endpoints for, you may run the following commands

Generates an ExpressJS file::

    $ python manage.py genmockserver

    --output: Custom output path and name, by default it will output 'index.js' in the current directory
    --port: The port that's exposed by the ExpressJS server
    --fixtures: Specify fixture paths - note that they must be the direct parent of where the .json fixtures are located
    --no-minify: Flag to indicate no minification of output file, doesn't take any arguments

Starts an ExpressJS server (it will generate an ExpressJS file if necessary)::

    $ python manage.py startmockserver

    --file: Specify the ExpressJS file to use
    --port: Specify the port
    --fixtures: Specify fixture paths - note that they must be the direct parent of where the .json fixtures are located
    --no-minify: Flag to indicate no minification of output file, doesn't take any arguments

Steps to use:

1. Create your docstrings in your views (more details below)
2. Add views to urls (the actual url doesn't matter, what matters is that the view class is added to Django's URL conf so that it can be detected)
3. Run either ``genmockserver`` or ``startmockserver``

Syntax
======

1. Basic endpoint::

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


2. RESTful endpoint with list & instances::

    class ResourceListView(ListCreateAPIView):
        """
        URL: /resource/__key
        """

        def post(self, request, *args, **kwargs):
            """
            ```
            {
                "__options": {
                        "excludeKey": true
                },
            }
            ```
            """
            pass

    class ResourceView(RetrieveUpdateDestroyAPIView):
        """
        URL: /resource/__key
        """

        def get(self, request, *args, **kwargs):
            """
            ```
            {
                "__key": "<id:int>",
                "__key_position": "url",
                "__mockcount": 5,
                "__options": {
                    "modifiers": ["patch", "put", "delete"],
                    "excludeKey": false
                },
                "id": "<int>",
                "name": "<name>",
                "complexStructure": [
                    {
                        "link": "<int::10>",
                        "url": "<uri>",
                        "related_user": {
                            "id": "<int:1:5>",
                            "hash": "<sha256>"
                        }
                    }
                ]
            }
            ```
            """
            pass
        
        def put(self, request, *args, **kwargs):
            """We won't need to specify any response here"""
            pass
        
        def patch(self, request, *args, **kwargs):
            """We won't need to specify any response here"""
            pass
        
        def delete(self, request, *args, **kwargs):
            """We won't need to specify any response here"""
            pass

When creating fixtures for a resource (CRUD), you only need to work with the instance endpoint, in ``Django REST framework``, it's typically the endpoint that requires a unique ID - e.g. ``/some-resource/<pk>``

You need to specify ``__key`` in the url and also in the response as above. The value follows the following syntax ``<name-of-unique-key:data-type>``.
You will also need to specify the position of the key: either ``url`` or ``query``. If it is ``url``, it exists as a URL param, and ``query`` means that the key should be found in query string.

* ``__mockcount``: (defaults to 1) Represents the number of instances of this fixture to create
* ``__options``: Possible options related to this endpoint:
* ``modifiers``: a list of modifier methods allowed for this resource. If you don't specify a method, that method won't be allowed for that endpoint
* ``excludeKey``: this can be specified to exclude a method from matching ``__key`` in the url. E.g. for the POST method for ``/resource/``, you might want to exclude it

The syntax for fake data is as follows: ``<fakedatatype:min:max>``

* ``fakedatatype`` is any attribute that can be generated by `Faker <https://faker.readthedocs.io/>`_
* ``min``: for numbers, it will only generated random numbers that are at least ``min`` or greater. For strings, this will be the first index it will slice from
* ``max``: for numbers, it will only generated random numbers that are at most ``max`` or smaller. For strings, this will be the last index

Special Characters

* ``^``: Putting a caret in front of the variable like "<^int:500:1000>" will generate only unique numbers between 500 to 1000


POST requests will not create new instances, but PUT, PATCH and DELETE will work as expected on the resources.
The resources are reset everytime the server is restarted.


Meta-Keys
=============

As you have probably seen in the examples above, there are special keys prefixed with double-underscores such as ``__key``. These are meta-keys which will be used to grant special properties to the mock responses.

* ``__key``: Represents the primary key/unique identifier of an instance
* ``__key_position``: Where the ``__key`` should be located in the url - there are only two options "url" or "query".
    * ``url``: The key should be within the main url such as ``/api/example/__key``
    * ``query``: They key should be within the params such as ``api/example?id[str]=__key``
* ``__mockcount``: The number of instances to create. Note that if ``__key`` is specified, an endpoint will be created that lists all the individual instances. However, if no ``__key`` is specified, then the endpoint will just return an array of N instances where N is specified in ``__mockcount``
* ``__relationships``: Relationships dictate simple relationships between items in the mock response. The syntax is always "<source__relationship__target>"
    * ``count``: It would be best illustrated with an example::

            {
                "__relationships": [
                    "user_count__count__users",
                ],
                "user_count": 20,
                "users": [
                    {
                        "id": "<int::50>",
                        "user": "<name>"
                    }
                ]
            }

    * If you want to specify a source value without displaying it in the eventual endpoint, you may use the hidden syntax with a double-dash::

            {
                "__relationships": [
                    "--user_count__count__users",
                ],
                "--user_count": 20,
                "users": [
                    {
                        "id": "<int::50>",
                        "user": "<name>"
                    }
                ]
            }
* ``__options``: Possible options related to this endpoint are as follows
    * ``modifiers``: a list of modifier methods allowed for this resource. If you don't specify a method, that method won't be allowed for that endpoint
    * ``excludeKey``: this can be specified to exclude a method from matching ``__key`` in the url. E.g. for the POST method for ``/resource/``, you might want to exclude it


Fixtures
========

More often than not, you will need to load fixtures to populate the mock endpoints.

We can load fixtures during generation by specifying the ``--fixtures`` flag:
``python manage.py genmockserver --fixtures data``

Note that the folders must be direct parents. All files with ``.json`` extension will be taken into account.

The syntax for that will be: "<key__from__filename>"

If a file called ``users.json`` was loaded, then you can do::

    {
        "id": "<id__from__users>",
        "full_name": "<first_name__from__users> <last_name__from__users>",
        "contact": "<contact__from__users>"
    }

The JSON files must follow Django's format of JSON fixtures and the fields must include the keys used in the mock response. So "id", "first_name", "last_name" and "contact" must all exist in the users fields.


Other Factory Methods (Not included in Faker)
=============================================
* ``percentage``: Will generate a percentage between 0 - 100 by default, you may specify the lower and upper bound to override the default range.


Advanced Usage with *
=====================

There may be a situation where you would like to specify the keys in an endpoint and what type of response each key maps to.

For example, you might have the following base URL "/api/example" and you would like to have the following key definition::

    URL: /api/example?id[str]=__key

    {
        "__key": "<*id:str>",
        "__key_position": "query",
        "users": [
            {
                "id": "<id__from__users>",
                "name": "<name__from__users>"
            }
        ],
        "burgers": [
            {
                "id": "<id__from__burgers>",
                "burger_type": "<burger__from__burgers>"
            }
        ]
    }

This will generate an endpoint that allows for two specific keys "/api/example?id=users" and "/api/example?id=burgers", which will each respond with whatever is defined under them.
Note the asterisk in front of the key which indicates that all non-meta keys will be taken as keys for this endpoint. In this case, our keys are "users" and "burgers"

Example
=======

Refer to the example app for a detailed example.

To-do
=====

* Allow for special queries such as 'limit', 'offset' and make them configurable (i.e. instead of 'limit', 'offset', user can set other names for the same function)
* Update exampleapp to include more usage examples
