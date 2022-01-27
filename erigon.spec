Name:           erigon
vendor:			Ledgerwatch
Version:        2022.01.02
Release:        beta%{?dist}
Summary:        Ethereum implementation on the efficiency frontier
Source0:		%{_sourcedir}/%{name}-%{version}-%{release}.tar.gz

License:        LGPL-3.0
URL:            https://github.com/ledgerwatch/erigon

BuildRequires:  gcc, gcc-c++, git, gzip, systemd-rpm-macros, rubygem-ronn-ng
#, golang

%define giturl https://github.com/
%define repourl %{giturl}%{vendor}/%{name}.git
%define NVR %{name}-%{version}-%{release}
%define trash_old_clone no

%description
Erigon is an implementation of Ethereum (aka "Ethereum client"), on the efficiency frontier, written in Go.

%prep
# Start as many jobs as we have actual CPU cores
N_JOBS=$(lscpu -p | grep -v '^#' | cut -d, -f2 | sort -u | wc -l)
rm -rf %{NVR}
echo 'Grabbing source to %{NVR}'
git clone --recurse-submodules -j$N_JOBS %{repourl} %{NVR}
echo 'Refreshing tags and submodules...'
git -C %{NVR} pull --recurse-submodules
git -C %{NVR} fetch --all --tags --recurse-submodules
git -C %{NVR} submodule update --init --recursive --force
echo 'Building source archive with bundled submodules...'
# Git strips the NVR because we implicitly change the pwd, but we want to preserve it, thus this hinky business:
git -C %{NVR} ls-files --recurse-submodules | awk '!/\.git/{print "%{NVR}/"$0}' | tar -T - -czf %{_sourcedir}/%{NVR}.tar.gz

%build
# Start as many jobs as we have actual CPU cores
N_JOBS=$(lscpu -p | grep -v '^#' | cut -d, -f2 | sort -u | wc -l)
cd %{NVR}
make -j$N_JOBS erigon rpcdaemon integration sentry txpool downloader hack db-tools
ln README.md erigon.1.md
ronn -r --manual 'The Erigon Ethereum Client' --organization Ledgerwatch erigon.1.md
gzip erigon.1
rm erigon.1.md


%install
install -m 0755 -D -s %{_builddir}/%{NVR}/build/bin/* -t %{buildroot}/usr/bin
install -m 0644 -D %{_builddir}/%{NVR}/README.md -t %{buildroot}/usr/share/doc/erigon
install -m 0644 -D %{_builddir}/%{NVR}/TESTING.md -t %{buildroot}/usr/share/doc/erigon
install -m 0644 -D %{_builddir}/%{NVR}/COPYING* -t %{buildroot}/usr/share/licenses/erigon
install -m 0644 -D %{_builddir}/%{NVR}/AUTHORS -t %{buildroot}/usr/share/licenses/erigon
install -m 0644 -D %{_builddir}/%{NVR}/erigon.1.gz -t %{buildroot}//usr/share/man/man1


%files
/usr/bin/erigon
/usr/bin/hack
/usr/bin/integration
/usr/bin/mdbx_chk
/usr/bin/mdbx_copy
/usr/bin/mdbx_drop
/usr/bin/mdbx_dump
/usr/bin/mdbx_load
/usr/bin/mdbx_stat
/usr/bin/pics
/usr/bin/rpcdaemon
/usr/bin/rpctest
/usr/bin/sentry
/usr/bin/state
/usr/bin/txpool
/usr/share/licenses/erigon/AUTHORS
/usr/share/man/man1/erigon.1.gz
%license COPYING COPYING.LESSER
%doc README.md TESTING.md


%changelog
* Tue Jan 25 2022 Kai Wetlesen <kaiw@semiotic.ai> - 2022.01.02 (beta)
- First Erigon RPM release
