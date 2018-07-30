#!/usr/bin/env bash

set -e

VERSION=$1

if [ $VERSION == '3.7' ]; then
    INSTALL_LATEST='false'
fi

eval "$(pyenv init -)"

if [[ "$INSTALL_LATEST" == 'false' ]]; then
    pyenv install $VERSION
    LATEST_VERSION=$(pyenv versions | grep $VERSION | grep -v '2.7.12' | grep -v '3.5.2')
    pyenv global $LATEST_VERSION
else
    pyenv install-latest $VERSION
    LATEST_VERSION=$(pyenv versions | grep $VERSION | grep -v '2.7.12' | grep -v '3.5.2')
fi

bash .devops/tests.sh