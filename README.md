# Erigon2 RPM Spec

This repository houses an RPM spec file for building Erigon2, a very fast
Ethereum peer-to-peer client written in GoLang. Erigon2 is based on Erigon with
the principal difference that Erigon2 is set up to function with the beacon
chain in preparation for the forthcoming Ethereum proof-of-stake fork.

See the [Erigon repo](https://github.com/ledgerwatch/erigon) for more information.

This packaging of Erigon runs Erigon as its own service user, defaulting the
Erigon2 data directory into `/var/lib/erigon2`, a LSB typical directory.

Also included are a set of SystemD style unit specifications and a set of
default service port definitions to plug into FirewallD.

Configuration options are stored into `/etc/sysconfig/erigon2` and are
identical to the command line configuration options that one would typically
use to start Erigon2.

[![Copr build status](https://copr.fedorainfracloud.org/coprs/kwetlesen/Erigon/package/erigon2/status_image/last_build.png)](https://copr.fedorainfracloud.org/coprs/kwetlesen/Erigon/package/erigon2/)
