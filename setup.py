from setuptools import setup, find_packages

setup(
    name="hqporner_api",
    version="1.7.5",
    packages=find_packages(),
    install_requires=[ "bs4", "eaf_base_api"],
    entry_points={
        'console_scripts': ['hqporner_api=hqporner_api.api:main'
            # If you want to create any executable scripts
        ],
    },
    author="Johannes Habel",
    author_email="EchterAlsFake@proton.me",
    description="A Python API for the Porn Site HQPorner.com",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    license="LGPLv3",
    url="https://github.com/EchterAlsFake/hqporner_api",
    classifiers=[
        # Classifiers help users find your project on PyPI
        "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
        "Programming Language :: Python",
    ],
)
