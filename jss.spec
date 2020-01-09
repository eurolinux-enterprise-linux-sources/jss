Name:           jss
Version:        4.2.6
Release:        15%{?dist}
Summary:        Java Security Services (JSS)

Group:          System Environment/Libraries
License:        MPLv1.1 or GPLv2+ or LGPLv2+
URL:            http://www.mozilla.org/projects/security/pki/jss/
# The source for this package was pulled from upstream's cvs. Use the
# following commands to generate the tarball:
# cvs -d :pserver:anonymous@cvs-mirror.mozilla.org:/cvsroot export -r JSS_4_2_6_RTM -d jss-4.2.6 -N mozilla/security/coreconf mozilla/security/jss
# tar -czvf jss-4.2.6.tar.gz jss-4.2.6
Source0:        %{name}-%{version}.tar.gz
Source1:        MPL-1.1.txt
Source2:        gpl.txt
Source3:        lgpl.txt
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires:  nss-devel >= 3.12.3.99
BuildRequires:  nspr-devel >= 4.6.99
BuildRequires:  java-devel
Requires:       java
Requires:       nss >= 3.12.3.99

Patch1:         jss-key_pair_usage_with_op_flags.patch
Patch2:         jss-javadocs-param.patch
Patch3:         jss-ipv6.patch
Patch4:         jss-ECC-pop.patch
Patch5:         jss-loadlibrary.patch
Patch6:         jss-ocspSettings.patch
Patch7:         jss-ECC_keygen_byCurveName.patch
Patch8:         jss-VerifyCertificate.patch
Patch9:         jss-bad-error-string-pointer.patch
Patch10:        jss-VerifyCertificateReturnCU.patch
Patch11:        jss-slots-not-freed.patch


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
%setup -q
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

%build
[ -z "$JAVA_HOME" ] && export JAVA_HOME=%{_jvmdir}/java

# Enable compiler optimizations and disable debugging code
BUILD_OPT=1
export BUILD_OPT

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

%ifarch x86_64 ppc64 ia64 s390x sparc64
USE_64=1
export USE_64
%endif

# The Makefile is not thread-safe
make -C mozilla/security/coreconf
make -C mozilla/security/jss
make -C mozilla/security/jss javadoc

%install
rm -rf $RPM_BUILD_ROOT docdir

# Copy the license files here so we can include them in %doc
cp -p %{SOURCE1} .
cp -p %{SOURCE2} .
cp -p %{SOURCE3} .

# There is no install target so we'll do it by hand

# jars
install -d -m 0755 $RPM_BUILD_ROOT%{_libdir}/jss
install -m 644 mozilla/dist/xpclass.jar ${RPM_BUILD_ROOT}%{_libdir}/jss/jss4-%{version}.jar
ln -fs jss4-%{version}.jar $RPM_BUILD_ROOT%{_libdir}/jss/jss4.jar

install -d -m 0755 $RPM_BUILD_ROOT%{_jnidir}
ln -fs %{_libdir}/jss/jss4.jar $RPM_BUILD_ROOT%{_jnidir}/jss4.jar

# We have to use the name libjss4.so because this is dynamically
# loaded by the jar file.
install -d -m 0755 $RPM_BUILD_ROOT%{_libdir}/jss
install -m 0755 mozilla/dist/Linux*.OBJ/lib/libjss4.so ${RPM_BUILD_ROOT}%{_libdir}/jss/

# javadoc
install -d -m 0755 $RPM_BUILD_ROOT%{_javadocdir}/%{name}-%{version}
cp -rp mozilla/dist/jssdoc/* $RPM_BUILD_ROOT%{_javadocdir}/%{name}-%{version}

%clean
rm -rf $RPM_BUILD_ROOT

# No ldconfig is required since this library is loaded by Java itself.
%files
%defattr(-,root,root,-)
%doc mozilla/security/jss/jss.html MPL-1.1.txt gpl.txt lgpl.txt
%{_libdir}/jss/*
%{_jnidir}/*

%files javadoc
%defattr(-,root,root,-)
%dir %{_javadocdir}/%{name}-%{version}
%{_javadocdir}/%{name}-%{version}/*


%changelog
* Wed Feb 23 2011 Andrew Wnuk <awnuk@redhat.com> - 4.2.6-15
- bug 676083 - JSS: slots not freed

* Mon Jan 31 2011 John Dennis <jdennis@redhat.com> - 4.2.6-13
- Related: bug 656094,
  remove misleading comment in spec file concerning jar signing

* Wed Jan 12 2011 John Dennis <jdennis@redhat.com> - 4.2.6-12
- Related: bug 656094, patch 10 was missing

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

* Mon Feb 27 2007 Rob Crittenden <rcritten@redhat.com> 4.2.4-1
- Initial build
