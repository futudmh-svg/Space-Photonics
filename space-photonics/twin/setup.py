from setuptools import setup, find_packages

setup(
    name="space-photonics-twin",
    version="0.2.0",
    description="All-optical digital twin for VLEO satellite-to-hypersonic vehicle optical communication",
    author="Space Photonics Team",
    packages=find_packages(),
    install_requires=[
        "numpy>=1.20.0",
        "matplotlib>=3.3.0",
    ],
    extras_require={
        "dev": ["pytest>=6.0", "jupyter>=1.0"],
    },
    python_requires=">=3.8",
)
