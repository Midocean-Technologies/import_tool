from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in import_tool/__init__.py
from import_tool import __version__ as version

setup(
	name="import_tool",
	version=version,
	description="Import Tool",
	author="Midocean Technologies",
	author_email="info@midocean.tech",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
