#!/bin/bash
git pull --tags &> /dev/null
GIT_TAG=$(git tag | egrep "\<$1\>")
if [ -z "$GIT_TAG" ]; then
	echo "Version $1 not found"
	exit 1
fi
if git branch --no-color --list | egrep -q "\<erigon-$GIT_TAG\>"; then
	git checkout "erigon-$GIT_TAG" &> /dev/null
	git pull &> /dev/null
else
	git tag | egrep "\<$GIT_TAG\>" | xargs -i git checkout 'tags/{}' -b 'erigon-{}' &> /dev/null
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
