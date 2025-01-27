# Project Overview
This project in streamlit app composed by 3 modules, the data generation part for scenario 1 and 2 and the modeling part.
In order to navigate the project remember to use the navigator on the top of the main page.


# Instructions for Using the Makefile

This project uses a `Makefile` to simplify the setup and management of the Streamlit application. Below are the available commands and how to use them.

## Prerequisites
Before using the `Makefile`, ensure the following are installed on your system:
- **Python**: Version 3.11.5
- **`pip`**: Python package manager
- **`make`**: Comes pre-installed on Linux/macOS. On Windows, install it using:
  - [Chocolatey](https://chocolatey.org/install): `choco install make`
  - [Git Bash](https://git-scm.com/) or [WSL](https://learn.microsoft.com/en-us/windows/wsl/install).
- **Run** run the make comand from the root directory.
---

## Available Commands

### 1. Create a Virtual Environment
To create a Python virtual environment for the project, run:
```bash
make venv
```
### 2. Install Dependencies
```bash
make install
```

### 3. Run the Streamlit App
```bash
make run
```
### 4. Clean Up Temporary Files
This will clean up:

The virtual environment (venv)
Cache files (__pycache__, .pytest_cache, etc.)
.streamlit cache files
```bash
make clean
```
### 5. Freeze Dependencies
```bash
make freeze
```

### 6. Work flow order 

make venv
make install
make run
make clean
make freeze

### 7. Navigating the App

Begin with the data generation part inserting the parameters.
Control the main metrics of the generated data. 
Navigate to the "launch the model" section to calculate the shrinking risk and the estimation of the availables containers in time. 