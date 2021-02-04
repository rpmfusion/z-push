Summary:        ActiveSync over-the-air implementation for mobile syncing
Name:           z-push
Version:        2.2.12
Release:        11%{?dist}
License:        AGPLv3 with exceptions
Group:          Applications/Productivity
URL:            https://z-push.org/
Source0:        http://download.z-push.org/final/2.2/%{name}-%{version}.tar.gz
Source1:        z-push-permission.pdf
Source2:        z-push-README.FEDORA
Source3:        z-push-autodiscover-README.FEDORA
Source4:        z-push.conf
Source5:        z-push-autodiscover.conf
Source6:        z-push.logrotate
Patch0:         z-push-2.2.4-package.patch
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

%package autodiscover
Summary:        Simplify account configuration for ActiveSync users
Group:          Applications/Productivity
Requires:       %{name} = %{version}-%{release}, php-xml >= 5.1.0

%description autodiscover
The z-push-autodiscover package contains the AutoDiscover service to
simplify the account configuration for clients, especially for mobile
phones. While in the past the user was required to enter the server
name, username and password manually into his mobile phone in order to
connect, with AutoDiscover the user is only required to fill in his
e-mail address and the password. AutoDiscover will try several methods
to reach the correct server automatically.

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

%if 0%{?rhel}
%package zarafa
Summary:        Zarafa data backend provider for Z-Push
Group:          Applications/Productivity
Requires:       %{name} = %{version}-%{release}, php-mapi >= 7.0.6
Provides:       zarafa-%{name} = %{version}-%{release}
Obsoletes:      zarafa-%{name} < %{version}-%{release}

%description zarafa
The z-push-zarafa package contains the Zarafa Collaboration Plattform
data backend provider for Z-Push. If you want Z-Push to access a MAPI-
based service or the Zarafa Collaboration Plattform, you will need to
install this package.
%endif

%prep
%setup -q -n %{name}-%{version}
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

%if 0%{?rhel}
variants="zarafa"
%endif

for backend in combined imap maildir searchldap vcarddir $variants; do
  mv -f $RPM_BUILD_ROOT%{_datadir}/%{name}/backend/${backend}/config.php $RPM_BUILD_ROOT%{_sysconfdir}/%{name}/${backend}.php
  ln -sf ../../../../..%{_sysconfdir}/%{name}/${backend}.php $RPM_BUILD_ROOT%{_datadir}/%{name}/backend/${backend}/config.php
done



mv -f $RPM_BUILD_ROOT%{_datadir}/%{name}/autodiscover/config.php $RPM_BUILD_ROOT%{_sysconfdir}/%{name}/autodiscover.php
ln -sf ../../../..%{_sysconfdir}/%{name}/${backend}.php $RPM_BUILD_ROOT%{_datadir}/%{name}/autodiscover/config.php

# Install the command line utilities
mv -f $RPM_BUILD_ROOT%{_datadir}/%{name}/%{name}-admin.php $RPM_BUILD_ROOT%{_sbindir}/%{name}-admin
mv -f $RPM_BUILD_ROOT%{_datadir}/%{name}/%{name}-top.php $RPM_BUILD_ROOT%{_sbindir}/%{name}-top

# Install the apache configuration files
install -D -p -m 644 %{SOURCE4} $RPM_BUILD_ROOT%{_sysconfdir}/httpd/conf.d/%{name}.conf
install -D -p -m 644 %{SOURCE5} $RPM_BUILD_ROOT%{_sysconfdir}/httpd/conf.d/%{name}-autodiscover.conf

# Install the logrotate configuration file
install -D -p -m 644 %{SOURCE6} $RPM_BUILD_ROOT%{_sysconfdir}/logrotate.d/%{name}

# Remove all unwanted files and directories
rm -rf $RPM_BUILD_ROOT%{_datadir}/%{name}/{autodiscover/INSTALL,composer.json,INSTALL,LICENSE}

# Correct the wrong file permissions
chmod 644 $RPM_BUILD_ROOT%{_datadir}/%{name}/lib/syncobjects/syncresolverecipient.php

# Copy permission and README for later usage
cp -pf %{SOURCE1} permission.pdf
cp -pf %{SOURCE2} README.FEDORA
cp -pf %{SOURCE3} autodiscover/README.FEDORA

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root,-)
%{!?_licensedir:%global license %%doc}
%license LICENSE permission.pdf
%doc README.FEDORA
%config(noreplace) %{_sysconfdir}/httpd/conf.d/%{name}.conf
%config(noreplace) %{_sysconfdir}/logrotate.d/%{name}
%dir %{_sysconfdir}/%{name}/
%config(noreplace) %{_sysconfdir}/%{name}/config.php
%{_sbindir}/z-push-admin
%{_sbindir}/z-push-top
%{_datadir}/%{name}/
%exclude %{_datadir}/%{name}/autodiscover/
%exclude %{_datadir}/%{name}/backend/combined/
%exclude %{_datadir}/%{name}/backend/imap/
%exclude %{_datadir}/%{name}/backend/maildir/
%exclude %{_datadir}/%{name}/backend/searchldap/
%exclude %{_datadir}/%{name}/backend/vcarddir/
%exclude %{_datadir}/%{name}/backend/zarafa/
%attr(-,apache,apache) %dir %{_localstatedir}/lib/%{name}/
%attr(-,apache,apache) %dir %{_localstatedir}/log/%{name}/

