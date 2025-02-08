import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pyaces",
    version="0.1.0",  # Remove 'v' prefix from version number
    packages=setuptools.find_packages(include=["pyaces"]),
    license="MIT",
    author="Remy Tuyeras",
    author_email="rtuyeras@gmail.com",
    description="A Python library for the fully homomorphic encryption scheme ACES.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/remytuyeras/aces",
    keywords=["ACES", "PyACES"],
    install_requires=["numpy"],
    classifiers=[
        "Development Status :: 4 - Beta",  # "3 - Alpha", "4 - Beta" or "5 - Production/Stable"
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Software Development :: Build Tools",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],
    # The `download_url` is commented out, but if you plan to use it, uncomment and format it correctly:
    # download_url="https://github.com/remytuyeras/aces/archive/refs/tags/pyaces-0.1.0.tar.gz",
)
