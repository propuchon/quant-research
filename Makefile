#################################################################################
# GLOBALS                                                                       #
#################################################################################

VENV_NAME = .venv
PYTHON_INTERPRETER = python

#################################################################################
# COMMANDS                                                                      #
#################################################################################

install:
	pip install --upgrade pip
	pip install -U -r requirements.txt

format:
	autoflake -i --remove-all-unused-imports --ignore-init-module-imports --expand-star-imports --exclude venv -r .
	isort .
	black .

venv:
	$(PYTHON_INTERPRETER) -m venv $(VENV_NAME)