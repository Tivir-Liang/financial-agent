from setuptools import setup, find_packages

setup(
    name="financial-agent",
    version="0.1.0",
    packages=find_packages(),
    install_requires=["openai", "pandas", "numpy", "yfinance", "statsmodels", "pandas-datareader"],
    entry_points={
        'console_scripts': [
            'financial-agent=financial_agent.agent:main', 
        ],
    },
)