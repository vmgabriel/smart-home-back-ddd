VENV = venv
PYTHON = $(VENV)/bin/python3
PIP = $(VENV)/bin/pip
PYTEST = $(VENV)/bin/pytest

REQUIREMENTS = requirements.txt
TESTS_PATH = tests

clean:
	rm -rf __pycache__
	rm -rf $(VENV)


$(VENV)/bin/activate:
	$(PYTHON) -m virtualenv $(VENV)
	$(PIP) install -r $(REQUIREMENTS)


run: $(VENV)/bin/activate
	$(PYTHON) main.py


test: $(VENV)/bin/activate
	$(PYTEST) $(TESTS_PATH)
