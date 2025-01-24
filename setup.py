from setuptools import setup, find_packages

setup(
    name='my_streamlit_app',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'pandas',
        'streamlit',
        'openpyxl',
        'scipy',
        'plotly'
    ],
    entry_points={
        'console_scripts': [
            'start-app = app:main',  # Adjust for your entry point if needed
        ],
    },
)