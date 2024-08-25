from setuptools import setup, find_packages

setup(
    name="ai model manager",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "huggingface_hub",
        "wget",
        "civitdl",
        "python-dotenv",
    ],
    entry_points={
        "console_scripts": [
            "pp-manager-dl=run:download_model",
            "pp-manager-clear=run:clearup_space",
            "pp-manager-reload=run:redownload_models",
        ],
    },
)