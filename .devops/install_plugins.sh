#!/usr/bin/env bash

set -e

VERSION=$1

eval "$(pyenv init -)"

pyenv install-latest $VERSION