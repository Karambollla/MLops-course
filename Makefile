PYTHON ?= python3
.PHONY: check test exercises links task task-list tasks tasks-collect
check:
	$(PYTHON) scripts/check_course.py

test:
	$(PYTHON) -m pytest tests labs/housing/tests -v --import-mode=importlib

task-list:
	$(PYTHON) scripts/run_task.py list

task:
	$(PYTHON) scripts/run_task.py test "$(TASK)"

tasks:
	$(PYTHON) scripts/run_task.py test --all

tasks-collect:
	$(PYTHON) -m pytest modules --collect-only --import-mode=importlib -q

exercises:
	RUN_EXERCISES=1 $(PYTHON) -m pytest labs/housing/tests -v --import-mode=importlib

links:
	$(PYTHON) scripts/check_external_links.py
