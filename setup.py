import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name = 'pyaces',
    packages=setuptools.find_packages(include=['pyaces']),
    version = 'v0.1.0',
    license='MIT',
    author = 'Remy Tuyeras',
    author_email = 'rtuyeras@gmail.com',
    description = 'A python library for the fully homomorphic encryption scheme ACES.',
    long_description = long_description,
    long_description_content_type = "text/markdown",
    url = 'https://github.com/remytuyeras/aces',
    #downlod_url = 'https://github.com/remytuyeras/aces/archive/refs/tags/aces-0.0.2.tar.gz',
    keywords = ["ACES", "PyACES"],
    install_requires=['numpy'],
    classifiers=[
        'Development Status :: 4 - Beta',  #"3 - Alpha", "4 - Beta" or "5 - Production/Stable"
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Topic :: Software Development :: Build Tools',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.12',
    ],
    )
