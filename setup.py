from setuptools import setup, find_packages

setup(
    name="empowering-agents",
    version="0.1.0",
    description="Starter pack for empowerment-first marketing AI agents",
    packages=find_packages("src"),
    package_dir={"": "src"},
    install_requires=[],
    python_requires=">=3.9",
)
