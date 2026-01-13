%{?scl_package:%global scl gcc-toolset-15}
%global scl_prefix gcc-toolset-15-
BuildRequires: scl-utils-build

%global __python /usr/bin/python3
%{?scl:%scl_package annobin}

Name:    %{?scl_prefix}annobin
Summary: Annotate and examine compiled binary files
Version: 12.93
Release: 4%{?dist}
License: GPL-3.0-or-later AND LGPL-2.0-or-later AND (GPL-2.0-or-later WITH GCC-exception-2.0) AND (LGPL-2.0-or-later WITH GCC-exception-2.0) AND GFDL-1.3-or-later
URL: https://sourceware.org/annobin/
# Maintainer: nickc@redhat.com
# Web Page: https://sourceware.org/annobin/
# Watermark Protocol: https://fedoraproject.org/wiki/Toolchain/Watermark

#---------------------------------------------------------------------------------

# Use "--without tests" to disable the testsuite.
%bcond_without tests

# Use "--without annocheck" to disable the installation of the annocheck program.
%bcond_without annocheck

# Use "--with debuginfod" to force support for debuginfod to be compiled into
# the annocheck program.  By default the configure script will check for
# availablilty at build time, but this might not match the run time situation.
# FIXME: Add a --without debuginfod option to forcefully disable the configure
# time check for debuginfod support.
%bcond_with debuginfod

# Use "--without clangplugin" to disable the building of the annobin plugin for Clang.
%bcond_without clangplugin

# Use "--without gccplugin" to disable the building of the annobin plugin for GCC.
%bcond_without gccplugin

# Use "--without llvmplugin" to disable the building of the annobin plugin for LLVM.
%bcond_without llvmplugin

# Set this to zero to disable the requirement for a specific version of gcc.
# This should only be needed if there is some kind of problem with the version
# checking logic or when building on RHEL-7 or earlier.
#
# Update: now that we have gcc version checking support in redhat-rpm-config
# there is no longer a great need for a hard gcc version check here.  Not
# enabling this check greatly simplifies the process of installing a new major
# version of gcc into the buildroot.
%global with_hard_gcc_version_requirement 0

%bcond_without plugin_rebuild
# Allow the building of annobin without using annobin itself.
# This is because if we are bootstrapping a new build environment we can have
# a new version of gcc installed, but without a new of annobin installed.
# (i.e. we are building the new version of annobin to go with the new version
# of gcc).  If the *old* annobin plugin is used whilst building this new
# version, the old plugin will complain that version of gcc for which it
# was built is different from the version of gcc that is now being used, and
# then it will abort.
#
# The default is to use plugin during rebuilds (cf BZ 1630550) but this can
# be changed because of the need to be able to rebuild annobin when a change
# to gcc breaks the version installed into the buildroot.  Note however that
# uncommenting the lines below will result in annocheck not passing the rpminspect
# tests....
# %%if %%{without plugin_rebuild}
# %%undefine _annotated_build
# %%endif

#---------------------------------------------------------------------------------

# Bootstrapping: Set this to 1 to build annobin with the system gcc.
# Then once GTS-gcc is built and in the buildroot, reset this variable
# to 0, bump the NVR and rebuild GTS-annobin.
%define bootstrapping 0
# # FIXME: Temporary - use this to get the annobin plugin into the buildroot.
%undefine _annotated_build

#---------------------------------------------------------------------------------

%global annobin_dir     annobin-%{version}
%global latest_sources  latest-annobin.tar.xz

Source: https://nickc.fedorapeople.org/%{annobin_dir}.tar.xz
# For the most recent sources use:  git clone git://sourceware.org/git/annobin.git

# Insert patches here, if needed.
Patch01: annobin-nop.patch
Patch02: annobin-tmp-default-to-using-group-attach.patch
%if %{bootstrapping}
Patch03: annobin-gcc-plugin-ignore-major-version-diffs.patch
%endif

# Workaround for a bug in /usr/include/locale.h:
#   /usr/include/locale.h:122:14: error: expected unqualified-id before 'const'
#   extern char *setlocale (int __category, const char *__locale) __THROW;
#   /usr/include/locale.h:122:14: error: expected ')' before 'const'
#   /opt/rh/gcc-toolset-15/root/usr/lib/gcc/aarch64-redhat-linux/15/plugin/include/intl.h:26:38: note: to match this '('
#   # define setlocale(category, locale) (locale)
Patch04: annobin-gcc-plugin-no-include-intl-h.patch

