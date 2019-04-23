import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

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
