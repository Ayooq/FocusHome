from setuptools import setup

setup(
    name='focus',
    packages=['focus'],
    include_package_data=True,
    install_requires=[
        'flask',
    ],
    long_description=open('README.md').read(),
)
