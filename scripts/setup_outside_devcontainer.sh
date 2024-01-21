#! /usr/bin/env bash

if [[ ! -d .venv ]]; then
  eval "$(pyenv init -)"
  python3 -m venv .venv
fi

source .venv/bin/activate
source scripts/setup.sh
