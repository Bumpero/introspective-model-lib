from setuptools import setup, find_packages

setup(
    name="introspective_model_lib",
    version="1.0.0",
    description="A library for generating database schemas from input data.",
    author="Your Name",
    packages=find_packages(),
    install_requires=["pyyaml"],
    entry_points={
        "console_scripts": [
            "introspective-model=introspective_model_lib.main:main",
        ],
    },
)
