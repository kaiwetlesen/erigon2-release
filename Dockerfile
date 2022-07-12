FROM rockylinux

WORKDIR /root

RUN dnf -y install epel-release dnf-plugins-core rpmdevtools 'dnf-command(copr)'
RUN dnf -y copr enable kwetlesen/libmdbx
RUN rpmdev-setuptree
RUN dnf -y upgrade

COPY ./buildrpm.sh /root/buildrpm.sh
COPY ./erigon2.spec /root/erigon2.spec
RUN dnf -y builddep /root/erigon2.spec

#CMD [ "/bin/bash", "/root/buildrpm.sh", "/root/erigon2.spec" ]
CMD [ "/bin/bash" ]
