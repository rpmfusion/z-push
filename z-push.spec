%global svnrevision 1690

Summary:        ActiveSync over-the-air implementation for mobile syncing
Name:           z-push
Version:        2.0.7
Release:        2%{?dist}
License:        AGPLv3 with exceptions
Group:          Applications/Productivity
URL:            http://z-push.sourceforge.net/
Source0:        http://www.zarafa-deutschland.de/z-push-download/final/2.0/%{name}-%{version}-%{svnrevision}.tar.gz
Source1:        z-push-permission.pdf
Source2:        z-push-README.FEDORA
Source3:        z-push.conf
Source4:        z-push.logrotate
Patch0:         z-push-2.0.6-package.patch
Requires:       httpd, php-iconv, php-sysvsem, php-sysvshm
Requires:       coreutils, bash, grep, less, php-pcntl
# Bug: php53 from RHEL 5 does not provide php (#717158)
%if 0%{?rhel} == 5
Requires:       mod_php >= 5.1
%else
Requires:       php >= 5.1
%endif
BuildArch:      noarch
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

%description
Z-Push is an implementation of the ActiveSync protocol which is used
'over-the-air' for multi platform ActiveSync devices, including Windows
Mobile, Android, iPhone, Sony Ericsson and Nokia mobile devices. With
Z-Push any groupware can be connected and synced with these devices.

%package combined
Summary:        Combines several data backend providers for Z-Push
Group:          Applications/Productivity
Requires:       %{name} = %{version}-%{release}

%description combined
The z-push-combined package contains a special data backend provider
for Z-Push to combine several data backend providers. This allows to
handle each type of item (e-mails, contacts, calendar entries, tasks)
by a different backend. A combination could be to handle e-mails via
the IMAP data backend provider, while all other items are handled by
the Zarafa data backend provider. If you want to use this, you will
need to install this package and additionally the other Z-Push data
backend providers that shall be combined.

%package imap
Summary:        IMAP data backend provider for Z-Push
Group:          Applications/Productivity
Requires:       %{name} = %{version}-%{release}, php-imap >= 5.1.0

%description imap
The z-push-imap package contains the IMAP data backend provider for
Z-Push. If you want Z-Push to access an IMAP server, you will need to
install this package.

%package maildir
Summary:        Maildir data backend provider for Z-Push
Group:          Applications/Productivity
Requires:       %{name} = %{version}-%{release}

%description maildir
The z-push-maildir package contains the Maildir data backend provider
for Z-Push. If you want Z-Push to access a Maildir, you will need to
install this package.

%package searchldap
Summary:        LDAP search backend provider for Z-Push
Group:          Applications/Productivity
Requires:       %{name} = %{version}-%{release}, php-ldap >= 5.1.0

%description searchldap
The z-push-searchldap contains the LDAP search backend provider for
Z-Push. If you want to perform search requests (Global Address Book
search) in an LDAP directory rather the default search functionality
provided by the data backend, you will need to install this package.

%package vcarddir
Summary:        vCard directory data backend provider for Z-Push
Group:          Applications/Productivity
Requires:       %{name} = %{version}-%{release}

%description vcarddir
The z-push-vcarddir package contains the vCard directory backend data
provider for Z-Push. If you want Z-Push to access a vCard directory,
you will need to install this package.

%package zarafa
Summary:        Zarafa data backend provider for Z-Push
Group:          Applications/Productivity
Requires:       %{name} = %{version}-%{release}, php-mapi >= 6.40.0
Provides:       zarafa-%{name} = %{version}-%{release}
Obsoletes:      zarafa-%{name} < %{version}-%{release}

%description zarafa
The z-push-zarafa package contains the Zarafa Collaboration Plattform
data backend provider for Z-Push. If you want Z-Push to access a MAPI-
based service or the Zarafa Collaboration Plattform, you will need to
install this package.

%prep
%setup -q -n %{name}-%{version}-%{svnrevision}
%patch0 -p1

%build

%install
rm -rf $RPM_BUILD_ROOT

# Create all needed directories
mkdir -p $RPM_BUILD_ROOT{{%{_sysconfdir},%{_datadir},%{_localstatedir}/{lib,log}}/%{name},%{_sbindir}}

