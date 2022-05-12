from rockylinux
copy buildrpm.sh .
copy erigon.spec .

run dnf -y install epel-release 'dnf-command(copr)'
run dnf -y copr enable kwetlesen/libmdbx

