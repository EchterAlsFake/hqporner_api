from setuptools import setup, find_packages

setup(
    name="hqporner_api",
    version="0.8",
    packages=find_packages(),
    install_requires=[
        "tqdm", "requests", "bs4", "lxml"
    ],
    entry_points={
        'console_scripts': [
            # If you want to create any executable scripts
        ],
    },
    author="EchterAlsFake | Johannes Habel",
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