# Install all files into destination
cp -af * $RPM_BUILD_ROOT%{_datadir}/%{name}/

# Move configuration files to its places
mv -f $RPM_BUILD_ROOT%{_datadir}/%{name}/config.php $RPM_BUILD_ROOT%{_sysconfdir}/%{name}/config.php
ln -sf ../../..%{_sysconfdir}/%{name}/config.php $RPM_BUILD_ROOT%{_datadir}/%{name}/config.php

for backend in imap maildir vcarddir; do
  mkdir -p $RPM_BUILD_ROOT%{_datadir}/%{name}/backend/${backend}/
  mv -f $RPM_BUILD_ROOT%{_datadir}/%{name}/backend/${backend}.php $RPM_BUILD_ROOT%{_datadir}/%{name}/backend/${backend}/
  mv -f $RPM_BUILD_ROOT%{_datadir}/%{name}/config.${backend}.php $RPM_BUILD_ROOT%{_sysconfdir}/%{name}/${backend}.php
  ln -sf ../../../../..%{_sysconfdir}/%{name}/${backend}.php $RPM_BUILD_ROOT%{_datadir}/%{name}/backend/${backend}/config.php
done

for backend in combined searchldap zarafa; do
  mv -f $RPM_BUILD_ROOT%{_datadir}/%{name}/backend/${backend}/config.php $RPM_BUILD_ROOT%{_sysconfdir}/%{name}/${backend}.php
  ln -sf ../../../../..%{_sysconfdir}/%{name}/${backend}.php $RPM_BUILD_ROOT%{_datadir}/%{name}/backend/${backend}/config.php
done

# Install the command line utilities
mv -f $RPM_BUILD_ROOT%{_datadir}/%{name}/%{name}-admin.php $RPM_BUILD_ROOT%{_sbindir}/%{name}-admin
mv -f $RPM_BUILD_ROOT%{_datadir}/%{name}/%{name}-top.php $RPM_BUILD_ROOT%{_sbindir}/%{name}-top

# Install the apache configuration file
install -D -p -m 644 %{SOURCE3} $RPM_BUILD_ROOT%{_sysconfdir}/httpd/conf.d/%{name}.conf

# Install the logrotate configuration file
install -D -p -m 644 %{SOURCE4} $RPM_BUILD_ROOT%{_sysconfdir}/logrotate.d/%{name}

# Remove all unwanted files and directories
rm -rf $RPM_BUILD_ROOT%{_datadir}/%{name}/{INSTALL,LICENSE,backend/kolab}

# Copy permission and README for later usage
cp -pf %{SOURCE1} permission.pdf
cp -pf %{SOURCE2} README.FEDORA

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root,-)
%doc LICENSE README.FEDORA permission.pdf
%config(noreplace) %{_sysconfdir}/httpd/conf.d/%{name}.conf
%config(noreplace) %{_sysconfdir}/logrotate.d/%{name}
%dir %{_sysconfdir}/%{name}/
%config(noreplace) %{_sysconfdir}/%{name}/config.php
%{_sbindir}/z-push-admin
%{_sbindir}/z-push-top
%{_datadir}/%{name}/
%exclude %{_datadir}/%{name}/backend/combined/
%exclude %{_datadir}/%{name}/backend/imap/
%exclude %{_datadir}/%{name}/backend/maildir/
%exclude %{_datadir}/%{name}/backend/searchldap/
%exclude %{_datadir}/%{name}/backend/vcarddir/
%exclude %{_datadir}/%{name}/backend/zarafa/
%attr(-,apache,apache) %dir %{_localstatedir}/lib/%{name}/
%attr(-,apache,apache) %dir %{_localstatedir}/log/%{name}/

%files combined
%defattr(-,root,root,-)
%config(noreplace) %{_sysconfdir}/%{name}/combined.php
%{_datadir}/%{name}/backend/combined/

%files imap
%defattr(-,root,root,-)
%config(noreplace) %{_sysconfdir}/%{name}/imap.php
%{_datadir}/%{name}/backend/imap/

%files maildir
%defattr(-,root,root,-)
%config(noreplace) %{_sysconfdir}/%{name}/maildir.php
%{_datadir}/%{name}/backend/maildir/

%files searchldap
%defattr(-,root,root,-)
%config(noreplace) %{_sysconfdir}/%{name}/searchldap.php
%{_datadir}/%{name}/backend/searchldap/

