.PHONY: clean virtualenv test

clean:
	find . -name '*.py[co]' -delete
	find . -name "__pycache__" -type d -empty -delete

virtualenv:
	virtualenv --prompt '|> confdict <| ' -p python3 env
	env/bin/pip install -r requirements-dev.txt
	env/bin/python setup.py develop
	@echo
	@echo "VirtualENV Setup Complete. Now run: source env/bin/activate"
	@echo

test:
	python -m pytest \
		-vv \
		--ignore=env \
		--cov=confdict \
		--cov-report=term-missing \
		tests/
