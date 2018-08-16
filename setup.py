# coding=utf-8
from setuptools import setup


def readme():
    with open('README.md') as desc:
        return desc.read()


setup(
    name='logi_circle',
    packages=['logi_circle'],
    version='0.0.3',
    description='A Python library to communicate with Logi Circle cameras',
    long_description=readme(),
    author='Evan Bruhn',
    author_email='evan.bruhn@gmail.com',
    url='https://github.com/evanjd/python-logi-circle',
    license='MIT',
    include_package_data=True,
    install_requires=['requests', 'pytz'],
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
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Home Automation',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
)
