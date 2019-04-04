.PHONY: help clean clean-pyc lint run-dev

help:
	@echo "clean - Remove all build, test, coverage and Python artifacts"
	@echo "run-dev - Run Development Server"

clean: clean-pyc

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

lint:
	flake8

dev-up:
	docker-compose -f docker/dev-compose.yml up

dev-down:
	docker-compose -f docker/dev-compose.yml down

test-up:
	docker-compose -f docker/test-compose.yml up

test-down:
	docker-compose -f docker/test-compose.yml down

run-dev:
	docker-compose -f docker/dev-compose.yml up -d && \
	cd core && \
	FLASK_ENV=development FLASK_APP=core.application ../venv/bin/flask run
