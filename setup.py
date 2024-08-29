from setuptools import setup, find_packages

setup(
    name="cozy-manager",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "huggingface_hub",
        "wget",
        "civitdl",
        "requests",
        "bs4",
        "python-dotenv",
    ],
    entry_points={
        "console_scripts": [
            "cozy=run:main",
        ],
    },
)