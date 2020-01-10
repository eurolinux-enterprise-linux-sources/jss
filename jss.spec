################################################################################
Name:           jss
################################################################################

Summary:        Java Security Services (JSS)
URL:            http://www.dogtagpki.org/wiki/JSS
License:        MPLv1.1 or GPLv2+ or LGPLv2+

Version:        4.4.4
Release:        5%{?_timestamp}%{?_commit_id}%{?dist}

# To generate the source tarball:
#
# git clone https://github.com/dogtagpki/jss.git
# cd jss
# git archive --format=tar.gz --prefix jss-VERSION/jss/ -o jss-VERSION.tar.gz -v HEAD
#
Source:         https://github.com/dogtagpki/%{name}/archive/v%{version}/%{name}-%{version}.tar.gz

Patch0:         jss-fix-classpath.patch
Patch1:         jss-fix-README.patch
Patch2:         jss-update-jss-spec-in-template.patch
Patch3:         jss-add-build-sh.patch
Patch4:         jss-add-travis-yml.patch
Patch5:         jss-add-x509-cert-and-crl-migration.patch
Patch6:         jss-fix-algorithm-identifier-encode-decode.patch
Patch7:         jss-add-TLS-SHA384-ciphers.patch
Patch8:         jss-disallow-curve-x25519-in-FIPS-mode.patch
Patch9:         jss-enable-AIA-OCSP-cert-checking-for-entire-cert-chain.patch
Patch10:        jss-enable-AIA-OCSP-cert-checking-for-entire-cert-chain-2.patch


Conflicts:      idm-console-framework < 1.1.17-4
Conflicts:      pki-base < 10.4.0
Conflicts:      tomcatjss < 7.2.1

# autosetup
BuildRequires:  git

BuildRequires:  nss-devel >= 3.28.4-6
BuildRequires:  nspr-devel >= 4.13.1
BuildRequires:  java-devel
BuildRequires:  jpackage-utils
%if 0%{?fedora} >= 25 || 0%{?rhel} > 7
BuildRequires:  perl-interpreter
%endif
BuildRequires:  apache-commons-lang
BuildRequires:  apache-commons-codec
BuildRequires:  ldapjdk

Requires:       nss >= 3.28.4-6
Requires:       java-headless
Requires:       jpackage-utils
Requires:       apache-commons-lang
Requires:       apache-commons-codec
Requires:       ldapjdk

%description
Java Security Services (JSS) is a java native interface which provides a bridge
for java-based applications to use native Network Security Services (NSS).
This only works with gcj. Other JREs require that JCE providers be signed.

################################################################################
%package javadoc
################################################################################

Summary:        Java Security Services (JSS) Javadocs
Group:          Documentation
Requires:       jss = %{version}-%{release}

%description javadoc
This package contains the API documentation for JSS.

################################################################################
%prep

#%autosetup -n %{name}-%{version} -p 1 -S git
%setup -q -n %{name}-%{version}
pushd jss
# Force use of 'patch' rather than 'git apply' by injecting "/jss/" prefix
# on patches of existing files located in top-level directory . . .
%patch0 -p2
%patch1 -p2
%patch2 -p2
%patch3 -p1
%patch4 -p1
%patch5 -p1
%patch6 -p2
%patch7 -p2
%patch8 -p2
%patch9 -p2
%patch10 -p2
popd

################################################################################
%build

#%set_build_flags

[ -z "$JAVA_HOME" ] && export JAVA_HOME=%{_jvmdir}/java
[ -z "$USE_INSTALLED_NSPR" ] && export USE_INSTALLED_NSPR=1
[ -z "$USE_INSTALLED_NSS" ] && export USE_INSTALLED_NSS=1

# Enable compiler optimizations and disable debugging code
# NOTE: If you ever need to create a debug build with optimizations disabled
# just comment out this line and change in the %%install section below the
# line that copies jars xpclass.jar to be xpclass_dbg.jar
export BUILD_OPT=1

# Generate symbolic info for debuggers
XCFLAGS="-g $RPM_OPT_FLAGS"
export XCFLAGS

PKG_CONFIG_ALLOW_SYSTEM_LIBS=1
PKG_CONFIG_ALLOW_SYSTEM_CFLAGS=1

export PKG_CONFIG_ALLOW_SYSTEM_LIBS
export PKG_CONFIG_ALLOW_SYSTEM_CFLAGS

