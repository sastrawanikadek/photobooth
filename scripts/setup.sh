#! /usr/bin/env bash

python3 -m scripts.generate_requirements

pip3 install -r requirements-dev.txt
pip3 install -r requirements.txt
pip3 install -r requirements-components.txt

pre-commit install
