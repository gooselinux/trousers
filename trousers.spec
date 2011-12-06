%global name         trousers
%global version      0.3.4
%global tarballrev   -1
%global release      4

Name: %{name}
Summary: TCG's Software Stack v1.2 
Version: %{version}
Release: %{release}%{?dist}
License: CPL
Group: System Environment/Libraries
Url: http://trousers.sourceforge.net
Source0: http://downloads.sourceforge.net/%{name}/%{name}-%{version}.tar.gz
# Patch from upstream cleaning up some use of free()
Patch1: trousers-0.3.4-free.patch
Patch2: trousers-0.3.4-init-lsb.patch
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildRequires: libtool, openssl-devel
Requires(pre): shadow-utils
Requires(post): chkconfig
Requires(preun): chkconfig
Requires(preun): initscripts
Requires(postun): initscripts

%description
TrouSerS is an implementation of the Trusted Computing Group's Software Stack
(TSS) specification. You can use TrouSerS to write applications that make use
of your TPM hardware. TPM hardware can create, store and use RSA keys
securely (without ever being exposed in memory), verify a platform's software
state using cryptographic hashes and more.

%package static
Summary: TrouSerS TCG Device Driver Library
Group: Development/Libraries
Requires: %{name}-devel = %{version}-%{release}

%description static
The TCG Device Driver Library (TDDL) used by the TrouSerS tcsd as the
interface to the TPM's device driver. For more information about writing
applications to the TDDL interface, see the latest TSS spec at
https://www.trustedcomputinggroup.org/specs/TSS.

%package devel
Summary: TrouSerS header files and documentation
Group: Development/Libraries
Requires: %{name} = %{version}-%{release}

%description devel
Header files and man pages for use in creating Trusted Computing enabled
applications.

%prep
%setup -q
%patch1 -p1
%patch2 -p1

%build
%configure --with-gui=openssl
make %{?_smp_mflags}

%install
rm -rf ${RPM_BUILD_ROOT}
mkdir -p ${RPM_BUILD_ROOT}/%{_localstatedir}/lib/tpm
mkdir -p ${RPM_BUILD_ROOT}/%{_initrddir}
cp -p dist/fedora/fedora.initrd.tcsd ${RPM_BUILD_ROOT}/%{_initrddir}/tcsd
make install DESTDIR=${RPM_BUILD_ROOT} INSTALL="install -p"
rm -f ${RPM_BUILD_ROOT}/%{_libdir}/libtspi.la

%clean
rm -rf ${RPM_BUILD_ROOT}

%pre
getent group tss >/dev/null || groupadd -g 59 -r tss
getent passwd tss >/dev/null || \
useradd -r -u 59 -g tss -d /dev/null -s /sbin/nologin \
 -c "Account used by the trousers package to sandbox the tcsd daemon" tss
exit 0

%post
/sbin/ldconfig
/sbin/chkconfig --add tcsd

%preun
if [ $1 = 0 ]; then
    /sbin/service tcsd stop > /dev/null 2>&1
    /sbin/chkconfig --del tcsd
fi

%postun
/sbin/ldconfig
if [ $1 -ge 1 ]; then
    /sbin/service tcsd condrestart >/dev/null 2>&1 || :
fi

%files
%defattr(-, root, root, -)
%doc README LICENSE ChangeLog
%{_sbindir}/tcsd
%{_libdir}/libtspi.so.?
%{_libdir}/libtspi.so.?.?.?
%config(noreplace) %attr(0600, tss, tss) %{_sysconfdir}/tcsd.conf
%attr(0644, root, root) %{_mandir}/man5/*
%attr(0644, root, root) %{_mandir}/man8/*
%{_initrddir}/tcsd
%attr(0700, tss, tss) %{_localstatedir}/lib/tpm/

%files devel
# The files to be used by developers, 'trousers-devel'
%defattr(-, root, root, -)
%attr(0755, root, root) %{_libdir}/libtspi.so
%{_includedir}/tss/
%{_includedir}/trousers/
%{_mandir}/man3/Tspi_*

%files static
%defattr(-, root, root, -)
# The only static library shipped by trousers, the TDDL
%{_libdir}/libtddl.a

%changelog
* Wed Jul 07 2010 Steve Grubb <sgrubb@redhat.com> 0.3.4-4
- Adjusted patch
resolves: #593673 Not LSB compliant initscript for tcsd daemon

* Tue Jul 06 2010 Steve Grubb <sgrubb@redhat.com> 0.3.4-3
resolves: #593673 Not LSB compliant initscript for tcsd daemon

* Thu Feb 25 2010 Steve Grubb <sgrubb@redhat.com> 0.3.4-2
- Fix issue freeing a data structure

* Fri Jan 29 2010 Steve Grubb <sgrubb@redhat.com> 0.3.4-1
- New upstream bug fix release
resolves: #557769

* Fri Jan 22 2010 Steve Grubb <sgrubb@redhat.com> 0.3.3.1-1
- New upstream bug fix release
resolves: #557769

* Fri Jan 15 2010 Steve Grubb <sgrubb@redhat.com> 0.3.3-1
- Initial package for RHEL6
resolves: #555782

* Fri Dec 11 2009 Dennis Gregorovic <dgregor@redhat.com> - 0.3.1-19.1
- Rebuilt for RHEL 6

