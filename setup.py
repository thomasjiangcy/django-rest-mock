import os
from setuptools import setup, find_packages


here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()

setup(
    name='django-rest-mock',
    version='0.2.6',
    packages=find_packages(),
    description='Mock Express server generated based on your views, that can come in handy when developing REST APIs with Django',
    long_description=README,
    author='Thomas Jiang',
    author_email='thomasjiangcy@gmail.com',
    url='https://github.com/thomasjiangcy/django-rest-mock-server',
    license='MIT',
    install_requires=[
        'Django>=1.11',
        'Faker>=0.8.11'
    ],
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        'Framework :: Django',
        'Framework :: Django :: 1.11',
        'Framework :: Django :: 2.0',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