# FIXME: TEMPORARY: This patch changes the GCC plugin so that will call error()
# instead of warning() when generating warning messages.  This is because the
# prototype for warning() changes between GCC 14 and GCC 15.  So a plugin built
# by GCC 14 cannot be run by GCC 15.  Once gcc-toolset-15-gcc in the buildroot
# is at version 15, this patch should be discarded.
# For more details see RHEL-95704.
Patch05: annobin-GCC-PLUGIN-WARNING.patch

# This is where a copy of the sources will be installed.
%global annobin_source_dir %{?_scl_root}/%{_usrsrc}/annobin

%if %{bootstrapping}

BuildRequires: gcc gcc-c++

%define gcc_for_annobin /usr/bin/gcc
%define gxx_for_annobin /usr/bin/g++

%else

BuildRequires: %{?scl_prefix}gcc
BuildRequires: %{?scl_prefix}gcc-c++
BuildRequires: %{?scl_prefix}annobin-plugin-gcc
%{?scl:BuildRequires:%scl_runtime}

%{?scl:Requires:%scl_runtime}
# We need the gcc-toolset-N version of gcc in order to run annobin, as otherwise the versions will not match.
%{?scl:Requires:%scl_require_package %{scl} gcc}

%define gcc_for_annobin %{?_scl_root}/usr/bin/gcc
%define gxx_for_annobin %{?_scl_root}/usr/bin/g++

%endif

#---------------------------------------------------------------------------------

# Make sure that the necessary sub-packages are built.

%if %{with gccplugin}
Requires: %{name}-plugin-gcc
%endif

%if %{with llvmplugin}
Requires: %{name}-plugin-llvm
%endif

%if %{with clangplugin}
Requires: %{name}-plugin-clang
%endif

#---------------------------------------------------------------------------------

%description
This package contains the tools needed to annotate binary files created by
compilers, and also the tools needed to examine those annotations.

%if %{with gccplugin}
One of the tools is a plugin for GCC that records information about the
security options that were in effect when the binary was compiled.

Note - the plugin is automatically enabled in gcc builds via flags
provided by the redhat-rpm-macros package.
%endif

%if %{with clangplugin}
One of the tools is a plugin for Clang that records information about the
security options that were in effect when the binary was compiled.
%endif

%if %{with llvmplugin}
One of the tools is a plugin for LLVM that records information about the
security options that were in effect when the binary was compiled.
%endif

%if %{with annocheck}
One of the tools is a security checker which analyses the notes present in
annotated files and reports on any missing security options.
%endif

#---------------------------------------------------------------------------

# Now that we have sub-packages for all of the plugins and for annocheck,
# there are no executables left to go into the "annobin" rpm.  But top-level
# packages cannot have "BuildArch: noarch" if sub-packages do have
# architecture requirements, and rpmlint generates an error if an
# architecture specific rpm does not contain any binaries.  So instead all of
# the documentation has been moved into an architecture neutral sub-package,
# and there no longer is a top level annobin rpm at all.

%package docs
Summary: Documentation and shell scripts for use with annobin
BuildArch: noarch
# The documentation uses pod2man...
BuildRequires: perl-interpreter perl-podlators gawk make sharutils

%description docs
Provides the documentation files and example shell scripts for use with annobin.

#----------------------------------------------------------------------------
%if %{with tests}

%package tests
Summary: Test scripts and binaries for checking the behaviour and output of the annobin plugin

Requires: %{name}-docs = %{version}-%{release}
BuildRequires: make sharutils

%if %{with debuginfod}
BuildRequires: elfutils-debuginfod-client-devel
%endif

%description tests
Provides a means to test the generation of annotated binaries and the parsing
of the resulting files.

%endif

#----------------------------------------------------------------------------
%if %{with annocheck}

%package annocheck
Summary: A tool for checking the security hardening status of binaries

BuildRequires: elfutils elfutils-devel elfutils-libelf-devel rpm-devel make
%if %{bootstrapping}
BuildRequires: gcc
%else
BuildRequires: %{?scl_prefix}gcc
%endif

