from setuptools import setup

setup(
    name='focus',
    version='0.8',
    packages=['focus'],
    include_package_data=True,
    install_requires=[
        'flask',
    ],
    long_description=open('README.md').read(),
)
