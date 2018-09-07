#!/bin/bash
set -e
VERSION=$1

export PYENV_ROOT="/home/circleci/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"

pyenv install-latest $VERSION

LATEST_VERSION=$(pyenv versions | grep $VERSION | grep -vE "(2.7.12|3.5.2|system)")
pyenv global $LATEST_VERSION

bash .devops/tests.sh