%if %{with debuginfod}
BuildRequires: elfutils-debuginfod-client-devel
%endif

Requires: %{name}-docs = %{version}-%{release}
Requires: cpio rpm

%description annocheck
Installs the annocheck program which uses the notes generated by annobin to
check that the specified files were compiled with the correct security
hardening options.

%package libannocheck
Summary: A library for checking the security hardening status of binaries

BuildRequires: elfutils elfutils-devel elfutils-libelf-devel rpm-devel make
%if %{bootstrapping}
BuildRequires: gcc
%else
BuildRequires: %{?scl_prefix}gcc
%endif

%if %{with debuginfod}
BuildRequires: elfutils-debuginfod-client-devel
%endif

Requires: %{name}-docs = %{version}-%{release}

%description libannocheck
Installs the libannocheck library which uses the notes generated by the
annobin plugins to check that the specified files were compiled with the
correct security hardening options.

%endif

#----------------------------------------------------------------------------
%if %{with gccplugin}

%package plugin-gcc
Summary: annobin gcc plugin

Requires: %{name}-docs = %{version}-%{release}
%if %{bootstrapping}
BuildRequires: gcc-c++ gcc-plugin-devel
%else
BuildRequires: %{?scl_prefix}gcc-c++ %{?scl_prefix}gcc-plugin-devel
%endif

# [Stolen from gcc-python-plugin]
# GCC will only load plugins that were built against exactly that build of GCC
# We thus need to embed the exact GCC version as a requirement within the
# metadata.
#
# Define "gcc_vr", a variable to hold the VERSION-RELEASE string for the gcc
# we are being built against.
#
# Unfortunately, we can't simply run:
#   rpm -q --qf="%%{version}-%%{release}"
# to determine this, as there's no guarantee of a sane rpm database within
# the chroots created by our build system
#
# So we instead query the version from gcc's output.
#
# gcc.spec has:
#   Version: %%{gcc_version}
#   Release: %%{gcc_release}%%{?dist}
#   ...snip...
#   echo 'Red Hat %%{version}-%%{gcc_release}' > gcc/DEV-PHASE
#
# So, given this output:
#
#   $ gcc --version
#   gcc (GCC) 4.6.1 20110908 (Red Hat 4.6.1-9)
#   Copyright (C) 2011 Free Software Foundation, Inc.
#   This is free software; see the source for copying conditions.  There is NO
#   warranty; not even for MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
# we can scrape out the "4.6.1" from the version line.
#
# The following implements the above:

%global gcc_vr %(%gcc_for_annobin --version | head -n 1 | sed -e 's|.*(Anolis\ OS\ ||g' -e 's|)$||g')

# We need the major version of gcc.
%global gcc_major %(echo "%{gcc_vr}" | cut -f1 -d".")
%global gcc_next  %(v="%{gcc_major}"; echo $((++v)))

# Needed when building the srpm.
%if 0%{?gcc_major} == 0
%global gcc_major 0
%endif

# For a gcc plugin gcc is required.
%if %{bootstrapping}
Requires: gcc
%else
%if %{with_hard_gcc_version_requirement}
# BZ 1607430 - There is an exact requirement on the major version of gcc.
Requires: (%{?scl_prefix}gcc >= %{gcc_major} with %{?scl_prefix}gcc < %{gcc_next})
%else
Requires: %{?scl_prefix}gcc
%endif
%endif

# Information about the gcc plugin is recorded in this file.
%global aver annobin-plugin-version-info

%description plugin-gcc
Installs an annobin plugin that can be used by gcc.

%endif

#---------------------------------------------------------------------------------
%if %{with llvmplugin}

%package plugin-llvm
Summary: annobin llvm plugin

Requires: %{name}-docs = %{version}-%{release}
Requires: llvm-libs
Conflicts: %{name} <= 9.60-1
BuildRequires: clang clang-devel llvm llvm-devel compiler-rt

%description plugin-llvm
Installs an annobin plugin that can be used by LLVM tools.

%endif

#---------------------------------------------------------------------------------
%if %{with clangplugin}

%package plugin-clang
Summary: annobin clang plugin

Requires: %{name}-docs = %{version}-%{release}
Requires: llvm-libs
Conflicts: %{name} <= 9.60-1
BuildRequires: clang clang-devel llvm llvm-devel compiler-rt

