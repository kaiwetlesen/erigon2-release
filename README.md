# Erigon RPM Spec

This repository houses an RPM spec file for building Erigon, a
very fast Ethereum peer-to-peer client written in GoLang.

See the [Erigon repo](https://github.com/ledgerwatch/erigon) for more information.


## About This Package

This packaging of Erigon runs Erigon as its own service user, defaulting
the Erigon data directory into `/var/lib/erigon`, a LSB typical directory.

Also included are a set of SystemD style unit specifications and
a set of default service port definitions to plug into FirewallD.

Configuration options are stored into `/etc/sysconfig/erigon` and
are identical to the command line configuration options that one
would typically use to start Erigon.

[![Copr build status](https://copr.fedorainfracloud.org/coprs/kwetlesen/Erigon/package/erigon/status_image/last_build.png)](https://copr.fedorainfracloud.org/coprs/kwetlesen/Erigon/package/erigon/)


## RHELesque Install Instructions

### From Published COPR RPMs

It's super simple! Just:

1. `dnf install dnf-plugins-core`
2. `dnf copr enable kwetlesen/Erigon`
3. `dnf install erigon`

You're done!

### From Your Own RPMs

Okay, so you do not trust COPR hosted RPMs. That's okay! Once you've built
RPMs for your system (and signed them with your key) simply use DNF to install:

- dnf install ./erigon-{version}.{arch}.
