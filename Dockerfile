FROM rockylinux:8

RUN dnf -y install epel-release dnf-plugins-core rpmdevtools 'dnf-command(copr)'
RUN dnf -y copr enable kwetlesen/libmdbx
RUN rpmdev-setuptree
RUN dnf -y upgrade

WORKDIR /root/build
COPY . .

CMD [ "/root/build/buildrpm.sh", "--buildvarsfile", "/root/build/builds.txt", "erigon2.spec" ]
