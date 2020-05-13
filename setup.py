from setuptools import setup

from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(name='parse_ecli',
      version='0.9.4',
      description='Parse German ECLI',
      long_description=long_description,
      long_description_content_type="text/markdown",
      url='http://github.com/kiersch/parse_ecli',
      author='Philipp Kiersch',
      author_email='philipp@kiersch.org',
      license='MIT',
      packages=['parse_ecli'],
      python_requires='>=3.8',
      zip_safe=False,
      classifiers=[
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Legal Industry",
        "Topic :: Text Processing :: Filters",
        'Topic :: Text Processing :: Linguistic',
        ],
        include_package_data=True,
        entry_points={
    'console_scripts': [
        'parse-ecli = parse_ecli.parse_ecli:main_func',
    ],
},
      )