%description plugin-clang
Installs an annobin plugin that can be used by Clang.

%endif

#---------------------------------------------------------------------------------

# Decide where the plugins will live.  Change if necessary.

%if %{bootstrapping}

# If we are bootstrapping then we will be using the system gcc.  But we do
# not want to install the newly built GTS-15 annobin plugin into the system
# plugin directory.  So we hard code a path here.
# FIXME: This is going to need to be updated every time we bootstrap.  Find
# a better way.

%global GTS_GCC_MAJOR_VERSION 15

%global ANNOBIN_GCC_PLUGIN_DIR %{_scl_root}/usr/lib/gcc/%{_target_platform}/%{GTS_GCC_MAJOR_VERSION}/plugin

%else

%global ANNOBIN_GCC_PLUGIN_DIR %(%gcc_for_annobin --print-file-name=plugin)

%endif

%{!?llvm_plugin_dir:%global  llvm_plugin_dir  %{_libdir}/llvm/plugins}
%{!?clang_plugin_dir:%global clang_plugin_dir %{_libdir}/clang/plugins}

#---------------------------------------------------------------------------------

%prep
if [ -z "%{gcc_vr}" ]; then
    echo "*** Missing gcc_vr spec file macro, cannot continue." >&2
    exit 1
fi

echo "Requires: (%{?scl_prefix}gcc >= %{gcc_major} and %{?scl_prefix}gcc < %{gcc_next})"

# NB/ Do not add {?scl_prefix} to the -n option below.  The annobin sources
# unpack into a directory called annobin-VERSION not gcc-toolset-N-annobin-VERSION.
%autosetup -p1 -n %{annobin_dir}

# The plugin has to be configured with the same arcane configure
# scripts used by gcc.  Hence we must not allow the Fedora build
# system to regenerate any of the configure files.
touch aclocal.m4 gcc-plugin/config.h.in
touch configure */configure Makefile.in */Makefile.in
# Similarly we do not want to rebuild the documentation.
touch doc/annobin.info

# Generate a source tarball for installation later with all the patches
# applied.  This must be the last step in the prep section.
tar -C ../ -cJf ../%{latest_sources} %{annobin_dir}

#---------------------------------------------------------------------------------

%build

CONFIG_ARGS="--quiet"

%if %{with debuginfod}
CONFIG_ARGS="$CONFIG_ARGS --with-debuginfod"
%else
# Note - we explicitly disable debuginfod support if it was not configured.
# This is because by default annobin's configue script will assume --with-debuginfod=auto
# and then run a build time test to see if debugingfod is available.  It
# may well be, but the build time environment may not match the run time
# environment, and the rpm will not have a Requirement on the debuginfod
# client.
CONFIG_ARGS="$CONFIG_ARGS --without-debuginfod"
%endif

%if %{without clangplugin}
CONFIG_ARGS="$CONFIG_ARGS --without-clang-plugin"
%endif

%if %{without gccplugin}
CONFIG_ARGS="$CONFIG_ARGS --without-gcc-plugin"
%else
CONFIG_ARGS="$CONFIG_ARGS --with-gcc-plugin-dir=%{ANNOBIN_GCC_PLUGIN_DIR}"
%endif

%if %{without llvmplugin}
CONFIG_ARGS="$CONFIG_ARGS --without-llvm-plugin"
%endif

%if %{without tests}
CONFIG_ARGS="$CONFIG_ARGS --without-tests"
%endif

%if %{without annocheck}
CONFIG_ARGS="$CONFIG_ARGS --without-annocheck"
%else
# Fedora and RHEL-10 support AArch64's -mbranch-protection=bti, RHEL-9 does not.
%if 0%{?fedora} != 0
export CFLAGS="$CFLAGS -DAARCH64_BRANCH_PROTECTION_SUPPORTED=1"
%endif
%endif

%set_build_flags

export CFLAGS="$CFLAGS $RPM_OPT_FLAGS %build_cflags -I%{?_scl_root}/usr/include"
export LDFLAGS="$LDFLAGS %build_ldflags -L%{?_scl_root}/usr/lib64 -L%{?_scl_root}/usr/lib"

