from setuptools import setup, find_packages

setup(
    name="HQPorner_API",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "tqdm", "requests", "bs4"
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
    url="https://github.com/your_username/my_package",
    classifiers=[
        # Classifiers help users find your project on PyPI
        "License :: LGPLv3 License",
        "Programming Language :: Python",
    ],
)
