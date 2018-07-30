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
    LATEST_VERSION=$(pyenv versions | grep $VERSION | grep -v '2.7.12' | grep -v '3.5.2' | grep -v system)
    pyenv global $LATEST_VERSION
else
    pyenv install-latest $VERSION
    LATEST_VERSION=$(pyenv versions | grep $VERSION | grep -v '2.7.12' | grep -v '3.5.2' | grep -v system)
    pyenv global $LATEST_VERSION
fi

bash .devops/tests.sh