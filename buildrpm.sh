#!/bin/bash
set -e
spec=$1
[ -f "$spec" ] || echo "Spec $1 not found"
cd /root
rm -rf anaconda-* original-*
dnf -y upgrade
dnf -y install dnf-plugins-core rpmdevtools
dnf -y copr enable kwetlesen/libmdbx
rpmdev-setuptree
dnf -y builddep $spec
if [ -f builds.txt ]; then
	echo Run these commands:
	while read build; do
		echo "spectool $build --get-files --sourcedir $spec && rpmbuild $build -bb $spec &"
	done < builds.txt
else
	rpmbuild -bb $spec
fi
