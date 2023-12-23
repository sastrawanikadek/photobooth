#! /usr/bin/env bash

if [[ ! -d .venv ]]; then
  python3 -m venv .venv
fi

source .venv/bin/activate
source scripts/setup.sh
