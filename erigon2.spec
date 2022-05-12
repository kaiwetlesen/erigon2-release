# Disable the debug package as we don't provide it:
%global debug_package %{nil}
# TODO: rig up debug package support with golang.

# The following conditional determine which version of Erigon we're building. They
# may be overrode by invoking rpmbuild with -D 'macroname "macro value here"'.

# Erigon version, buildable branch, & commit hash:
%{!?erigon_ver: %global erigon_ver  2022.04.03}
%{!?branch:     %global branch      stable}
%{!?commit:     %global commit      d139c750cba2d9ce03e4677d6700b21246c6813f}
# Supplementary files version:
%{!?suppl_ver:  %global suppl_ver   0.0.1}

Name:           erigon2
Vendor:         Ledgerwatch
Version:        %{erigon_ver}
Release:        0%{?dist}
Summary:        A very efficient next-generation Ethereum client
License:        LGPLv3
URL:            https://github.com/ledgerwatch/erigon

# File sources:
Source0:        https://github.com/%{vendor}/%{name}/archive/refs/tags/v%{version}.tar.gz
Source1:        https://github.com/kaiwetlesen/%{name}-release/archive/refs/tags/v%{suppl_ver}.tar.gz

BuildRequires: libmdbx-devel, binutils, git, golang-github-cpuguy83-md2man
BuildRequires: golang >= 1.16
%if "%{dist}" == ".el8"
BuildRequires: gcc-toolset-10-gcc
BuildRequires: gcc-toolset-10-gcc-c++
%else
BuildRequires: gcc >= 10
BuildRequires: gcc-c++ >= 10
%endif

%description
An implementation of Ethereum (aka "Ethereum client"), on the efficiency
frontier, written in Go.


%prep
# Build fails with GCC Go, so die unless we can set that alternative:
if go version | grep -i gcc; then
    echo 'Cannot build with GCC-Go! Run "alternatives --config go" and select the official Go binary or remove GCC-Go before rerunning this build!'
    exit -1
fi
%autosetup -b 0
%autosetup -b 1


%build
%if "%{?rhel}" != ""
    . /opt/rh/gcc-toolset-10/enable
%endif
export GIT_BRANCH="%{branch}"
export GIT_COMMIT="%{commit}"
export GIT_TAG="v%{version}"
make %{name} rpcdaemon integration sentry txpool hack pics
echo '# "%{name}" 1 "%{summary}" %{vendor} "User Manuals"' > %{name}.1.md
cat %{name}.1.md README.md | go-md2man > %{name}.1
%{__gzip} %{name}.1
%{__rm} %{name}.1.md
# Rename binaries with common names to %{name}_{binary} scheme:
cd build/bin
for binary in *; do
    %{__strip} --strip-debug --strip-unneeded ${binary}
    if echo $binary | grep -qv '^%{name}'; then
        %{__mv} ${binary} %{name}-${binary}
    fi
done
cd -


%install
%define erigon_srcdir  %{_builddir}/%{name}-%{version}
%define suppl_srcdir   %{_builddir}/%{name}-release-%{suppl_ver}
%{__install} -m 0755 -D -s   %{erigon_srcdir}/build/bin/*       -t %{buildroot}%{_bindir}
%{__install} -m 0644 -D      %{erigon_srcdir}/README.md         -t %{buildroot}%{_datadir}/doc/%{name}
%{__install} -m 0644 -D      %{erigon_srcdir}/TESTING.md        -t %{buildroot}%{_datadir}/doc/%{name}
%{__install} -m 0644 -D      %{erigon_srcdir}/COPYING*          -t %{buildroot}%{_datadir}/licenses/%{name}
%{__install} -m 0644 -D      %{erigon_srcdir}/AUTHORS           -t %{buildroot}%{_datadir}/licenses/%{name}
%{__install} -m 0644 -D      %{erigon_srcdir}/%{name}.1.gz      -t %{buildroot}%{_mandir}/man1
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
* Tue May 3 2022 Kai Wetlesen <kaiw@semiotic.ai> - 2022.04.03-0%{?dist}
- First Erigon2 RPM release
