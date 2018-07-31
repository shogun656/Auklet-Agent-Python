#!/usr/bin/env bash

set -e

VERSION=$1

INSTALL_LATEST='true'

if [ "${#VERSION}" -gt 4 ]; then  # This checks if a complete version is passed
    INSTALL_LATEST='false'      # and if so, it will install that exact version
fi

eval "$(pyenv init -)"

if [[ "$INSTALL_LATEST" == 'false' ]]; then
    pyenv install $VERSION
else
    pyenv install-latest $VERSION
fi

LATEST_VERSION=$(pyenv versions | grep $VERSION | grep -vE "(2.7.12|3.5.2|system)")
pyenv global $LATEST_VERSION

bash .devops/tests.sh