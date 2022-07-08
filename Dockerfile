FROM rockylinux

RUN dnf -y upgrade

RUN dnf -y install epel-release 'dnf-command(copr)'
RUN dnf -y copr enable kwetlesen/libmdbx

WORKDIR /root/build
COPY . .

CMD [ "/root/build/buildrpm.sh", "--buildvarsfile", "/root/build/builds.txt", "erigon2.spec" ]
