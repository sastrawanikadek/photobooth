#! /usr/bin/env bash

if [[ ! -d .venv ]]; then
  eval "$(pyenv init -)"
  python3 -m venv .venv
fi

source .venv/bin/activate

pip3 install -r requirements-dev.txt
pip3 install -r requirements.txt

python3 -m scripts.generate_requirements
pip3 install -r requirements-components.txt

yarn install

pre-commit install