# Set target-specific options to be used when building the Clang and LLVM plugins.
# FIXME: There should be a better way to do this.
%ifarch %{ix86} x86_64
export CLANG_TARGET_OPTIONS="-fcf-protection"
%endif

%ifarch aarch64
export CLANG_TARGET_OPTIONS="-mbranch-protection=standard"
%endif

%ifnarch riscv64
export CLANG_TARGET_OPTIONS="$CLANG_TARGET_OPTIONS -flto -O2"
%endif
	
# # Override the default fortification level used by the Clang and LLVM plugins.
# export PLUGIN_FORTIFY_OPTION="-D_FORTIFY_SOURCE=3"

CC=%gcc_for_annobin CXX=%gxx_for_annobin CFLAGS="$CFLAGS" LDFLAGS="$LDFLAGS" CXXFLAGS="$CFLAGS" %configure ${CONFIG_ARGS} || cat config.log

%make_build

%if %{with plugin_rebuild}
# Rebuild the plugin(s), this time using the plugin itself!  This
# ensures that the plugin works, and that it contains annotations
# of its own.

%if %{with gccplugin}
cp gcc-plugin/.libs/annobin.so.0.0.0 %{_tmppath}/tmp_annobin.so
make -C gcc-plugin clean
BUILD_FLAGS="-fplugin=%{_tmppath}/tmp_annobin.so"

# Disable the standard annobin plugin so that we do get conflicts.
# Note - rpm-4.10 uses a different way of evaluating macros.
#%if 0%{?rhel} && 0%{?rhel} < 9
#OPTS="$(rpm --eval '%undefine _annotated_build %build_cflags %build_ldflags')"
#%else
OPTS="$(rpm --undefine=_annotated_build --eval '%build_cflags %build_ldflags')"
#%endif

# If building on systems with an assembler that does not support the
# .attach_to_group pseudo op (eg RHEL-7) then enable the next line.
# BUILD_FLAGS="$BUILD_FLAGS -fplugin-arg-tmp_annobin-no-attach"

make -C gcc-plugin CXX=%gxx_for_annobin CXXFLAGS="$OPTS $BUILD_FLAGS"
rm %{_tmppath}/tmp_annobin.so
%endif

%if %{with clangplugin}
cp clang-plugin/annobin-for-clang.so %{_tmppath}/tmp_annobin.so
# To enable verbose more in the plugin append the following: ANNOBIN="verbose"
make -C clang-plugin clean all CLANG_TARGET_OPTIONS="$CLANG_TARGET_OPTIONS $BUILD_FLAGS" PLUGIN_INSTALL_DIR=%{clang_plugin_dir}
%endif

%if %{with llvmplugin}
cp llvm-plugin/annobin-for-llvm.so %{_tmppath}/tmp_annobin.so
# To enable verbose more in the plugin append the following: ANNOBIN_VERBOSE="true"
make -C llvm-plugin clean all CLANG_TARGET_OPTIONS="$CLANG_TARGET_OPTIONS $BUILD_FLAGS" PLUGIN_INSTALL_DIR=%{llvm_plugin_dir}
%endif

# endif for %%if {with_plugin_rebuild}
%endif

#---------------------------------------------------------------------------------

%install

# PLUGIN_INSTALL_DIR is used by the Clang and LLVM makefiles...
%make_install PLUGIN_INSTALL_DIR=%{buildroot}/%{llvm_plugin_dir}

%if %{with clangplugin}
# Move the clang plugin to a seperate directory.
mkdir -p %{buildroot}/%{clang_plugin_dir}
mv %{buildroot}/%{llvm_plugin_dir}/annobin-for-clang.so %{buildroot}/%{clang_plugin_dir}
%endif

%if %{with gccplugin}
pushd %{buildroot}/%{ANNOBIN_GCC_PLUGIN_DIR}

# Record the version of gcc that built this plugin.
# Note - we cannot just store %%{gcc_vr} as sometimes the gcc rpm version changes
# without the NVR being altered.  See BZ #2030671 for more discussion on this.
cat `%gcc_for_annobin --print-file-name=rpmver` > %{aver}

# Also rename the plugin to its GTS variant
mv annobin.so.0.0.0 gts-annobin.so.0.0.0
rm -f annobin.so annobin.so.0 gts-annobin.so gts-annobin.so.0
ln -s gts-annobin.so.0.0.0 gts-annobin.so
ln -s gts-annobin.so.0.0.0 gts-annobin.so.0

