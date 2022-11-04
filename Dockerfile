FROM rockylinux:8

RUN dnf -y upgrade && \
    dnf -y install epel-release dnf-plugins-core rpmdevtools git curl 'dnf-command(copr)' && \
	dnf -y copr enable kwetlesen/libmdbx && \
    rpmdev-setuptree

WORKDIR /root/build
COPY . .

CMD [ "/root/build/buildrpm.sh", "--versionlist", "/root/build/versions.txt", "erigon.spec" ]
