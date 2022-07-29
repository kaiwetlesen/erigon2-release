# Disable the debug package as we don't provide it:
%global debug_package %{nil}
# TODO: rig up debug package support with golang.

# Upstream, the repo and makefile targets are still called erigon, go account
# for that:
%global original_name erigon

# The following conditional determine which version of Erigon we're building. They
# may be overrode by invoking rpmbuild with -D 'macroname "macro value here"'.

# Erigon version, buildable branch, & commit hash:
%define spec_pkgver %{?pkgver}%{!?pkgver:2022.07.02}
%define spec_commit %{?commit}%{!?commit:c7a94eeea05d7c0d569c811399642a7d108d8c82}
%define spec_branch %{?branch}%{!?branch:%{original_name}-v%{spec_pkgver}}
# Supplementary files version:
%define spec_suppl_ver %{?suppl_ver}%{!?suppl_ver:0.0.2}
%define spec_go_ver %{?go_ver}%{!?go_ver:1.18.3}

Name:           erigon2
Vendor:         Ledgerwatch
Version:        %{spec_pkgver}
Release:        0%{?dist}
Summary:        A very efficient next-generation Ethereum execution client
License:        LGPLv3
URL:            https://github.com/ledgerwatch/erigon

# File sources:
Source0:        https://github.com/%{vendor}/%{original_name}/archive/refs/tags/v%{version}.tar.gz
Source1:        https://github.com/kaiwetlesen/%{name}-release/archive/refs/tags/v%{spec_suppl_ver}.tar.gz

BuildRequires: libmdbx-devel, binutils, git, curl
#BuildRequires: golang >= 1.16
%if "%{dist}" == ".el8"
BuildRequires: gcc-toolset-10-gcc
BuildRequires: gcc-toolset-10-gcc-c++
%else
BuildRequires: gcc >= 10
BuildRequires: gcc-c++ >= 10
%endif

%description
An implementation of Ethereum (aka "Ethereum execution client"), on the
efficiency frontier, written in Go, compatible with the proof-of-stake merge.


%prep
# Build fails with GCC Go, so die unless we can set that alternative:
%autosetup -b 1 -n %{name}-release-%{spec_suppl_ver}
%autosetup -b 0 -n %{original_name}-%{version}
# Apply git attributes to release code:
git clone --bare --depth 1 -b v%{version} https://github.com/%{vendor}/%{original_name}.git .git
git init
git checkout -f -b %{spec_branch} tags/v%{version}

# Clone these two guys into the Erigon code:
#git clone https://github.com/ledgerwatch/erigon-snapshot.git turbo/snapshotsync/snapshothashes/erigon-snapshots
#git clone https://github.com/ngosang/trackerslist.git cmd/downloader/trackers/trackerslist
#sed -e 's/-buildvcs=false//g' Makefile > Makefile.new && mv -f Makefile.new Makefile


%build
if [ -f /opt/rh/gcc-toolset-10/enable ]; then
    . /opt/rh/gcc-toolset-10/enable
    echo "Enabled GCC toolchain v10 for RedHat systems"
fi
export mach=$(uname -m | tr '[A-Z]' '[a-z]')
echo "Detected machine architecture ${mach}"
# Map a few choice platforms:
if [ "${mach}" == 'x86_64' ]; then
    mach='amd64'
elif [ "${mach}" == 'i386' ] || [ "${mach}" == 'i686' ]; then
    mach='386'
elif [ "${mach}" == 'aarch64' ]; then
	mach='arm64'
else
	no_tx='notx'
fi
if ! [ "$no_tx" = 'notx' ]; then
	echo "Translated seen machine architecture to ${mach}"
fi
echo "Installing Go v%{spec_go_ver} into ${PWD}/go for the ${mach} platform"
curl -sL https://go.dev/dl/go%{spec_go_ver}.linux-${mach}.tar.gz | tar -C ${PWD} -xz
export GOPATH="${PWD}/go"
export PATH="${GOPATH}/bin:${PATH}"
go install github.com/cpuguy83/go-md2man@latest
export GIT_BRANCH="%{spec_branch}"
export GIT_COMMIT="%{spec_commit}"
export GIT_TAG="v%{version}"
cd %{_builddir}/%{original_name}-%{version}
make %{original_name} rpcdaemon integration sentry txpool hack pics
echo '# "%{name}" 1 "%{summary}" %{vendor} "User Manuals"' > %{name}.1.md
cat %{name}.1.md README.md | go-md2man > %{name}.1
%{__gzip} %{name}.1
%{__rm} %{name}.1.md
# Rename binaries with common names to [name]-[binary] scheme:
cd build/bin
mv %{original_name} %{name}
for binary in *; do
    %{__strip} --strip-debug --strip-unneeded ${binary}
    if echo $binary | grep -qv '^%{name}'; then
        %{__mv} ${binary} %{name}-${binary}
    fi
done
chmod -R ug+w ${GOPATH}
rm -rf ${GOPATH}
cd -


%install
%define build_srcdir  %{_builddir}/%{original_name}-%{version}
%define suppl_srcdir   %{_builddir}/%{name}-release-%{spec_suppl_ver}
%{__install} -m 0755 -D -s   %{build_srcdir}/build/bin/*       -t %{buildroot}%{_bindir}
%{__install} -m 0644 -D      %{build_srcdir}/README.md         -t %{buildroot}%{_datadir}/doc/%{name}
%{__install} -m 0644 -D      %{build_srcdir}/TESTING.md        -t %{buildroot}%{_datadir}/doc/%{name}
%{__install} -m 0644 -D      %{build_srcdir}/COPYING*          -t %{buildroot}%{_datadir}/licenses/%{name}
%{__install} -m 0644 -D      %{build_srcdir}/AUTHORS           -t %{buildroot}%{_datadir}/licenses/%{name}
%{__install} -m 0644 -D      %{build_srcdir}/%{name}.1.gz      -t %{buildroot}%{_mandir}/man1
%{__install} -m 0644 -D      %{suppl_srcdir}/units/*.service    -t %{buildroot}%{_prefix}/lib/systemd/system
%{__install} -m 0644 -D      %{suppl_srcdir}/firewallsvcs/*.xml -t %{buildroot}%{_prefix}/lib/firewalld/services
%{__install} -m 0644 -D      %{suppl_srcdir}/sysconfig/%{name}  -T %{buildroot}%{_sysconfdir}/sysconfig/%{name}


%files
%license COPYING COPYING.LESSER AUTHORS
%doc README.md TESTING.md
%{_bindir}/*
%{_mandir}/man1/%{name}.1.gz
%{_prefix}/lib/systemd/system/*
%{_prefix}/lib/firewalld/services/*
%config(noreplace) %{_sysconfdir}/sysconfig/%{name}


%pre
if ! getent group %{name} &> /dev/null; then
    groupadd -r %{name}
fi
if ! getent passwd %{name} &> /dev/null; then
    useradd -r -g %{name} -m -d %{_sharedstatedir}/%{name} -k /dev/null %{name}
fi


%changelog
* Tue Jul 12 2022 Kai Wetlesen <kaiw@semiotic.ai> - 2022.07.02-0%{?dist}
- Major revamp of build specification
- GoLang now must be pulled independently due to lack of available v1.19 in RL8
- Renamed all services from Erigon to Erigon2
- Bumped build version to v2022.07.02
* Tue May 3 2022 Kai Wetlesen <kaiw@semiotic.ai> - 2022.04.03-0%{?dist}
- First Erigon2 RPM release