popd

# Also install a copy of the sources into the build tree.
mkdir -p                %{buildroot}%{annobin_source_dir}
cp ../%{latest_sources} %{buildroot}%{annobin_source_dir}
%endif

rm -f %{buildroot}%{_infodir}/dir

# When annocheck is disabled, annocheck.1.gz will still be generated, remove it.
%if %{without annocheck}
rm -f %{_mandir}/man1/annocheck.1.gz
%endif

#---------------------------------------------------------------------------------

%if %{with tests}
%check
# The first "make check" is run with "|| :" so that we can capture any logs
# from failed tests.  The second "make check" is there so that the build
# will fail if any of the tests fail.
make check GCC=%gcc_for_annobin CC=%gcc_for_annobin || :
if [ -f tests/test-suite.log ]; then
    cat tests/test-suite.log
fi

# If necessary use uuencode to preserve test binaries here.  For example:
#   uuencode tests/tmp_atexit/atexit.strip atexit.strip

# Now repeat the tests so that we get the correct exit code.
make check GCC=%gcc_for_annobin CC=%gcc_for_annobin 
%endif

#---------------------------------------------------------------------------------

%files docs
%license COPYING3 LICENSE
%exclude %{_datadir}/doc/annobin-plugin/COPYING3
%exclude %{_datadir}/doc/annobin-plugin/LICENSE
%doc %{_datadir}/doc/annobin-plugin/annotation.proposal.txt
%{_infodir}/annobin.info*
%{_mandir}/man1/annobin.1*
%exclude %{_mandir}/man1/built-by.1*
%exclude %{_mandir}/man1/check-abi.1*
%exclude %{_mandir}/man1/hardened.1*
%exclude %{_mandir}/man1/run-on-binaries-in.1*

%if %{with llvmplugin}
%files plugin-llvm
%dir %{llvm_plugin_dir}
%{llvm_plugin_dir}/annobin-for-llvm.so
%endif

%if %{with clangplugin}
%files plugin-clang
%dir %{clang_plugin_dir}
%{clang_plugin_dir}/annobin-for-clang.so
%endif

%if %{with gccplugin}
%files plugin-gcc
%dir %{ANNOBIN_GCC_PLUGIN_DIR}

%{ANNOBIN_GCC_PLUGIN_DIR}/gts-annobin.so
%verify(owner) %{ANNOBIN_GCC_PLUGIN_DIR}/gts-annobin.so

%{ANNOBIN_GCC_PLUGIN_DIR}/gts-annobin.so.0
%verify(owner) %{ANNOBIN_GCC_PLUGIN_DIR}/gts-annobin.so.0

%{ANNOBIN_GCC_PLUGIN_DIR}/gts-annobin.so.0.0.0
%verify(owner) %{ANNOBIN_GCC_PLUGIN_DIR}/gts-annobin.so.0.0.0

%{ANNOBIN_GCC_PLUGIN_DIR}/%{aver}

%dir %{annobin_source_dir}
%{annobin_source_dir}/%{latest_sources}
%endif

%if %{with annocheck}
%files annocheck
%{_bindir}/annocheck
%{_mandir}/man1/annocheck.1*

%files libannocheck
%{_includedir}/libannocheck.h
%{_libdir}/libannocheck.*
%{_libdir}/pkgconfig/libannocheck.pc
%endif

#---------------------------------------------------------------------------------

%changelog
* Tue Jun 17 2025 Nick Clifton  <nickc@redhat.com> - 12.93-4
- Generate latest-annobin.tar.xz at prep phase (RHEL-95704)

* Tue Jun 10 2025 Nick Clifton  <nickc@redhat.com> - 12.93-3
- Disable bootstrapping.  Also use error() in place of warning() in the gcc plugin.  (RHEL-95704)

* Tue Apr 01 2025 Nick Clifton  <nickc@redhat.com> - 12.93-2
- NVR bump in order to allow rebuilding with correct GTS-15 tags.  (RHEL-81744)

* Fri Mar 28 2025 Nick Clifton  <nickc@redhat.com> - 12.93-1
- Initial commit on c8s.  (RHELPLAN-171846)