%files vcarddir
%defattr(-,root,root,-)
%config(noreplace) %{_sysconfdir}/%{name}/vcarddir.php
%{_datadir}/%{name}/backend/vcarddir/

%files zarafa
%defattr(-,root,root,-)
%config(noreplace) %{_sysconfdir}/%{name}/zarafa.php
%{_datadir}/%{name}/backend/zarafa/

%changelog
* Sun Apr 28 2013 Nicolas Chauvet <kwizart@gmail.com> - 2.0.7-2
- https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Sat Feb 23 2013 Robert Scheck <robert@fedoraproject.org> 2.0.7-1
- Upgrade to 2.0.7

* Thu Dec 06 2012 Robert Scheck <robert@fedoraproject.org> 2.0.6-1
- Upgrade to 2.0.6

* Thu Nov 08 2012 Robert Scheck <robert@fedoraproject.org> 2.0.5-1
- Upgrade to 2.0.5

* Sun Nov 04 2012 Robert Scheck <robert@fedoraproject.org> 2.0.4-1
- Upgrade to 2.0.4

* Wed Oct 31 2012 Robert Scheck <robert@fedoraproject.org> 1.5.13-1
- Upgrade to 1.5.13

* Sun Aug 26 2012 Robert Scheck <robert@fedoraproject.org> 1.5.12-1
- Upgrade to 1.5.12

* Sat Jun 30 2012 Robert Scheck <robert@fedoraproject.org> 1.5.11-1
- Upgrade to 1.5.11

* Tue Jun 05 2012 Robert Scheck <robert@fedoraproject.org> 1.5.10-1
- Upgrade to 1.5.10

* Mon Apr 09 2012 Robert Scheck <robert@fedoraproject.org> 1.5.8-1
- Upgrade to 1.5.8

* Tue Feb 07 2012 Robert Scheck <robert@fedoraproject.org> 1.5.7-1
- Upgrade to 1.5.7

* Sun Dec 11 2011 Robert Scheck <robert@fedoraproject.org> 1.5.6-1
- Upgrade to 1.5.6

* Sun Sep 18 2011 Robert Scheck <robert@fedoraproject.org> 1.5.5-1
- Upgrade to 1.5.5

* Mon Jul 18 2011 Robert Scheck <robert@fedoraproject.org> 1.5.4-1
- Upgrade to 1.5.4

* Tue Jun 07 2011 Robert Scheck <robert@fedoraproject.org> 1.5.3-1
- Upgrade to 1.5.3

* Wed Apr 27 2011 Robert Scheck <robert@fedoraproject.org> 1.5.2-1
- Upgrade to 1.5.2

* Fri Feb 11 2011 Robert Scheck <robert@fedoraproject.org> 1.5.1-1
- Upgrade to 1.5.1

* Mon Jan 26 2011 Robert Scheck <robert@fedoraproject.org> 1.5-1
- Upgrade to 1.5

* Thu May 27 2010 Robert Scheck <robert@fedoraproject.org> 1.3-2
- Use date_default_timezone_get() as default (RHBZ #570398)

* Mon May 17 2010 Robert Scheck <robert@fedoraproject.org> 1.3-1
- Upgrade to 1.3

* Sat Feb 27 2010 Robert Scheck <robert@fedoraproject.org> 1.2.2-3
- Use the equivalent namespaces as zarafa-webaccess package

* Sun Aug 09 2009 Robert Scheck <robert@fedoraproject.org> 1.2.2-2
- Require httpd instead of webserver at runtime (RFBZ #585 #c20)

* Sun Jul 05 2009 Robert Scheck <robert@fedoraproject.org> 1.2.2-1
- Upgrade to 1.2.2

* Sun May 10 2009 Robert Scheck <robert@fedoraproject.org> 1.2.1-2
- Re-added the forgotten MAPI_SERVER definement for Zarafa
- Enabled the allow_call_time_pass_reference in PHP settings
- Corrected STATE_DIR value from absolute to relative path

* Thu Apr 30 2009 Robert Scheck <robert@fedoraproject.org> 1.2.1-1
- Upgrade to 1.2.1
- Initial spec file for Fedora and Red Hat Enterprise Linux
