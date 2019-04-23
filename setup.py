import os
import setuptools

this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, "README.md"), "r", encoding='utf-8') as f:
    long_description = f.read()

setuptools.setup(
    name="dbinspector",
    version="0.1.0",
    author="Chrys Gonsalves",
    author_email="cgons@pcxchange.ca",
    description="A libray for use with SQLAlchemy to count queires, log queries, etc...",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/cgons/dbinspector",
    packages=setuptools.find_packages(),
    install_requires=[
        "sqlalchemy",
        "psycopg2-binary",
    ],
    extras_require={
        'dev': [
            'pytest',
            'black',
            "ipython",
            "ipdb",
            "wheel",
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
