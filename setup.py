#!/usr/bin/env python3
"""
setup.py
Setup script for Vehicle Detection System
"""

from setuptools import setup, find_packages
import os

# Read requirements
def read_requirements():
    requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(requirements_path):
        with open(requirements_path, 'r') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return []

# Read README
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "Vehicle Detection System with GUI and CLI interfaces"

setup(
    name="vehicle-detection-system",
    version="1.0.0",
    description="Modular vehicle detection system with GUI and CLI modes",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    author="Vehicle Detection Team",
    author_email="team@vehicledetection.com",
    url="https://github.com/yourusername/vehicle-detection-system",
    packages=find_packages(),
    install_requires=read_requirements(),
    extras_require={
        'gui': ['tkinter', 'pillow'],
        'dev': ['pytest', 'black', 'flake8', 'mypy'],
    },
    python_requires=">=3.8",
    entry_points={
        'console_scripts': [
            'vehicle-detection=main:main',
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="vehicle detection, computer vision, opencv, openvino, gui, cli",
    include_package_data=True,
    zip_safe=False,
)