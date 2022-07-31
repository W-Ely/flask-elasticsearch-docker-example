.PHONY: help clean clean-all kill docker_network seed-elasticsearch build run \
	dev kibana test lint code

code-directory := api
test-directory := tests
root-code-files := seed.py gunicorn.conf.py manage.py config.py
code-files := $(shell find $(code-directory) -name '*.py' -not \( -path '*__pycache__*' \))
test-files := $(shell find $(test-directory) -name '*.py' -not \( -path '*__pycache__*' \))

python := python3
pip := venv/bin/pip

DOCKER_NETWORK_NAME ?= 'geo_services'

help:
	@grep -E '^[0-9a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

clean: ## clean local assets
	rm -rf venv
	rm -f .venv
	rm -rf .pytest_cache
	rm -f .coverage
	rm -f pytest-out.xml
	rm -f supervisord.log
	rm -f supervisord.pid

clean-all: clean
	docker-compose down -v
	docker-compose rm -f -s -v
	docker images geo-search:latest -a -q | xargs docker rmi
	docker images geo-search:build-python-deps -a -q | xargs docker rmi
	docker images geo-search:build-sys-deps -a -q | xargs docker rmi
	docker network rm $(DOCKER_NETWORK_NAME) | true

venv:
	$(python) -m venv venv

.venv: venv requirements_dev.txt
	$(pip) install --progress-bar off --upgrade pip wheel
	$(pip) install --progress-bar off -r requirements_dev.txt
	touch .venv

kill: ## Stop all running services
	docker-compose down -v

docker-network:  ## Starts docker networking
	docker network inspect $(DOCKER_NETWORK_NAME) >/dev/null || docker network create $(DOCKER_NETWORK_NAME)

seed-elasticsearch: docker-network build  ## Starts and seeds Elasticsearch
	docker-compose up -d elasticsearch
	docker-compose run --rm api python -c 'import seed; seed.search();'

build: $(code-directory) $(root-code-files) $(test-directory) ## Build the service
	docker build . -t geo-search:build-system-deps --target build-system-deps --rm
	docker build . -t geo-search:build-python-deps --target build-python-deps --rm
	docker build . -t geo-search:latest --target release --rm

run: docker-network build seed-elasticsearch ## Starts a clean Elasticsearch and runs the Flask app in the current window
	docker-compose up api

dev: docker_network build seed-elasticsearch ## Starts a clean Elasticsearch and runs the Flask app in the current window with automatic reloading on code changes.
	docker-compose run -p 8080:8080 api /bin/bash -c "gunicorn -c gunicorn.conf.py --reload manage:app -b 0.0.0.0:8080"

kibana:  ## Start a local kibana for testing elasticsearch
	docker-compose up kibana

t ?=
test: docker-network build
	docker-compose run --rm -e STAGE=testing api py.test $(t) \
		--junit-xml=pytest-out.xml --cov=$(code-directory) --cov-report=term-missing

lint: .venv ## Run syntax/style check.
	venv/bin/black --line-length=101 --safe -v $(code-directory) $(root-code-files) $(test-directory)
	venv/bin/flake8 --max-line-length=101 $(code-directory) $(root-code-files) $(test-directory)

code: lint test ## Run both lint and tests
