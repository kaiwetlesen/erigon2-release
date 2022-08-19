#!/bin/bash
set -e
if [ "$1" == "--buildvarsfile" ]; then
	shift
	buildvars=$1
	shift
	if [ -n "$buildvars" ] && [ ! -f "$buildvars" ]; then
		echo 'Option "--buildvars" provided but does not point to a valid file'
		exit 1
	fi
else
	echo "something: $1"
fi
spec=$1
if [ ! -f "$spec" ]; then
	echo "Spec '$1' not found"
	exit 2
fi
dnf -y upgrade
dnf -y install dnf-plugins-core rpmdevtools
dnf -y copr enable kwetlesen/libmdbx
cd /root
rpmdev-setuptree
cd -
dnf -y builddep $spec
if [ -f "$buildvars" ]; then
	echo '----------------------- Fetching sources -----------------------'
	while read build; do
		version="$(echo "$build" | cut -d, -f1 | tr -d \')"
		commit="$(echo "$build" | cut -d, -f2 | tr -d \')"
		spectool --debug --get-files --all --sourcedir --define="$version" --define="$commit" $spec
	done < $buildvars
	wait
	echo '----------------------- Running builds -----------------------'
	while read build; do
		version=$(echo "$build" | cut -d, -f1 | tr -d \')
		commit=$(echo "$build" | cut -d, -f2 | tr -d \')
		rpmbuild -D "$version" -D "$commit" -bb $spec # &
	done < builds.txt
	wait
else
	spectool --debug --get-files --all --sourcedir $spec
	rpmbuild -bb $spec
fi
chmod -R a+r ${HOME}/rpmbuild/RPMS
