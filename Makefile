PYTHON ?= python3
.PHONY: check test exercises links
check:
	$(PYTHON) scripts/check_course.py

test:
	$(PYTHON) -m pytest labs/housing/tests -v

exercises:
	RUN_EXERCISES=1 $(PYTHON) -m pytest labs/housing/tests -v

links:
	$(PYTHON) scripts/check_external_links.py
