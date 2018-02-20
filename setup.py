import os
from setuptools import setup


here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()

setup(
    name='django-rest-mock-server',
    version='0.344',
    packages=['rest_mock_server'],
    description='Mock Express server generated based on your views, that can come in handy when developing REST APIs with Django',
    long_description=README,
    author='Thomas Jiang',
    author_email='thomasjiangcy@gmail.com',
    url='https://github.com/thomasjiangcy/django-rest-mock-server',
    license='MIT',
    install_requires=[
        'Django>=1.11',
        'Faker>=0.8.11'
    ]
)
