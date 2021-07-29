from setuptools import setup, find_packages

version = '21.07.1'

setup(
    name='datalocker',
    version=version,
    description='Collect, store, and review online form submissions',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Framework :: Django',
        'Programming Language :: Python',
    ],
    keywords='Python Django',
    author='Paul Rentschler',
    author_email='par117@psu.edu',
    url='https://github.com/PSUEducationalEquity/datalocker',
    license='3-Clause BSD License',
    packages=find_packages(exclude=['ez_setup']),
    include_package_data=True,
    zip_safe=False,
    install_requires=[],
)
