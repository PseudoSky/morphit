"""
Setup script.
"""
from distutils.core import Command
from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

class Coverage(Command):
    """
    Coverage setup.
    """

    description = (
        "Run test suite against single instance of"
        "Python and collect coverage data."
    )
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        import coverage
        import unittest

        cov = coverage.coverage(config_file='.coveragerc')
        cov.erase()
        cov.start()

        test_loader = unittest.TestLoader()
        test_suite = test_loader.discover(start_dir='tests')
        unittest.TextTestRunner().run(test_suite)

        cov.stop()
        cov.save()
        cov.report()
        cov.html_report()


setup(
    name='morphit',
    description='makes shitty data more fit (a smarter serializer)',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='pseudosky',
    keywords='serialize data schema transform parse parser parsing',
    classifiers=[
        'Topic :: Software Development :: Libraries',
        'Topic :: Utilities',
        'Topic :: Text Editors :: Text Processing',
        'Topic :: Text Processing'
    ],
    author_email='grepthesky@gmail.com',
    download_url='',
    cmdclass={
        'coverage': Coverage,
    },
    install_requires=[
      'multipledispatch>=0.4.9',
      'iso8601>=0.1.12'
    ],
    license='MIT',
    packages=[
        'morphit',
    ],
    scripts=[],
    test_suite='tests',
    tests_require=[
        'codecov>=2.0.3,<3.0.0',
        'coverage>=4.0.3,<5.0.0',
        'Sphinx>=1.4.1,<2.0.0',
        'tox>=2.3.1,<3.0.0',
        'virtualenv>=15.0.1,<16.0.0'
    ],
    url='https://github.com/PseudoSky/morphit',
    version='1.2.0',
)
