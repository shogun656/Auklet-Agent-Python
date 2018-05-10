#!/bin/bash
set -e
if [[ "$1" == "" ]]; then
  echo "ERROR: env not provided."
  exit 1
fi
ENVDIR=$1
VERSION="$(cat ~/.version)"
VERSION_SIMPLE=$(cat ~/.version | xargs | cut -f1 -d"+")
VERSION_PEP440=$(cat ~/.version440)
export TIMESTAMP="$(date --rfc-3339=seconds | sed 's/ /T/')"

if [[ "$ENVDIR" == "production" ]]; then
  echo 'Deploying to PyPI...'
  # Make and upload the distribution.
  # Update setuptools so we have a version that supports Markdown READMEs.
  # twine is also required.
  sudo pip install -U setuptools twine wheel
  python setup.py sdist bdist_wheel
  if [[ "$TWINE_REPOSITORY_URL" != "" ]]; then
    twine upload --repository-url $TWINE_REPOSITORY_URL dist/*
  else
    twine upload dist/*
  fi
  # Push to public GitHub repo.
  # The hostname "aukletio.github.com" is intentional and it matches the "ssh-config-aukletio" file.
  echo 'Pushing production branch to github.com/aukletio...'
  mv ~/.ssh/config ~/.ssh/config-bak
  cp .devops/ssh-config-aukletio ~/.ssh/config
  chmod 400 ~/.ssh/config
  git remote add aukletio git@aukletio.github.com:aukletio/Auklet-Agent-Python.git
  git push aukletio HEAD:master
  git remote rm aukletio
  rm -f ~/.ssh/config
  mv ~/.ssh/config-bak ~/.ssh/config
fi