%files autodiscover
%defattr(-,root,root,-)
%doc autodiscover/README.FEDORA
%config(noreplace) %{_sysconfdir}/httpd/conf.d/%{name}-autodiscover.conf
%config(noreplace) %{_sysconfdir}/%{name}/autodiscover.php
%{_datadir}/%{name}/autodiscover/

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

%if 0%{?rhel}
%files zarafa
%defattr(-,root,root,-)
%config(noreplace) %{_sysconfdir}/%{name}/zarafa.php
%{_datadir}/%{name}/backend/zarafa/
%endif

%changelog
* Thu Feb 04 2021 RPM Fusion Release Engineering <leigh123linux@gmail.com> - 2.2.12-11
- Rebuilt for https://fedoraproject.org/wiki/Fedora_34_Mass_Rebuild

* Wed Aug 19 2020 RPM Fusion Release Engineering <leigh123linux@gmail.com> - 2.2.12-10
- Rebuilt for https://fedoraproject.org/wiki/Fedora_33_Mass_Rebuild

* Wed Feb 05 2020 RPM Fusion Release Engineering <leigh123linux@gmail.com> - 2.2.12-9
- Rebuilt for https://fedoraproject.org/wiki/Fedora_32_Mass_Rebuild

* Fri Aug 09 2019 RPM Fusion Release Engineering <leigh123linux@gmail.com> - 2.2.12-8
- Rebuilt for https://fedoraproject.org/wiki/Fedora_31_Mass_Rebuild

* Tue Mar 05 2019 RPM Fusion Release Engineering <leigh123linux@gmail.com> - 2.2.12-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_30_Mass_Rebuild

* Sun Aug 19 2018 Leigh Scott <leigh123linux@googlemail.com> - 2.2.12-6
- Rebuilt for Fedora 29 Mass Rebuild binutils issue

* Fri Jul 27 2018 RPM Fusion Release Engineering <leigh123linux@gmail.com> - 2.2.12-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Thu Mar 01 2018 RPM Fusion Release Engineering <leigh123linux@googlemail.com> - 2.2.12-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Thu Aug 31 2017 RPM Fusion Release Engineering <kwizart@rpmfusion.org> - 2.2.12-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Tue Mar 21 2017 RPM Fusion Release Engineering <kwizart@rpmfusion.org> - 2.2.12-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Thu Sep 15 2016 Sérgio Basto <sergio@serjux.com> - 2.2.12-1
- Update to 2.2.12

* Thu Sep 15 2016 Sérgio Basto <sergio@serjux.com> - 2.2.9-2
- Only need z-push-zarafa for Zarafa, which is no longer in Fedora, rfbz #3892

* Sat Aug 20 2016 Sérgio Basto <sergio@serjux.com> - 2.2.8-2
- Only need z-push-zarafa for Zarafa, which is no longer in Fedora, rfbz #3892

* Thu Mar 24 2016 Robert Scheck <robert@fedoraproject.org> 2.2.9-1
- Upgrade to 2.2.9

* Tue Feb 02 2016 Robert Scheck <robert@fedoraproject.org> 2.2.8-1
- Upgrade to 2.2.8

* Sat Dec 05 2015 Robert Scheck <robert@fedoraproject.org> 2.2.7-1
- Upgrade to 2.2.7

* Fri Nov 13 2015 Robert Scheck <robert@fedoraproject.org> 2.2.5-1
- Upgrade to 2.2.5

* Fri Oct 02 2015 Robert Scheck <robert@fedoraproject.org> 2.2.4-1
- Upgrade to 2.2.4

* Mon Jun 30 2014 Robert Scheck <robert@fedoraproject.org> 2.1.3-1
- Upgrade to 2.1.3

* Tue May 27 2014 Robert Scheck <robert@fedoraproject.org> 2.1.2-1
- Upgrade to 2.1.2

* Thu Dec 12 2013 Robert Scheck <robert@fedoraproject.org> 2.1.1-1
- Upgrade to 2.1.1

* Sun Dec 08 2013 Robert Scheck <robert@fedoraproject.org> 2.0.9-1
- Upgrade to 2.0.9

* Mon Aug 05 2013 Robert Scheck <robert@fedoraproject.org> 2.0.7-3
- Added configuration compatibility for Apache 2.2 and 2.4

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

* Tue Jan 25 2011 Robert Scheck <robert@fedoraproject.org> 1.5-1
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