NSPR_INCLUDE_DIR=`/usr/bin/pkg-config --cflags-only-I nspr | sed 's/-I//'`
NSPR_LIB_DIR=`/usr/bin/pkg-config --libs-only-L nspr | sed 's/-L//'`

NSS_INCLUDE_DIR=`/usr/bin/pkg-config --cflags-only-I nss | sed 's/-I//'`
NSS_LIB_DIR=`/usr/bin/pkg-config --libs-only-L nss | sed 's/-L//'`

export NSPR_INCLUDE_DIR
export NSPR_LIB_DIR
export NSS_INCLUDE_DIR
export NSS_LIB_DIR

%if 0%{?__isa_bits} == 64
USE_64=1
export USE_64
%endif

# The Makefile is not thread-safe
make -C jss/coreconf
make -C jss
make -C jss javadoc

################################################################################
%install

# Copy the license files here so we can include them in %%doc
cp -p jss/MPL-1.1.txt .
cp -p jss/gpl.txt .
cp -p jss/lgpl.txt .

# There is no install target so we'll do it by hand

# jars
install -d -m 0755 $RPM_BUILD_ROOT%{_jnidir}
# NOTE: if doing a debug no opt build change xpclass.jar to xpclass_dbg.jar
install -m 644 dist/xpclass.jar ${RPM_BUILD_ROOT}%{_jnidir}/jss4.jar

# We have to use the name libjss4.so because this is dynamically
# loaded by the jar file.
install -d -m 0755 $RPM_BUILD_ROOT%{_libdir}/jss
install -m 0755 dist/Linux*.OBJ/lib/libjss4.so ${RPM_BUILD_ROOT}%{_libdir}/jss/
pushd  ${RPM_BUILD_ROOT}%{_libdir}/jss
    ln -fs %{_jnidir}/jss4.jar jss4.jar
popd

# javadoc
install -d -m 0755 $RPM_BUILD_ROOT%{_javadocdir}/%{name}-%{version}
cp -rp dist/jssdoc/* $RPM_BUILD_ROOT%{_javadocdir}/%{name}-%{version}
cp -p jss/jss.html $RPM_BUILD_ROOT%{_javadocdir}/%{name}-%{version}
cp -p jss/*.txt $RPM_BUILD_ROOT%{_javadocdir}/%{name}-%{version}

# No ldconfig is required since this library is loaded by Java itself.
################################################################################
%files

%defattr(-,root,root,-)
%doc jss/jss.html jss/MPL-1.1.txt jss/gpl.txt jss/lgpl.txt
%{_libdir}/jss/*
%{_jnidir}/*
%{_libdir}/jss/lib*.so

################################################################################
%files javadoc

%defattr(-,root,root,-)
%dir %{_javadocdir}/%{name}-%{version}
%{_javadocdir}/%{name}-%{version}/*

################################################################################
%changelog
* Fri Feb 15 2019 Dogtag PKI Team <pki-devel@redhat.com> 4.4.4-5
- Bugzilla #1671247 - CC: Enable AIA OCSP cert checking for entire cert
  chain [rhel-7.6.z] (jmagne)

* Thu Jan 31 2019 Dogtag PKI Team <pki-devel@redhat.com> 4.4.4-4
- Bugzilla #1671244 - x25519 allowed in FIPS mode [rhel-7.6.z] (ascheel)
- Bugzilla #1671247 - CC: Enable AIA OCSP cert checking for entire cert
  chain [rhel-7.6.z] (jmagne)

* Thu Jul  5 2018 Dogtag PKI Team <pki-devel@redhat.com> 4.4.4-3
- Bugzilla #1534772 - org.mozilla.jss.pkix.primitive.AlgorithmIdentifier
  decode/encode process alters original data (cfu)
- Bugzilla #1554056 - JSS: Add support for TLS_*_SHA384 ciphers (cfu)

* Thu Jun 21 2018 Dogtag PKI Team <pki-devel@redhat.com> 4.4.4-2
- Red Hat Bugzilla #1560682 - (RFE) Migrate RHCS x509 cert and crl
  functionality to JSS (jmagne)

* Tue May 29 2018 Dogtag PKI Team <pki-devel@redhat.com> 4.4.4-1
- Rebased to JSS 4.4.4

* Thu Apr 05 2018 Dogtag PKI Team <pki-devel@redhat.com> 4.4.3-1
- Rebased to JSS 4.4.3
#- Red Hat Bugzilla #1548548 - Partial Fedora build flags injection
