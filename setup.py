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
        'plotly',
        'lifelines'
    ],
    entry_points={
        'console_scripts': [
            'start-app = app:app.py',  
        ],
    },
)