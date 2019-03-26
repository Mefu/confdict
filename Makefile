.PHONY: clean virtualenv test

clean:
	find . -name '*.py[co]' -delete
	find . -name "__pycache__" -type d -empty -delete
	find . -name ".pytest_cache" -type d -exec rm -rv {} +
	find . -name "pip-wheel-metadata" -type d -exec rm -rv {} +

virtualenv: SHELL:=/bin/bash
virtualenv:
	virtualenv --prompt '|> confdict <| ' -p python3 env
	source env/bin/activate; \
	pip install poetry; \
	poetry install
	@echo
	@echo "VirtualENV Setup Complete."
	@echo

test:
	python -m pytest \
		-vv \
		--ignore=env \
		--cov=confdict \
		--cov-report=term-missing \
		tests/
