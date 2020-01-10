Name:           jss
Version:        4.4.0
Release:        13%{?dist}
Summary:        Java Security Services (JSS)

Group:          System Environment/Libraries
License:        MPLv1.1 or GPLv2+ or LGPLv2+
URL:            http://www.mozilla.org/projects/security/pki/jss/
# The source for this package was pulled from upstream's hg. Use the
# following commands to generate the tarball:
#
# hg clone https://hg.mozilla.org/projects/jss
# cd jss
# hg archive --prefix jss-4.4.0/jss/ ../jss-4.4.0.tar.gz
#
Source0:        http://pki.fedoraproject.org/pki/sources/%{name}/%{version}/%{name}-%{version}.tar.gz
Source1:        http://pki.fedoraproject.org/pki/sources/%{name}/%{version}/MPL-1.1.txt
Source2:        http://pki.fedoraproject.org/pki/sources/%{name}/%{version}/gpl.txt
Source3:        http://pki.fedoraproject.org/pki/sources/%{name}/%{version}/lgpl.txt
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

Conflicts:      idm-console-framework < 1.1.17-4
Conflicts:      pki-base < 10.4.0
Conflicts:      tomcatjss < 7.2.1

BuildRequires:  nss-devel >= 3.28.4-6
BuildRequires:  nspr-devel >= 4.13.1
BuildRequires:  java-devel
%if 0%{?fedora} >= 25 || 0%{?rhel} > 7
BuildRequires:  perl-interpreter
%endif
Requires:       java-headless
Requires:       nss >= 3.28.4-6

Patch1:         jss-post-rebase.patch
Patch2:         jss-rhel-7-4-beta.patch
Patch3:         jss-HMAC-test-for-AES-encrypt-unwrap.patch
Patch4:         jss-PBE-padded-block-cipher-enhancements.patch
Patch5:         jss-fix-PK11Store-getEncryptedPrivateKeyInfo-segfault.patch
Patch6:         jss-HMAC-unwrap-keywrap-FIPSMODE.patch
Patch7:         jss-SignatureAlgorithm.patch
Patch8:         jss-ObjectNotFoundException-message.patch
Patch9:         jss-signature-correction.patch
Patch10:        jss-standardize-ECC-algorithm-names.patch
Patch11:        jss-fix-SignerInfo-version.patch
Patch12:        jss-fix-ECDSA-SHA-AlgorithmIdentifier-encoding.patch
Patch13:        jss-fix-algorithm-identifier-encode-decode.patch
Patch14:        jss-add-TLS-SHA384-ciphers.patch

%description
Java Security Services (JSS) is a java native interface which provides a bridge
for java-based applications to use native Network Security Services (NSS).
This only works with gcj. Other JREs require that JCE providers be signed.

%package javadoc
Summary:        Java Security Services (JSS) Javadocs
Group:          Documentation
Requires:       jss = %{version}-%{release}

%description javadoc
This package contains the API documentation for JSS.

%prep
%setup -q -n %{name}-%{version}
pushd jss
%patch1 -p1
%patch2 -p1
%patch3 -p1
%patch4 -p1
%patch5 -p1
%patch6 -p1
%patch7 -p1
%patch8 -p1
%patch9 -p1
%patch10 -p1
%patch11 -p1
%patch12 -p1
%patch13 -p1
%patch14 -p1
popd

%build
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

%check

%install
rm -rf $RPM_BUILD_ROOT docdir

# Copy the license files here so we can include them in %%doc
cp -p %{SOURCE1} .
cp -p %{SOURCE2} .
cp -p %{SOURCE3} .

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
cp -p *.txt $RPM_BUILD_ROOT%{_javadocdir}/%{name}-%{version}

%clean
rm -rf $RPM_BUILD_ROOT

