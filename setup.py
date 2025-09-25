from setuptools import setup, find_packages
import pathlib

# Read requirements.txt
this_dir = pathlib.Path(__file__).parent
requirements = (this_dir / "requirements.txt").read_text().splitlines()

setup(
    name="safechatter",
    version="0.1.0",
    description="SafeChatter Package",
    author="Monica Tare",
    author_email="mtare@twilio.com",
    packages=find_packages(exclude=("tests", "docs")),
    include_package_data=True,
    install_requires=requirements,
    python_requires=">=3.8",
)