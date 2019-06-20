from setuptools import setup, find_packages

setup(
    name='focus',
    version='0.8',
    packages=find_packages(exclude=('venv', '*__pycache__')),
    include_package_data=True,
    install_requires=[
        'flask',
    ],
    long_description=open('README.md').read(),
)
