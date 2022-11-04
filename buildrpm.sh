#!/bin/bash
set -e
if [ "$1" == "--versionlist" ]; then
	shift
	versionlist=$1
	shift
	if [ -n "$versionlist" ] && [ ! -f "$versionlist" ]; then
		echo 'Option "--versionlist" provided but does not point to a valid file'
		exit 1
	fi
fi
spec=$1
if [ ! -f "$spec" ]; then
	echo "Spec '$1' not found"
	exit 2
fi
dnf -y install dnf-plugins-core rpmdevtools
dnf -y copr enable kwetlesen/libmdbx
cd /root
rpmdev-setuptree
cd -
dnf -y builddep $spec
if [ -f "$versionlist" ]; then
	echo '----------------------- Fetching sources -----------------------'
	while read version; do
		spectool --debug --get-files --all --sourcedir --define="pkgver $version" $spec
	done < $versionlist
	wait
	echo '----------------------- Running builds -----------------------'
	while read version; do
		rpmbuild -D "pkgver $version" -bb $spec # &
	done < $versionlist
	wait
else
	spectool --debug --get-files --all --sourcedir $spec
	rpmbuild -bb $spec
fi
chmod -R a+r ${HOME}/rpmbuild/RPMS
