import pathlib
import setuptools

setuptools.setup(
    name="securenv",
    version="0.0.5",
    description="Simple TUI for Defining and Constraining Environment Variables",
    long_description=pathlib.Path("README.md").read_text(),
    long_description_content_type="text/markdown",
    url="https://github.com/TheDrowsyDev/securenv",
    author="DrowsyDev",
    license="Apache-2.0",
    project_urls={
        "Documentation": "https://github.com/TheDrowsyDev/securenv/blob/main/README.md",
        "Source": "https://github.com/TheDrowsyDev/securenv"
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Topic :: Utilities",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12"
    ],
    python_requires=">=3.8",
    install_requires=[
        "textual",
        "PyYaml",
        "python-dotenv",
        "schema"
    ],
    packages=setuptools.find_packages(),
    include_package_data=True,
    entry_points={"console_scripts": ["securenv = securenv.cli:main"]}
)
