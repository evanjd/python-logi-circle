# coding=utf-8
from setuptools import setup


def readme():
    with open('README.md', encoding='utf-8') as desc:
        return desc.read()


setup(
    name='logi_circle',
    packages=['logi_circle'],
    version='0.1.8',
    description='A Python library to communicate with Logi Circle cameras',
    long_description=readme(),
    long_description_content_type='text/markdown',
    author='Evan Bruhn',
    author_email='evan.bruhn@gmail.com',
    url='https://github.com/evanjd/python-logi-circle',
    license='MIT',
    include_package_data=True,
    install_requires=['aiohttp', 'pytz'],
    test_suite='tests',
    keywords=[
        'logi',
        'logi circle',
        'logitech'
        'home automation',
    ],
    classifiers=[
        'Environment :: Other Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Framework :: AsyncIO',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Home Automation',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
)
