import pathlib

from setuptools import find_packages, setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

packages = find_packages(exclude=["test_*", "*.tests"])

setup(
    name="strongtyping",
    version="3.12.1",
    description="Decorator which checks whether the function is called with the correct type of parameters",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://strongtyping.readthedocs.io/en/latest/",
    author="FelixTheC",
    author_email="fberndt87@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.12",
    ],
    packages=packages,
    package_data={"strongtyping-stubs": ["**/*.py", "**/*.pyi"]},
    python_requires=">=3.12",
    include_package_data=True,
)
