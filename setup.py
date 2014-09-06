from setuptools import setup

setup(
    name="python-dotenv",
    description=".env file settings for non-heroku setups",
    version="0.1.0",
    author="Saurabh Kumar",
    author_email="me+github@saurabh-kumar.com",
    url="http://github.com/theskumar/python-dotenv",
    py_modules=['dotenv'],
    install_requires=[
        'click>=3.0',
    ],
    entry_points='''
        [console_scripts]
        dotenv=dotenv:cli
    ''',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 2.7',
    ]
)
