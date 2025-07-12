"""
SUMO Helper Backend Setup
Web-based traffic simulation tool with OSM integration
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), '..', 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "SUMO Helper - Web-based traffic simulation tool"

# Read requirements
def read_requirements():
    requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(requirements_path):
        with open(requirements_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return []

setup(
    name="sumo-helper-backend",
    version="1.0.0",
    description="Backend for SUMO Helper - Web-based traffic simulation tool",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    author="SUMO Helper Contributors",
    author_email="contributors@sumo-helper.org",
    url="https://github.com/gsmkev/sumo-helper",
    packages=find_packages(),
    include_package_data=True,
    install_requires=read_requirements(),
    python_requires=">=3.11",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
    ],
    keywords=[
        "sumo",
        "traffic-simulation",
        "openstreetmap",
        "osm",
        "traffic-analysis",
        "transportation",
        "simulation",
        "fastapi",
        "web-application"
    ],
    entry_points={
        "console_scripts": [
            "sumo-helper=main:main",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/gsmkev/sumo-helper/issues",
        "Source": "https://github.com/gsmkev/sumo-helper",
        "Documentation": "https://github.com/gsmkev/sumo-helper#readme",
    },
) 