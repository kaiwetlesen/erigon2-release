#!/bin/bash
git checkout devel &> /dev/null
git pull &> /dev/null
git pull --tags &> /dev/null
git submodule update &> /dev/null
if ! git status 2>&1 | egrep -q 'nothing added to commit|working tree clean'; then
	echo 'Repository is not clean or correctly initialised. Cannot continue.'
	exit 2
fi
GIT_TAG=$(git tag | egrep "\<$1\>")
if [ -z "$GIT_TAG" ]; then
	echo "Version $1 not found"
	exit 1
fi
if git branch --no-color --list | egrep -q "\<erigon-$GIT_TAG\>"; then
	git checkout "erigon-$GIT_TAG" &> /dev/null
	git pull &> /dev/null
else
	git tag | egrep "\<$GIT_TAG\>" | xargs -i git checkout -b 'erigon-{}' 'tags/{}' &> /dev/null
fi
GIT_BRANCH=$(git branch --no-color --show-current)
GIT_COMMIT=$(git rev-parse HEAD)
if [ "$2" = 'list' ]; then
	GIT_TAG=$(echo $GIT_TAG | tr -d 'v')
	echo "$GIT_TAG	$GIT_COMMIT"
else
	echo GIT_TAG=$GIT_TAG
	echo GIT_COMMIT=$GIT_COMMIT
fi
