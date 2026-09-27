"""AGENTLENS setup script."""
from setuptools import setup, find_packages

setup(
    name="agentlens",
    version="1.0.0",
    description="AI Agent Reliability Intelligence - See where AI agents fail. Prove why.",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[
        "fastapi>=0.111.0",
        "uvicorn[standard]>=0.30.1",
        "pydantic>=2.7.4",
        "pydantic-settings>=2.3.4",
        "scikit-learn>=1.5.2",
        "pandas>=2.2.2",
        "numpy>=1.26.4",
        "jinja2>=3.1.4",
        "httpx>=0.27.2",
        "python-multipart>=0.0.9",
    ],
    entry_points={
        "console_scripts": [
            "agentlens=agentlens.main:main",
        ],
    },
)
