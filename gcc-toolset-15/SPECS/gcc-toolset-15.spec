%global __python /usr/bin/python3
%global gts_ver 15
%global scl gcc-toolset-%{gts_ver}
%global scl_prefix gcc-toolset-%{gts_ver}-
%global scl_name %scl

# We moved away from scl-utils in RHEL10. Instead, we have bundled in the
# minimal macro hackery necessary to build GTS into the same root to give us
# the necessary isolation and allow an equivalent of `scl enable` since that's
# a common way to use GTS.
#
# Some day we will move away from the 'scl' names, but today is not that day.
%global have_scl_utils 1

# GTS only has gcc and binutils in RHEL9 and later.
%global gts_only_gcc_binutils 1

%if %have_scl_utils
%global long_name %scl Software Collection
%global version_string GCC-Toolset %{gts_ver} Software Collection
BuildRequires: scl-utils-build
%else
%global long_name GCC Toolset %gts_ver
%global version_string GCC-Toolset %{gts_ver}
%include %{_sourcedir}/macros.gts
%endif
%{?scl_package:%scl_package %scl}

Summary: Package that installs %scl
Name: %scl_name
Version: %{gts_ver}.0
Release: 11%{?dist}
License: GPLv2+
Group: Applications/File
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
Source0: README
Source2: gts-annobin-plugin-select.sh
Source3: macros.gts
Source4: enable.in
Source5: gcc-toolset-env.in

Requires: %{scl_prefix}runtime == %{version}-%{release}
Requires: %{scl_prefix}gcc %{scl_prefix}gcc-c++ %{scl_prefix}gcc-gfortran
Requires: %{scl_prefix}binutils
# None of these are in GTS in RHEL9 and later.
%if %gts_only_gcc_binutils == 0
Requires: %{scl_prefix}gdb
Requires: %{scl_prefix}dwz
Requires: %{scl_prefix}annobin-plugin-gcc
%endif
Obsoletes: %{name} < %{version}-%{release}
Obsoletes: %{scl_prefix}dockerfiles < %{version}-%{release}

BuildRequires: iso-codes
BuildRequires: help2man
BuildRequires: python3-devel

%if %gts_only_gcc_binutils == 0
%global rrcdir %{_scl_root}/usr/lib/rpm/redhat
%endif

%description
This is the main package for %long_name.

%package runtime
Summary: Package that handles %long_name.
Group: Applications/File
Obsoletes: %{name}-runtime < %{version}-%{release}
%if %have_scl_utils
Requires: scl-utils >= 20120927-11
%{?scl_package:Requires(post): %{_root_sbindir}/semanage %{_root_sbindir}/restorecon}
%{?scl_package:Requires(postun): %{_root_sbindir}/semanage %{_root_sbindir}/restorecon}
#Requires(post): libselinux policycoreutils-python
#Requires(postun): libselinux policycoreutils-python
%endif

%description runtime
Package shipping essential scripts to work with %long_name.

%if %have_scl_utils == 0
%package devel
Summary: Scripts needed to build %long_name.
Group: Applications/File
Conflicts: scl-utils-build

%description devel
Package shipping scripts to build %long_name.
%endif

%prep
%setup -c -T

# This section generates README file from a template and creates man page
# from that file, expanding RPM macros in the template file.
cat <<'EOF' | tee README
%{expand:%(cat %{SOURCE0})}
EOF

%build

# Temporary helper script used by help2man.
cat <<\EOF | tee h2m_helper
#!/bin/sh
if [ "$1" = "--version" ]; then
  printf '%%s' "%{version_string}"
else
  cat README
fi
EOF
chmod a+x h2m_helper
# Generate the man page.
help2man -n "GNU project C, C++ and Fortran compiler and linker" -N --section 7 ./h2m_helper -o %{?scl_name}.7
gzip %{?scl_name}.7

# Enable collection script
# ========================
cat <<'EOF' | tee enable
%{expand:%(cat %{SOURCE4})}
EOF

%if %have_scl_utils == 0
cat <<'EOF' | tee gcc-toolset-%{gts_ver}-env
%{expand:%(cat %{SOURCE5})}
EOF
%endif

%install

%if %have_scl_utils
(%{scl_install})

# We no longer need this, and it would result in an "unpackaged but
# installed" error.
rm -rf %{buildroot}%{_root_sysconfdir}/rpm/macros.%{scl}-config
%else
mkdir -p %{buildroot}%{_root_sysconfdir}/rpm

# RPM macro weirdness: when it's explicitly included like in this spec file, it
# expects the %%define but when it is installed as a macro file, it cannot
# handle the %%define and instead expects %%<macro name> directly.
sed 's/^%%define scl_/%%scl_/' %{SOURCE3} > %{buildroot}%{_root_sysconfdir}/rpm/macros.%{scl}-build
%endif

%if %have_scl_utils
%define source_cmd source scl_source enable %{scl}
%else
%define source_cmd source %{_root_prefix}/lib/gcc-toolset/%{gts_ver}-env.source
%endif

# This allows users to build packages using DTS/GTS.
cat >> %{buildroot}%{_root_sysconfdir}/rpm/macros.%{scl}-enable << EOF
%%enable_gcctoolset%{gts_ver} %%global ___build_pre %%{___build_pre}; %source_cmd || :
EOF

%if %have_scl_utils
# Without SCL we just let gcc-toolset-*-binutils own this and use the
# --altdir/--admindir mechanism.
mkdir -p %{buildroot}%{_scl_root}/etc/alternatives %{buildroot}%{_scl_root}/var/lib/alternatives