# No ldconfig is required since this library is loaded by Java itself.
%files
%defattr(-,root,root,-)
%doc jss/jss.html MPL-1.1.txt gpl.txt lgpl.txt
%{_libdir}/jss/*
%{_jnidir}/*
%{_libdir}/jss/lib*.so

%files javadoc
%defattr(-,root,root,-)
%dir %{_javadocdir}/%{name}-%{version}
%{_javadocdir}/%{name}-%{version}/*

%changelog
* Mon Jul  2 2018 Dogtag Team <pki-devel@redhat.com> 4.4.2-13
- Bugzilla #1595759 - org.mozilla.jss.pkix.primitive.AlgorithmIdentifier
  decode/encode process alters original data [rhel-7.5.z] (cfu)
- Bugzilla #1596552 - JSS: Add support for TLS_*_SHA384 ciphers
  [rhel-7.5.z] (cfu)

* Tue May 22 2018 Dogtag Team <pki-devel@redhat.com> 4.4.2-12
- Bugzilla #1579202 - JSS has wrong encoding for ecdsa with sha*
  AlgorithmIdentifier [rhel-7.5.z] (cfu)

* Mon Jan 22 2018 Dogtag Team <pki-devel@redhat.com> 4.4.0-11
- Bugzilla #1506826 - org.mozilla.jss.pkix.cms.SignerInfo incorrectly
  producing signatures (especially for EC) (cfu,dstutzman)
- Bugzilla #1533667 - Add: standard algorithm names for all ECC signature
  types (cfu,dstutzman)
- Bugzilla #1534761 - SignerInfo class inserts wrong version # into the
  resulting structure (cfu,dstutzman)

* Wed Nov  1 2017 Dogtag Team <pki-devel@redhat.com> 4.4.0-10
- Bugzilla #1506710 - JSS throws ObjectNotFoundException without message
  (edewata)
- Bugzilla #1506826 - org.mozilla.jss.pkix.cms.SignerInfo incorrectly
  producing signatures (especially for EC) (cfu,dstutzman)

* Fri Oct 27 2017 Dogtag Team <pki-devel@redhat.com> 4.4.0-9
- Bugzilla #1505690 - new JSS failures: HMAC Unwrap and KeyWrapping
  FIPSMODE [rhel-7.4.z] (jmagne)

* Mon Sep 11 2017 Dogtag Team <pki-devel@redhat.com> 4.4.0-8
- Bugzilla #1488846 - Fix HmacTest code for AES encrypt/unwrap [rhel-7.4.z]
  (jmagne)
- Bugzilla #1490494 - PKCS12: (JSS) upgrade to at least AES and SHA2 (FIPS)
  [RHEL-7.4.z] (ftweedal)
- Bugzilla #1490740 - PK11Store.getEncryptedPrivateKeyInfo() segfault if
  export fails [rhel-7.4.z] (ftweedal)

* Tue May  9 2017 Matthew Harmsen <mharmsen@redhat.com> - 4.4.0-7
- Bump NSS dependencies from 4.28.3 to 4.28.4-6 to pick-up fix in
  Mozilla Bugzilla #1360207 - Fix incorrect if (ss->...) in SSL_ReconfigFD

* Mon May  1 2017 Matthew Harmsen <mharmsen@redhat.com> - 4.4.0-6
- Mozilla Bugzilla #1352476 - RFE: Document on the README how to create a
  release tag (mharmsen)
- Mozilla Bugzilla #1355358 - CryptoStore: add methods for importing and
  exporting EncryptedPrivateKeyInfo (ftweedal)
- Mozilla Bugzilla #1359731 - CryptoStore.importPrivateKey enhancements
  (ftweedal)

* Mon Apr 17 2017 Matthew Harmsen <mharmsen@redhat.com> - 4.4.0-5
- Mozilla Bugzilla #1355268 - JSS 4.4 is incompatible with versions of
  idm-console-framework < 1.1.17-4
- Red Hat Bugzilla #1435076 - Remove unused legacy lines from JSS spec files

* Mon Mar 27 2017 Matthew Harmsen <mharmsen@redhat.com> - 4.4.0-4
- Bugzilla Bug #1394414 - Rebase jss to 4.4.0 in RHEL 7.4
- Updated build requirements for NSPR
- Updated build and runtime requirements for NSS
- ## 'jss-post-rebase.patch' resolves the following issues ported from
  ## upstream:
- Mozilla Bugzilla #1337092 - CMC conformance update: Implement required ASN.1
  code for RFC5272+ (cfu)
- Mozilla Bugzilla #1347394 - Eclipse project files for JSS (edewata)
- Mozilla Bugzilla #1347429 - Deprecated SSL 3.0 cipher names in SSLSocket
  class. (edewata)
- Mozilla Bugzilla #1348856 - SSL alert callback (edewata)
- Mozilla Bugzilla #1349278 - SSL cipher enumeration (edewata)
- Mozilla Bugzilla #1349349 - Problem with Password.readPasswordFromConsole().
  (edewata)
- Mozilla Bugzilla #1349831 - Revise top-level README file (mharmsen)
- Mozilla Bugzilla #1349836 - Changes to JSS Version Block (mharmsen)
- Mozilla Bugzilla #1350130 - Missing
  CryptoManager.verifyCertificateNowCUNative() implementation. (emaldona)

* Tue Mar 21 2017 Matthew Harmsen <mharmsen@redhat.com> - 4.4.0-3
- Added Conflicts statement due to incompatibility with pki-base < 10.4.0

* Wed Mar 15 2017 Matthew Harmsen <mharmsen@redhat.com> - 4.4.0-2
- Added Conflicts statement due to incompatibility with tomcatjss < 7.2.1

* Mon Mar 13 2017 Elio Maldonado <emaldona@redhat.com> - 4.4.0-1
- Bugzilla Bug #1394414 - Rebase jss to 4.4.0 in RHEL 7.4
- ## JSS 4.4.0 includes the following patches ported from downstream:
- Mozilla Bugzilla #507536 - Add IPv6 functionality to JSS
- Mozilla Bugzilla #1307872 - Expose NSS calls for OCSP settings
- Mozilla Bugzilla #1307882 - RFE ecc - add ecc curve name support in JSS and
  CS interface
- Mozilla Bugzilla #1307993 - Expose updated certificate verification function
  in JSS
- Mozilla Bugzilla #1308000 - Incorrect socket accept error message due to bad
  pointer arithmetic
- Mozilla Bugzilla #1308001 - Verification should fail when a revoked
  certificate is added
- Mozilla Bugzilla #1308004 - Warnings should be cleaned up in JSS build
- Mozilla Bugzilla #1308006 - DRM failed to recovery keys when in FIPS mode
  (HSM + NSS)
- Mozilla Bugzilla #1308008 - Defects revealed by Coverity scan
- Mozilla Bugzilla #1308009 - Add support for PKCS5v2; support for secure PKCS12
- Mozilla Bugzilla #1308012 - DRM: during archiving and recovering, wrapping
  unwrapping keys should be done in the token
- Mozilla Bugzilla #1308013 - JSS - HSM token name was mistaken for
  manufacturer identifier
- Mozilla Bugzilla #1308017 - Un-deprecate previously deprecated methods in
  JSS 4.2.6
- Mozilla Bugzilla #1308019 - Provide Tomcat support for TLS v1.1 and
  TLS v1.2 via NSS through JSS
- Mozilla Bugzilla #1308026 - JSS certificate validation does not pass up exact
  error from NSS
- Mozilla Bugzilla #1308027 - Merge pki-symkey into jss
- Mozilla Bugzilla #1308029 - Resolve Javadoc build issues
- Mozilla Bugzilla #1308047 - support ECC encryption key archival and recovery
- Mozilla Bugzilla #1313122 - Remove bypass tests as latest NSS has removed
  PKCS#11 bypass support
- Mozilla Bugzilla #1328675 - Simple problem unwrapping AES sym keys on token
- Mozilla Bugzilla #1345174 - Cannot create system certs when using LunaSA HSM
  in FIPS Mode and ECC algorithms
- Mozilla Bugzilla #1345613 - expose AES KeyWrap and add some useful OID
  functions
- Mozilla Bugzilla #1346410 - Load JSS libraries appropriately
- ## JSS 4.4.0 includes the following changes for building and testing:
- Mozilla Bugzilla #1331765 - Simplify JSS Makefile build and test
- Mozilla Bugzilla #1346420 - Document steps required to use the proper
  libjss4.so when running certain HMAC Algorithms tests

* Wed Feb 22 2017 Jack Magne <jmagne@redhat.com> - 4.2.6-44
- Bugzilla Bug #1425971 - Simple problem unwrapping AES sym keys on token

* Fri Feb 10 2017 Fedora Release Engineering <releng@fedoraproject.org> - 4.2.6-43
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Tue Aug 9 2016 Christina Fu <cfu@redhat.com> - 4.2.6-42
- Sync up patches from both Fedora and RHEL; adding two patches
  (cfu, edewata, mharmsen) from RHEL:
- Bugzilla Bug #1238450 - UnsatisfiedLinkError on Windows (cfu)
- make it compile on Windows platforms (cfu for nhosoi)

* Fri Jun 24 2016 Christina Fu <cfu@redhat.com> - 4.2.6-41
- Bugzilla 1221295 jss fails to decode EncryptedKey >> EnvelopedData
  (cfu for roysjosh@gmail.com)

* Thu May 19 2016 Christina Fu <cfu@redhat.com> - 4.2.6-40
- Bugzilla 1074208 - pass up exact JSS certificate validation errors from NSS
  (edewata)
- Bugzilla 1331596 - Key archival fails when KRA is configured with lunasa.
  (cfu)
- PKI ticket 801 - Merge pki-symkey into jss (phase 1)
  (jmagne)

* Wed Dec 09 2015 Endi Dewata <edewata@redhat.com> - 4.2.6-38
- Bugzilla Bug #1289799 - JSS build failure on F23 and Rawhide (edewata)

* Thu Apr 09 2015 Marcin Juszkiewicz <mjuszkiewicz@redhat.com> - 4.2.6-37
- Fix use of __isa_bits macro so it does not fail during srpm generation on koji

* Thu Apr 09 2015 Marcin Juszkiewicz <mjuszkiewicz@redhat.com> - 4.2.6-36
- Use __isa_bits macro to check for 64-bit arch. Unblocks aarch64 and ppc64le.

* Tue Sep 30 2014 Christina Fu <cfu@redhat.com> - 4.2.6-35
- Bugzilla Bug #1040640 - Incorrect OIDs for SHA2 algorithms
  (cfu for jnimeh@gmail.com)
- Bugzilla Bug #1133718 - Key strength validation is not performed for RC4
  algorithm (nkinder)
- Bugzilla Bug #816396 - Provide Tomcat support for TLS v1.1 and
  TLS v1.2 via NSS through JSS (cfu)

* Sat Aug 16 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 4.2.6-34
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Sun Jun 08 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 4.2.6-33
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Fri Mar 28 2014 Michael Simacek <msimacek@redhat.com> - 4.2.6-32
- Use Requires: java-headless rebuild (#1067528)

* Sat Aug 03 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 4.2.6-31
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Wed Jul 17 2013 Nathan Kinder <nkinder@redhat.com> - 4.2.6-30
- Bugzilla Bug #847120 - Unable to build JSS on F17 or newer

* Thu Feb 14 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 4.2.6-29
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Wed Dec 19 2012 Stanislav Ochotnicky <sochotnicky@redhat.com> - 4.2.6-28
- revbump after jnidir change

* Wed Dec 12 2012 Stanislav Ochotnicky <sochotnicky@redhat.com> - 4.2.6-27
- Simple rebuild

* Mon Nov 19 2012 Christina Fu <cfu@redhat.com> - 4.2.6-26
- added source URLs in spec file to pass Package Wrangler

* Thu Jul 19 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 4.2.6-25
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Fri Mar 30 2012 Matthew Harmsen <mharmsen@redhat.com> - 4.2.6-24
- Bugzilla Bug #783007 - Un-deprecate previously deprecated methods in
  JSS 4.2.6 . . . BadPaddingException (mharmsen)

* Tue Mar 20 2012 Christina Fu <cfu@redhat.com> - 4.2.6-23
- Bugzilla Bug #797351 - JSS - HSM token name was mistaken for manufacturer
  identifier (cfu)
- Bugzilla Bug #804840 - [RFE] ECC encryption keys cannot be archived
  ECC phase2 work - support for ECC encryption key archival and recovery (cfu)
- Bugzilla Bug #783007 - Un-deprecate previously deprecated methods in
  JSS 4.2.6 . . . (mharmsen)
- Dogtag TRAC Task #109 (https://fedorahosted.org/pki/ticket/109) - add
  benign JNI jar file symbolic link from JNI libdir to JNI jar file (mharmsen)

* Fri Jan 13 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 4.2.6-22
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Wed Oct 19 2011 Christina Fu <cfu@redhat.com> - 4.2.6-21
- Bugzilla Bug #737122 - DRM: during archiving and recovering, wrapping
  unwrapping keys should be done in the token
- support for PKCS5v2; support for secure PKCS12
- Bugzilla Bug #744797 - KRA key recovery (retrieve pkcs#12) fails after the
  in-place upgrade( CS 8.0->8.1)

* Mon Sep 19 2011 Matthew Harmsen <mharmsen@redhat.com> - 4.2.6-20
- Bugzilla Bug #715621 - Defects revealed by Coverity scan

* Wed Aug 31 2011 Matthew Harmsen <mharmsen@redhat.com> - 4.2.6-19.1
- Bugzilla Bug #734590 - Refactor JNI libraries for Fedora 16+ . . .

* Mon Aug 15 2011 Christina Fu <cfu@redhat.com> - 4.2.6-19
- Bugzilla Bug 733550 - DRM failed to recovery keys when in FIPS mode
  (HSM + NSS)

* Fri Aug 12 2011 Matthew Harmsen <mharmsen@redhat.com> - 4.2.6-18
- Bugzilla Bug #660436 - Warnings should be cleaned up in JSS build
  (jdennis, mharmsen)

* Wed May 18 2011 Christina Fu <cfu@redhat.com> - 4.2.6-17
- Bug 670980 - Cannot create system certs when using LunaSA HSM in FIPS Mode
  and ECC algorithms (support tokens that don't do ECDH)

* Fri Apr 08 2011 Jack Magne <jmagne@redhat.com> - 4.2.6-15.99
- bug 694661 - TKS instance crash during token enrollment.
  Back out of previous patch for #676083.

* Thu Feb 24 2011 Andrew Wnuk <awnuk@redhat.com> - 4.2.6-15
- bug 676083 - JSS: slots not freed 

* Wed Feb 09 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 4.2.6-14
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Mon Jan 31 2011 John Dennis <jdennis@redhat.com> - 4.2.6-13
- remove misleading comment in spec file concerning jar signing

* Tue Jan 11 2011 Kevin Wright <kwright@redhat.com> - 4.2.6-12
- added missing patch line

* Tue Dec 21 2010 Christina Fu <cfu@redhat.com> - 4.2.6-11
- bug 654657 - <jdennis@redhat.com>
  Incorrect socket accept error message due to bad pointer arithmetic
- bug 661142 - <cfu@redhat.com>
  Verification should fail when a revoked certificate is added

* Thu Dec 16 2010 John Dennis <jdennis@redhat.com> - 4.2.6-10
- Resolves: bug 656094 - <jdennis@redhat.com>
  Rebase jss to at least jss-4.2.6-9
- <jdennis@redhat.com>
  merge in updates from Fedora
  move jar location to %%{_libdir}/jss and provide symlinks, on 32bit looks like this:
    /usr/lib/java/jss4.jar -> /usr/lib/jss/jss4.jar
    /usr/lib/jss/jss4-<version>.jar
    /usr/lib/jss/jss4.jar -> jss4-<version>.jar
    /usr/lib/jss/libjss4.so
- bug 654657 - <jdennis@redhat.com>
  Incorrect socket accept error message due to bad pointer arithmetic
- bug 647364 - <cfu@redhat.com>
  Expose updated certificate verification function in JSS
- bug 529945 - <cfu@redhat.com>
  expose NSS calls for OCSP settings
- bug 638833 - <cfu@redhat.com>
  rfe ecc - add ec curve name support in JSS and CS
- <rcritten@redhat.com>
  Need to explicitly catch UnsatisfiedLinkError exception for System.load()
- bug 533304 - <rcritten@redhat.com>
  Move location of libjss4.so to subdirectory and use System.load() to
  load it instead of System.loadLibrary() for Fedora packaging compliance

* Mon Nov 30 2009 Dennis Gregorovic <dgregor@redhat.com> - 4.2.6-4.1
- Rebuilt for RHEL 6

* Fri Jul 31 2009 Rob Crittenden <rcritten@redhat.com> 4.2.6-4
- Resolves: bug 224688 - <cfu@redhat.com>
  Support ECC POP on the server
- Resolves: bug 469456 - <jmagne@redhat.com>
  Server Sockets are hard coded to IPV4
- Resolves: bug 509183 - <mharmsen@redhat.com>
  Set NSS dependency >= 3.12.3.99

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 4.2.6-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Fri Jun  5 2009 Rob Crittenden <rcritten@redhat.com> 4.2.6-2
- Include patch to fix missing @param so javadocs will build

* Fri Jun  5 2009 Rob Crittenden <rcritten@redhat.com> 4.2.6-1
- Resolves: bug 455305 - <cfu@redhat.com>
  CA ECC Signing Key Failure
- Resolves: bug 502111 - <cfu@redhat.com>
  Need JSS interface for NSS's PK11_GenerateKeyPairWithOpFlags() function
- Resolves: bug 503809 - <mharmsen@redhat.com>
  Update JSS version to 4.2.6
- Resolves: bug 503817 - <mharmsen@redhat.com>
  Create JSS Javadocs as their own RPM

* Wed Feb 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 4.2.5-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild
 
* Tue Aug  5 2008 Tom "spot" Callaway <tcallawa@redhat.com> - 4.2.5-3
- fix license tag

* Tue Feb 19 2008 Fedora Release Engineering <rel-eng@fedoraproject.org> - 4.2.5-2
- Autorebuild for GCC 4.3

* Fri Aug  3 2007 Rob Crittenden <rcritten@redhat.com> 4.2.5-1
- update to 4.2.5

* Thu May 24 2007 Rob Crittenden <rcritten@redhat.com> 4.2.4-6
- Use _jnidir macro instead of _javadir for the jar files. This will break
  multilib installs but adheres to the jpackage spec.

* Wed May 16 2007 Rob Crittenden <rcritten@redhat.com> 4.2.4-5
- Include the 3 license files
- Remove Requires for nss and nspr. These libraries have versioned symbols
  so BuildRequires is enough to set the minimum.
- Add sparc64 for the 64-bit list

* Mon May 14 2007 Rob Crittenden <rcritten@redhat.com> 4.2.4-4
- Included additional comments on jar signing and why ldconfig is not
  required.

* Thu May 10 2007 Rob Crittenden <rcritten@redhat.com> 4.2.4-3
- Added information on how to pull the source into a tar.gz

* Thu Mar 15 2007  Rob Crittenden <rcritten@redhat.com> 4.2.4-2
- Added RPM_OPT_FLAGS to XCFLAGS
- Added link to Sun JCE information

* Tue Feb 27 2007 Rob Crittenden <rcritten@redhat.com> 4.2.4-1
- Initial build
