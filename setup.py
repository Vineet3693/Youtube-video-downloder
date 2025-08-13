
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="youtube-downloader-app",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A modern YouTube video and playlist downloader web application",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/youtube-downloader-app",
    project_urls={
        "Bug Tracker": "https://github.com/yourusername/youtube-downloader-app/issues",
        "Documentation": "https://github.com/yourusername/youtube-downloader-app/docs",
        "Source Code": "https://github.com/yourusername/youtube-downloader-app",
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Multimedia :: Video",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    package_dir={"": "."},
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=4.0",
            "black>=22.0",
            "flake8>=5.0",
            "mypy>=1.0",
        ],
        "prod": [
            "gunicorn>=20.0",
            "nginx",
        ],
    },
    entry_points={
        "console_scripts": [
            "youtube-downloader=app.main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.toml", "*.yaml", "*.yml", "*.md", "*.txt"],
        "assets": ["images/*", "styles/*"],
    },
)
