# Define variables
PYTHON := python
PIP := pip
VENV_DIR := venv
REQ_FILE := requirements.txt
STREAMLIT_APP := app.py 

# Default target
.PHONY: help
help:
	@echo "Makefile for managing your Streamlit project:"
	@echo "  make venv        - Create a virtual environment"
	@echo "  make install     - Install requirements from requirements.txt"
	@echo "  make run         - Run the Streamlit app"
	@echo "  make clean       - Remove temporary and cache files"
	@echo "  make freeze      - Freeze the current environment into requirements.txt"

# Create a virtual environment
.PHONY: venv
venv:
	@echo "Creating virtual environment..."
	$(PYTHON) -m venv $(VENV_DIR)
	@echo "Virtual environment created in $(VENV_DIR)."

# Install requirements
.PHONY: install
install: venv
	@echo "Installing requirements..."
	$(VENV_DIR)/bin/$(PIP) install -r $(REQ_FILE)

# Run the Streamlit app
.PHONY: run
run:
	@echo "Running the Streamlit app..."
	$(VENV_DIR)/bin/streamlit run $(STREAMLIT_APP)


# Clean up temporary and cache files
.PHONY: clean
clean:
	@echo "Cleaning up temporary files..."
	rm -rf $(VENV_DIR) __pycache__ *.pyc .pytest_cache .mypy_cache .streamlit

# Freeze requirements
.PHONY: freeze
freeze:
	@echo "Freezing environment to $(REQ_FILE)..."
	$(VENV_DIR)/bin/$(PIP) freeze > $(REQ_FILE)
	@echo "Updated $(REQ_FILE)."