install -d -m 755 %{buildroot}%{_scl_scripts}
install -p -m 755 enable %{buildroot}%{_scl_scripts}/

%if %gts_only_gcc_binutils == 0
# Other directories that should be owned by the runtime
install -d -m 755 %{buildroot}%{_datadir}/appdata
# Otherwise unowned perl directories
install -d -m 755 %{buildroot}%{_libdir}/perl5
install -d -m 755 %{buildroot}%{_libdir}/perl5/vendor_perl
install -d -m 755 %{buildroot}%{_libdir}/perl5/vendor_perl/auto

# Install the plugin selector trigger script.
mkdir -p %{buildroot}%{rrcdir}
install -p -m 755 %{SOURCE2} %{buildroot}%{rrcdir}/
%endif
%else
install -d -m 755 %{buildroot}%{_root_bindir}
install -p -m 755 gcc-toolset-%{gts_ver}-env %{buildroot}%{_root_bindir}/
install -d -m 755 %{buildroot}%{_root_prefix}/lib/gcc-toolset
install -p -m 755 enable %{buildroot}%{_root_prefix}/lib/gcc-toolset/%{gts_ver}-env.source
%endif

# Install generated man page.
install -d -m 755 %{buildroot}%{_root_mandir}/man7
install -p -m 644 %{?scl_name}.7.gz %{buildroot}%{_root_mandir}/man7/
%if %have_scl_utils == 0
pushd %{buildroot}%{_root_mandir}/man7/
ln -s ./%{?scl_name}.7.gz gcc-toolset-%{gts_ver}-env.7.gz
popd
%endif

# This trigger is used to decide which version of the annobin plugin for gcc
# should be used.  See comments in the script for full details.

%if %gts_only_gcc_binutils == 0
%triggerin runtime -- %{scl_prefix}annobin-plugin-gcc %{scl_prefix}gcc-plugin-annobin
%{rrcdir}/gts-annobin-plugin-select.sh %{_scl_root}
%end

# We also trigger when annobin is uninstalled.  This allows us to switch
# over to the gcc generated version of the plugin.  It does not matter if
# gcc is uninstalled, since if that happens the plugin cannot be used.

%triggerpostun runtime -- %{scl_prefix}annobin-plugin-gcc
%{rrcdir}/gts-annobin-plugin-select.sh %{_scl_root}
%end
%endif

%files
%doc README
%if %have_scl_utils
%{_root_mandir}/man7/%{?scl_name}.*
%endif

%files runtime
%{_root_sysconfdir}/rpm/macros.%{scl}-enable
%if %have_scl_utils
%if %gts_only_gcc_binutils == 0
%attr(0755,-,-) %{rrcdir}/gts-annobin-plugin-select.sh
%dir %{_datadir}/appdata
%endif
%scl_files
%attr(0644,root,root) %verify(not md5 size mtime) %ghost %config(missingok,noreplace) %{_sysconfdir}/selinux-equiv.created
%dir %{_scl_root}/etc/alternatives
%else
%{_root_mandir}/man7/%{?scl_name}.*
%{_root_mandir}/man7/gcc-toolset-%{gts_ver}-env.*
%{_root_bindir}/gcc-toolset-%{gts_ver}-env
%{_root_prefix}/lib/gcc-toolset/%{gts_ver}-env.source
%endif

%if %have_scl_utils
%post runtime
if [ ! -f %{_sysconfdir}/selinux-equiv.created ]; then
  /usr/sbin/semanage fcontext -a -e / %{_scl_root}
  restorecon -R %{_scl_root}
  touch %{_sysconfdir}/selinux-equiv.created
fi

%preun runtime
[ $1 = 0 ] && rm -f %{_sysconfdir}/selinux-equiv.created || :

%postun runtime
if [ $1 = 0 ]; then
  /usr/sbin/semanage fcontext -d %{_scl_root}
  [ -d %{_scl_root} ] && restorecon -R %{_scl_root} || :
fi
%endif

%if %have_scl_utils == 0
%files devel
%{_root_sysconfdir}/rpm/macros.%{scl}-build
%endif

%changelog
* Fri Jun 20 2025 Siddhesh Poyarekar <siddhesh@redhat.com> - 15.0-9
- Compress man page and fix its name (RHEL-98731)

* Tue Jun 10 2025 Siddhesh Poyarekar <siddhesh@redhat.com> - 15.0-7
- Man page and documentation updates (RHEL-96025)

* Thu Jun  5 2025 Siddhesh Poyarekar <siddhesh@redhat.com> - 15.0-6
- Split out scripts into a -runtime package on RHEL10 (RHEL-94841)

* Tue May 20 2025 Siddhesh Poyarekar <siddhesh@redhat.com> - 15.0-4
- New script to replace scl-enable (RHEL-91829).

* Thu May  8 2025 Siddhesh Poyarekar <siddhesh@redhat.com> - 15.0-3
- Drop the sudo wrapper script.

* Mon May  5 2025 Siddhesh Poyarekar <siddhesh@redhat.com> - 15.0-2
- Split out a devel package to break the dependency look with gts-gcc and
  gts-binutils.

* Mon May  5 2025 Siddhesh Poyarekar <siddhesh@redhat.com> - 15.0-1
- Drop scl-utils dependency on c10s and later.

* Mon Apr 14 2025 Marek Polacek <polacek@redhat.com> - 15.0-0
- new package (RHELPLAN-171604)
