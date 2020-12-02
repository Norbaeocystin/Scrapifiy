import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="scrapify",
    install_requires=["pymongo","requests","bs4","selenium", "lxml"],
    version="1.2.0",
    author="Rastislav_Baran",
    author_email="baranrastislav@gmail.com",
    description="Python classes to help with scraping data from internet ",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
