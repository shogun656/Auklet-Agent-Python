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

echo 'Deploying to PyPI...'
# Update setuptools so we have a version that supports Markdown READMEs.
# twine is also required.
sudo pip install -U setuptools twine wheel
# Make and upload the distribution.
python setup.py sdist bdist_wheel
if [[ "$TWINE_REPOSITORY_URL" != "" ]]; then
  echo '[pypitest]' > ~/.pypirc
  echo "repository=$TWINE_REPOSITORY_URL" >> ~/.pypirc
  chmod 600 ~/.pypirc
  twine register -r pypitest $(cd dist ; ls *.gz)
  twine upload -r pypitest dist/*
else
  twine upload dist/*
fi
if [[ "$ENVDIR" == "production" ]]; then
  # Push to public GitHub repo.
  git remote add aukletio git@github.com:aukletio/Auklet-Agent-Python.git
  git push aukletio HEAD:master
fi
