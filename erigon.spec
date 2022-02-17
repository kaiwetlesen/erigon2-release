# Global macros:
# Disable the debug package as we don't provide it:
%global debug_package %{nil}
# TODO: rig up debug package support with golang.

# The following conditional determine which version of Erigon we're building. They
# may be overrode by invoking rpmbuild with -D 'macroname "macro value here"'.

# Erigon version, buildable branch, & commit hash:
%{!?erigon_ver: %global erigon_ver  2022.01.02}
%{!?branch:     %global branch      stable}
%{!?commit:     %global commit      d8b0992a01881101818a9bf316850fef1891bb5f}
# Supplementary files version:
%{!?suppl_ver:  %global suppl_ver   0.0.1-alpha}

Name:           erigon
Vendor:         Ledgerwatch
Version:        %{erigon_ver}
Release:        beta%{?dist}
Summary:        The Erigon Ethereum Client
License:        LGPL-3.0
URL:            https://github.com/ledgerwatch/erigon

Requires:       libmdbx

# Computed macros:
# These depend on a combination of the flags and other macros.

# File sources:
Source0:        https://github.com/%{vendor}/%{name}/archive/refs/tags/v%{version}.tar.gz
Source1:        https://github.com/kaiwetlesen/%{name}-release/archive/refs/tags/v%{suppl_ver}.tar.gz

# Note: ruby and ruby-devel are needed to setup ronn, the markdown to manpage compiler
BuildRequires: systemd-rpm-macros, ruby, ruby-devel, libmdbx-devel, binutils
BuildRequires: golang >= 1.16
%if "%{dist}" == ".el8"
BuildRequires: gcc-toolset-10-gcc
BuildRequires: gcc-toolset-10-gcc-c++
%else
BuildRequires: gcc >= 10
BuildRequires: gcc-c++ >= 10
%endif

%description
Erigon is an implementation of Ethereum (aka "Ethereum client"), on the efficiency frontier, written in Go.

%prep
# Build fails with GCC Go, so die unless we can set that alternative:
if go version | grep -i gcc; then
    echo 'Cannot build with GCC-Go! Run "alternatives --config go" and select the official Go binary or remove GCC-Go before rerunning this build!'
    exit -1
fi
#gem install ronn
gem install md2man
%autosetup -b 0
%autosetup -b 1

%build
%if "%{dist}" == ".el8"
    . /opt/rh/gcc-toolset-10/enable
%endif
export GIT_BRANCH="%{branch}"
export GIT_COMMIT="%{commit}"
export GIT_TAG="v%{version}"
# Start as many jobs as we have actual CPU cores
make %{name} rpcdaemon integration sentry txpool hack pics
echo '# "%{name}" 1 "%{summary}" %{vendor} "User Manuals"' > erigon.1.md
sed -i 's/[\d128-\d255]//g' README.md >> erigon.1.md
md2man-roff erigon.1.md > erigon.1
%{__gzip} %{name}.1
%{__rm} %{name}.1.md
# Rename binaries with common names to %{name}_{binary} scheme:
mkdir -p build/debuginfo
cd build/bin
# This is done in two separate loops to prevent nondeterministic wildcard evaluation:
for binary in *; do
    %{__strip} --strip-debug --strip-unneeded ${binary}
    if echo $binary | grep -qv '^%{name}'; then
        %{__mv} ${binary} %{name}_${binary}
    fi
done
cd -


%install
%define erigon_srcdir  %{_builddir}/%{name}-%{version}
%define suppl_srcdir   %{_builddir}/%{name}-release-%{suppl_ver}
%{__install} -m 0755 -D -s   %{erigon_srcdir}/build/bin/*   -t %{buildroot}%{_bindir}
%{__install} -m 0644 -D      %{erigon_srcdir}/README.md     -t %{buildroot}%{_datadir}/doc/%{name}
%{__install} -m 0644 -D      %{erigon_srcdir}/TESTING.md    -t %{buildroot}%{_datadir}/doc/%{name}
%{__install} -m 0644 -D      %{erigon_srcdir}/COPYING*      -t %{buildroot}%{_datadir}/licenses/%{name}
%{__install} -m 0644 -D      %{erigon_srcdir}/AUTHORS       -t %{buildroot}%{_datadir}/licenses/%{name}
%{__install} -m 0644 -D      %{erigon_srcdir}/%{name}.1.gz  -t %{buildroot}%{_mandir}/man1
%{__install} -m 0644 -D      %{suppl_srcdir}/*.service      -t %{buildroot}%{_prefix}/lib/systemd/system
%{__install} -m 0644 -D      %{suppl_srcdir}/%{name}_opts   -T %{buildroot}%{_sysconfdir}/sysconfig/%{name}


%files
%license COPYING COPYING.LESSER AUTHORS
%doc README.md TESTING.md
%{_bindir}/*
%{_mandir}/man1/%{name}.1.gz
%{_prefix}/lib/systemd/system/*
%{_sysconfdir}/sysconfig/%{name}


%pre
if ! getent group %{name} &> /dev/null; then
    groupadd -r %{name}
fi
if getent passwd %{name} &> /dev/null; then
    mkdir -p %{_sharedstatedir}/%{name}
    chown -R %{name}:%{name} %{_sharedstatedir}/%{name}
else
    useradd -r -g %{name} -m -d %{_sharedstatedir}/%{name} -k /dev/null %{name}
fi


%changelog
* Tue Jan 25 2022 Kai Wetlesen <kaiw@semiotic.ai> - 2022.01.02 (beta)
- First Erigon RPM release
