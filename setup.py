#!/usr/bin/env python
"""
Sentient Core v4 - Setup Script
"""

from setuptools import setup, find_packages
import os

# Read version from file
def get_version():
    version_file = os.path.join(os.path.dirname(__file__), 'VERSION')
    if os.path.exists(version_file):
        with open(version_file, 'r') as f:
            return f.read().strip()
    return "4.0.0"

# Read long description from README
def get_long_description():
    readme_file = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_file):
        with open(readme_file, 'r', encoding='utf-8') as f:
            return f.read()
    return ""

# Read requirements
def get_requirements():
    requirements_file = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    requirements = []
    if os.path.exists(requirements_file):
        with open(requirements_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    requirements.append(line)
    return requirements

setup(
    name="sentient-core",
    version=get_version(),
    author="Sentient Core Team",
    author_email="team@sentient-core.ai",
    description="Advanced AI Cognitive Architecture for Autonomous Systems",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    url="https://github.com/thotsl4yer69/sentient-core-v4",
    project_urls={
        "Bug Tracker": "https://github.com/thotsl4yer69/sentient-core-v4/issues",
        "Documentation": "https://github.com/thotsl4yer69/sentient-core-v4/docs",
        "Source Code": "https://github.com/thotsl4yer69/sentient-core-v4",
    },
    packages=find_packages(exclude=["tests", "tests.*", "docs", "examples"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
        "Natural Language :: English",
    ],
    python_requires=">=3.9,<3.12",
    install_requires=get_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.1.0",
            "black>=23.11.0",
            "isort>=5.12.0",
            "flake8>=6.1.0",
            "pylint>=3.0.0",
            "mypy>=1.7.0",
        ],
        "docs": [
            "sphinx>=7.2.0",
            "sphinx-rtd-theme>=2.0.0",
            "mkdocs>=1.5.0",
            "mkdocs-material>=9.4.0",
        ],
        "gpu": [
            "torch>=2.0.0",
            "torchvision>=0.15.0",
            "torchaudio>=2.0.0",
        ],
        "vision": [
            "opencv-python>=4.8.0",
            "pillow>=10.0.0",
            "scikit-image>=0.22.0",
        ],
        "audio": [
            "librosa>=0.10.0",
            "soundfile>=0.12.1",
            "pydub>=0.25.1",
            "pyaudio>=0.2.13",
        ],
        "all": [
            "pytest>=7.4.0",
            "black>=23.11.0",
            "torch>=2.0.0",
            "opencv-python>=4.8.0",
            "librosa>=0.10.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "sentient-core=sentient_core.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "sentient_core": [
            "config/*.yaml",
            "config/*.json",
            "assets/*",
        ],
    },
    zip_safe=False,
    keywords=[
        "artificial intelligence",
        "ai",
        "machine learning",
        "deep learning",
        "cognitive architecture",
        "autonomous systems",
        "reasoning",
        "planning",
        "natural language processing",
        "nlp",
        "llm",
        "large language models",
        "transformers",
    ],
)
