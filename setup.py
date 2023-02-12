#!/usr/bin/env python3

from setuptools import setup

if __name__ == '__main__':
    import sys

    if len(sys.argv) == 1:
        sys.argv.append('install')

with open('README.md', 'r') as f:
    long_description = f.read()

setup(
    name='parsed',
    packages=['parsed'],
    version='0.1',
    license='MIT',
    author='nggit',
    author_email='contact@anggit.com',
    description='A simple, pure Python 2.7/3.x HTTP parser',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/nggit/parsed',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
