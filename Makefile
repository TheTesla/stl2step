# SPDX-FileCopyrightText: 2025 Stefan Helmert <stefan@entroserv.de>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

.DEFAULT_GOAL := build
.PHONY: build lint test docs package deploy
PROJ_SLUG = stl2step
SHELL = bash

version=$(shell git describe --tags --abbrev=0)

build:
	echo "__version__ = \"$(version)\"" > ./$(PROJ_SLUG)/_version.py
	poetry version $(version)
	poetry build

lint:
	poetry run black --check .
	poetry run isort --check .
	poetry run reuse lint

test: clean
	mkdir -p build
	poetry run pytest tests/

docs:
	poetry run sphinx-apidoc -f -o ./docs/source/ ./$(PROJ_SLUG)
	cd docs && poetry run make html

package: clean docs
	poetry build

prepair-publish:
	sed -i "s/screw_step.png/https:\/\/raw.githubusercontent.com\/TheTesla\/stl2step\/refs\/tags\/$(version)\/example_step.png/g" README.md

publish:
	poetry publish

clean:
	echo "__version__ = \"0.0.0+devel\"" > ./$(PROJ_SLUG)/_version.py
	poetry version 0.0.0+devel
	rm -rf .pytest_cache \
	rm -rf dist \
	rm -rf build \
	rm -rf __pycache__ \
	rm -rf $(PROJ_SLUG)/__pycache__ \
	rm -rf tests/__pycache__
	rm -rf stl2step.dist
	rm -rf stl2step.build
	rm -f tests/resources/*.step
	#rm -rf docs/build \
	rm -rf *.egg-info \
	rm -rf docs/source/modules \
	rm -rf htmlcov \
	rm -rf meta\
	rm -rf output

reformat:
	poetry run isort .
	poetry run black .
