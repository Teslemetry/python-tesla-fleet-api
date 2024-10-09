import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="tesla_fleet_api",
    version="0.8.4",
    author="Brett Adams",
    author_email="hello@teslemetry.com",
    description="Tesla Fleet API library for Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Teslemetry/tesla_fleet_api",
    packages=setuptools.find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
    install_requires=["aiohttp", "aiolimiter"],
)
