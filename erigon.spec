Name:           erigon
Vendor:			Ledgerwatch
Version:        2022.01.02
Release:        beta%{?dist}
Summary:        The Erigon Ethereum Client
Source0:		%{_sourcedir}/%{name}-%{version}-%{release}.tar.gz

License:        LGPL-3.0
URL:            https://github.com/ledgerwatch/erigon

BuildRequires: gcc >= 10
BuildRequires: gcc-c++ >= 10
BuildRequires: git
BuildRequires: gzip
BuildRequires: systemd-rpm-macros
BuildRequires: rubygem-ronn-ng
BuildRequires: golang >= 1.16

%define giturl https://github.com/
%define repourl %{giturl}%{vendor}/%{name}.git
%define NVR %{name}-%{version}-%{release}
%define trash_old_clone no

%description
Erigon is an implementation of Ethereum (aka "Ethereum client"), on the efficiency frontier, written in Go.

%prep
# Build fails with GCC Go, so die unless we can set that alternative:
GOVER=$(alternatives --list | awk '/^go\s/{print $3}' | grep -v gcc)
if [ -z "$GOVER" ]; then
	echo 'Cannot build with GCC-Go! Run "alternatives --config go" and select the official Go binary before rerunning this build!'
	exit -1
fi
# Start as many jobs as we have actual CPU cores
N_JOBS=$(lscpu -p | grep -v '^#' | cut -d, -f2 | sort -u | wc -l)
rm -rf %{NVR}
echo 'Grabbing source to %{NVR}'
git clone --recurse-submodules -j$N_JOBS %{repourl} %{NVR}
echo 'Refreshing tags and submodules...'
git -C %{NVR} pull --recurse-submodules
git -C %{NVR} fetch --all --tags --recurse-submodules
git -C %{NVR} submodule update --init --recursive --force
git -C %{NVR} checkout tags/v%{version} -b v%{version}
echo 'Building source archive with bundled submodules...'
# Git strips the NVR because we implicitly change the pwd, but we want to preserve it, thus this hinky business:
git -C %{NVR} ls-files --recurse-submodules | awk '!/\.git/{print "%{NVR}/"$0}' | tar -T - -czf %{_sourcedir}/%{NVR}.tar.gz

%build
# Start as many jobs as we have actual CPU cores
N_JOBS=$(lscpu -p | grep -v '^#' | cut -d, -f2 | sort -u | wc -l)
cd %{NVR}
make -j$N_JOBS %{name} rpcdaemon integration sentry txpool downloader hack db-tools
ln README.md %{name}.1.md
ronn -r --manual %{Summary} --organization %{Vendor} %{name}.1.md
gzip %{name}.1
rm %{name}.1.md
# Rename binaries with common names to %{name}_{binary} scheme:
cd build/bin
for file in hack integration mdbx_* rpcdaemon downloader sentry txpool; do
	mv $file %{name}_$file
done
cd -


%install
install -m 0755 -D -s %{_builddir}/%{NVR}/build/bin/* -t %{buildroot}%{_bindir}
install -m 0644 -D %{_builddir}/%{NVR}/README.md -t %{buildroot}%{_datadir}/doc/%{name}
install -m 0644 -D %{_builddir}/%{NVR}/TESTING.md -t %{buildroot}%{_datadir}/doc/%{name}
install -m 0644 -D %{_builddir}/%{NVR}/COPYING* -t %{buildroot}%{_datadir}/licenses/%{name}
install -m 0644 -D %{_builddir}/%{NVR}/AUTHORS -t %{buildroot}%{_datadir}/licenses/%{name}
install -m 0644 -D %{_builddir}/%{NVR}/%{name}.1.gz -t %{buildroot}%{_mandir}/man1


%files
%{_bindir}/%{name}
%{_bindir}/%{name}_hack
%{_bindir}/%{name}_integration
%{_bindir}/%{name}_mdbx_chk
%{_bindir}/%{name}_mdbx_copy
%{_bindir}/%{name}_mdbx_drop
%{_bindir}/%{name}_mdbx_dump
%{_bindir}/%{name}_mdbx_load
%{_bindir}/%{name}_mdbx_stat
%{_bindir}/%{name}_rpcdaemon
%{_bindir}/%{name}_downloader
%{_bindir}/%{name}_sentry
%{_bindir}/%{name}_txpool
%{_datarootdir}/licenses/%{name}/AUTHORS
%{_mandir}/man1/%{name}.1.gz
%license %{NVR}/COPYING %{NVR}/COPYING.LESSER
%doc %{NVR}/README.md %{NVR}/TESTING.md


%pre
if ! getent group %{name} &> /dev/null; then
	groupadd -r %{name}
fi
if getent passwd %{name} &> /dev/null; then
	mkdir -p %{_sharedstatedir}/%{name}
	chown -R %{name}:%{name} %{_sharedstatedir}/%{name}
else
	useradd -r -m -d %{_sharedstatedir}/%{name} -k /dev/null %{name}
fi


%changelog
* Tue Jan 25 2022 Kai Wetlesen <kaiw@semiotic.ai> - 2022.01.02 (beta)
- First Erigon RPM release
