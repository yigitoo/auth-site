# define the name of the virtual environment directory
VENV := venv

# default target, when make executed without arguments
all: venv
ifeq ($(OS), Windows_NT)
$(VENV)/bin/activate: requirements.txt
	python3 -m venv $(VENV)
	.\$(VENV)\Scripts\pip install -r requirements.txt
else
$(VENV)/bin/activate: requirements.txt
	python3 -m venv $(VENV)
	./$(VENV)/bin/pip install -r requirements.txt
endif
# venv is a shortcut target
venv: $(VENV)/bin/activate

run: venv
	.\$(VENV)\Scripts\python3.exe .\src\main.py
clean:
	rm -rf $(VENV)
	ifneq ($(OS), Windows_NT)
		find . -type f -name '*.pyc' -delete
	endif
.PHONY: all venv run clean