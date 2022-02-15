Name:           erigon
Vendor:			Ledgerwatch
Version:        2022.01.02
Release:        beta%{?dist}
Summary:        The Erigon Ethereum Client
Source0:        https://github.com/%{vendor}/%{name}/archive/refs/tags/v%{version}.tar.gz

License:        LGPL-3.0
URL:            https://github.com/ledgerwatch/erigon

Requires:       libmdbx

BuildRequires: systemd-rpm-macros, rubygem-ronn-ng, libmdbx-devel
BuildRequires: golang >= 1.16
%if "%{dist}" == ".el8"
BuildRequires: gcc-toolset-10-gcc
BuildRequires: gcc-toolset-10-gcc-c++
%else
BuildRequires: gcc >= 10
BuildRequires: gcc-c++ >= 10
%endif

%define giturl https://github.com/
%define repourl %{giturl}%{vendor}/%{name}.git
%define NVR %{name}-%{version}-%{release}
%define trash_old_clone no

%description
Erigon is an implementation of Ethereum (aka "Ethereum client"), on the efficiency frontier, written in Go.

%prep
# Build fails with GCC Go, so die unless we can set that alternative:
if go version | grep -i gcc; then
	echo 'Cannot build with GCC-Go! Run "alternatives --config go" and select the official Go binary or remove GCC-Go before rerunning this build!'
	exit -1
fi
%autosetup

%build
%if "%{dist}" == ".el8"
    . /opt/rh/gcc-toolset-10/enable
%endif
# Start as many jobs as we have actual CPU cores
make %{name} rpcdaemon integration sentry txpool hack pics
%{__mv} README.md %{name}.1.md
ronn -r --manual %{Summary} --organization %{Vendor} %{name}.1.md
%{__gzip} %{name}.1
%{__rm} %{name}.1.md
# Rename binaries with common names to %{name}_{binary} scheme:
cd build/bin
for binary in *; do
    if echo $binary | grep -q '^%{name}'; then
	    %{__mv} ${binary} %{name}_${binary}
    fi
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
#%{_bindir}/%{name}
#%{_bindir}/%{name}_hack
#%{_bindir}/%{name}_integration
#%{_bindir}/%{name}_rpcdaemon
#%{_bindir}/%{name}_downloader
#%{_bindir}/%{name}_sentry
#%{_bindir}/%{name}_txpool
%license COPYING COPYING.LESSER AUTHORS
%doc README.md TESTING.md
%{_bindir}/*
%{_mandir}/man1/%{name}.1.gz
%{_prefix}/lib/systemd/system/*


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
