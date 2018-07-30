#!/usr/bin/env bash

set -e

VERSION=$1
INSTALL_LATEST=$2

eval "$(pyenv init -)"

if [ ! -d "$(pyenv root)"/plugins/pyenv-install-latest ]; then
    sudo git clone https://github.com/momo-lab/pyenv-install-latest.git "$(pyenv root)"/plugins/pyenv-install-latest
    sudo mkdir "$(pyenv root)"/shims
    sudo mkdir "$(pyenv root)"/versions
fi

if [[ "$INSTALL_LATEST" == 'false' ]]; then
    pyenv install $VERSION
    LATEST_VERSION=$(pyenv versions | grep $VERSION | grep -v '2.7.12' | grep -v '3.5.2')
    pyenv global $LATEST_VERSION
else
    pyenv install-latest $VERSION
    LATEST_VERSION=$(pyenv versions | grep $VERSION | grep -v '2.7.12' | grep -v '3.5.2')
fi

bash .devops/tests.sh