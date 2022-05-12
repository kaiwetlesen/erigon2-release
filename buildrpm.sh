#!/bin/bash
set -e
spec=$1
if [ ! -f "$spec" ]; then
	echo "Spec $1 not found"
	exit 1
fi
dnf -y upgrade
dnf -y install dnf-plugins-core rpmdevtools
dnf -y copr enable kwetlesen/libmdbx
cd /root
rpmdev-setuptree
cd -
dnf -y builddep $spec
if [ -f builds.txt ]; then
	echo '----------------------- Fetching sources -----------------------'
	while read build; do
		version="$(echo "$build" | cut -d, -f1 | tr -d \')"
		commit="$(echo "$build" | cut -d, -f2 | tr -d \')"
		spectool --debug --get-files --all --sourcedir "--define=$version" "--define=$commit" $spec &
	done < builds.txt
	wait
	echo '----------------------- Running builds -----------------------'
	while read build; do
		version=$(echo "$build" | cut -d, -f1)
		commit=$(echo "$build" | cut -d, -f2)
		rpmbuild -D "$version" -D "$commit" -bb $spec &
	done < builds.txt
	wait
else
	rpmbuild -bb $spec
fi
