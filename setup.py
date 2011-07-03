from setuptools import setup

setup(
    name='gutils',
    version='0.1',
    author='Kenji Wellman',
    description='Decorators for rate-limiting, caching, and automatic retries using gevent',
    packages=['gutils'],
    install_requires=['gevent'],
)
