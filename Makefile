PYTHON ?= python3
.PHONY: check test links task task-list tasks tasks-collect
check:
	$(PYTHON) scripts/check_course.py

test:
	@echo "01-ml: проверки упражнений запускаются в modules/01-ml/housing.ipynb"
	$(PYTHON) -m pytest tests labs/housing/tests -v --import-mode=importlib

task-list:
	$(PYTHON) scripts/run_task.py list

task:
	$(PYTHON) scripts/run_task.py test "$(TASK)"

tasks:
	$(PYTHON) scripts/run_task.py test --all

tasks-collect:
	@echo "01-ml пропущен: проверки запускаются в modules/01-ml/housing.ipynb"
	$(PYTHON) -m pytest modules --collect-only --import-mode=importlib -q

links:
	$(PYTHON) scripts/check_external_links.py
