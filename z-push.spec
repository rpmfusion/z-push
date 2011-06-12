%global svnrevision 685
%global with_ldap   1

Summary:        ActiveSync over-the-air implementation for mobile syncing
Name:           z-push
Version:        1.5.3
Release:        1%{?dist}
License:        AGPLv3 with exceptions
Group:          Applications/Productivity
URL:            http://z-push.sourceforge.net/
Source0:        http://download.berlios.de/%{name}/%{name}-%{version}-%{svnrevision}.tar.gz
Source1:        z-push-permission.pdf
Source2:        z-push-README.FEDORA.package
Source3:        z-push-README.FEDORA.zarafa
Source4:        z-push.conf
Source5:        zarafa-z-push.conf
Patch0:         z-push-1.5.2-package.patch
Patch1:         z-push-1.5.2-zarafa.patch
Patch2:         z-push-1.5.3-license.patch
Requires:       httpd, php >= 4.3.0, php-imap >= 4.3.0
%if %{with_ldap}
Requires:       php-ldap >= 4.3.0
%endif
BuildArch:      noarch
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

%description
Z-Push is an implementation of the ActiveSync protocol which is used
'over-the-air' for multi platform ActiveSync devices, including Windows
Mobile, Android, iPhone, Sony Ericsson and Nokia mobile devices. With
Z-Push any groupware can be connected and synced with these devices.

For use cases of Z-Push with the Zarafa Collaboration Platform and Open
Source Collaboration, please use the prepared package zarafa-z-push.

%package -n zarafa-%{name}
Summary:        ActiveSync over-the-air implementation for Zarafa
Group:          Applications/Productivity
Requires:       httpd, php >= 4.3.0, php-mapi >= 6.40.0
%if %{with_ldap}
Requires:       php-ldap >= 4.3.0
%endif

%description -n zarafa-%{name}
Z-Push is an implementation of the ActiveSync protocol which is used
'over-the-air' for multi platform ActiveSync devices, including Windows
Mobile, Android, iPhone, Sony Ericsson and Nokia mobile devices. With
Z-Push any groupware can be connected and synced with these devices.

This package is prepared for use with the Zarafa Collaboration Platform
and Open Source Collaboration. For non-Zarafa use cases, please use the
regular Z-Push package.

%prep
%setup -q -T -c -a 0

# Copy permission for later usage
cp -pf %{SOURCE1} permission.pdf

# Correct wrong file permissions
chmod 644 %{name}-%{version}-%{svnrevision}/{include/z_RFC822,streamer}.php

# Z-Push for Zarafa
mkdir zarafa-%{name}-%{version}-%{svnrevision}
pushd zarafa-%{name}-%{version}-%{svnrevision}
cp -af ../%{name}-%{version}-%{svnrevision}/* .
cp -pf %{SOURCE3} README.FEDORA
%patch1 -p1 -b .zarafa
touch -c -r config.php{.zarafa,}
%patch2 -p1
popd

# Z-Push without Zarafa
pushd %{name}-%{version}-%{svnrevision}
cp -pf %{SOURCE2} README.FEDORA
%patch0 -p1 -b .package
touch -c -r config.php{.package,}
%patch2 -p1
popd

%build

%install
rm -rf $RPM_BUILD_ROOT

# Create all needed directories
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/{{,zarafa}/%{name},httpd/conf.d}/
mkdir -p $RPM_BUILD_ROOT{%{_bindir},%{_datadir}/{%{name},zarafa-%{name}}}/
mkdir -p $RPM_BUILD_ROOT%{_localstatedir}/lib/{%{name},zarafa-%{name}}/state/

# Z-Push without Zarafa
pushd %{name}-%{version}-%{svnrevision}

# Install all files into destination
cp -af * $RPM_BUILD_ROOT%{_datadir}/%{name}/

# Move configuration file to its place
mv -f $RPM_BUILD_ROOT%{_datadir}/%{name}/config.php $RPM_BUILD_ROOT%{_sysconfdir}/%{name}/config.php
ln -sf ../../..%{_sysconfdir}/%{name}/config.php $RPM_BUILD_ROOT%{_datadir}/%{name}/config.php

# Install the apache configuration file
install -p -m 644 %{SOURCE4} $RPM_BUILD_ROOT%{_sysconfdir}/httpd/conf.d/%{name}.conf

# Remove all Zarafa requiring files
rm -f $RPM_BUILD_ROOT%{_datadir}/%{name}/{backend/ics,include/z_{ical,tnef}}.php

# Move searchldap configuration to its place
%if %{with_ldap}
mv -f $RPM_BUILD_ROOT%{_datadir}/%{name}/backend/searchldap/config.php $RPM_BUILD_ROOT%{_sysconfdir}/%{name}/searchldap.php
ln -sf ../../../../..%{_sysconfdir}/%{name}/searchldap.php $RPM_BUILD_ROOT%{_datadir}/%{name}/backend/searchldap/config.php
%else
rm -rf $RPM_BUILD_ROOT%{_datadir}/%{name}/backend/{searchbackend.php,searchldap/}
%endif

popd

# Z-Push for Zarafa
pushd zarafa-%{name}-%{version}-%{svnrevision}

# Install all files into destination
cp -af * $RPM_BUILD_ROOT%{_datadir}/zarafa-%{name}/

# Move configuration file to its place
mv -f $RPM_BUILD_ROOT%{_datadir}/zarafa-%{name}/config.php $RPM_BUILD_ROOT%{_sysconfdir}/zarafa/%{name}/config.php
ln -sf ../../..%{_sysconfdir}/zarafa/%{name}/config.php $RPM_BUILD_ROOT%{_datadir}/zarafa-%{name}/config.php

# Install the apache configuration file
install -p -m 644 %{SOURCE5} $RPM_BUILD_ROOT%{_sysconfdir}/httpd/conf.d/zarafa-%{name}.conf

# Remove all non-Zarafa related files
rm -f $RPM_BUILD_ROOT%{_datadir}/zarafa-%{name}/backend/{diffbackend,imap,maildir,vcarddir}.php

# Move searchldap configuration to its place
%if %{with_ldap}
mv -f $RPM_BUILD_ROOT%{_datadir}/zarafa-%{name}/backend/searchldap/config.php $RPM_BUILD_ROOT%{_sysconfdir}/zarafa/%{name}/searchldap.php
ln -sf ../../../../..%{_sysconfdir}/zarafa/%{name}/searchldap.php $RPM_BUILD_ROOT%{_datadir}/zarafa-%{name}/backend/searchldap/config.php
%else
rm -rf $RPM_BUILD_ROOT%{_datadir}/zarafa-%{name}/backend/{searchbackend.php,searchldap/}
%endif

# Install Zarafa-related command line tool
install -p -m 755 backend/zarafa/z-push-admin.php $RPM_BUILD_ROOT%{_bindir}/z-push-admin

popd

# Remove all unwanted files and directories
rm -rf $RPM_BUILD_ROOT%{_datadir}/{%{name},zarafa-%{name}}/{state,backend/{kolab,zarafa}}/
rm -f $RPM_BUILD_ROOT%{_datadir}/{%{name},zarafa-%{name}}/{INSTALL,LICENSE,{config,debug}.php.{package,zarafa},README.FEDORA}

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root,-)
%doc %{name}-%{version}-%{svnrevision}/LICENSE permission.pdf
%doc %{name}-%{version}-%{svnrevision}/README.FEDORA
%config(noreplace) %{_sysconfdir}/httpd/conf.d/%{name}.conf
%dir %{_sysconfdir}/%{name}/
%config(noreplace) %{_sysconfdir}/%{name}/config.php
%if %{with_ldap}
%config(noreplace) %{_sysconfdir}/%{name}/searchldap.php
%endif
%{_datadir}/%{name}/
%dir %{_localstatedir}/lib/%{name}/
%attr(-,apache,apache) %dir %{_localstatedir}/lib/%{name}/state/

%files -n zarafa-%{name}
%defattr(-,root,root,-)
%doc zarafa-%{name}-%{version}-%{svnrevision}/LICENSE permission.pdf
%doc zarafa-%{name}-%{version}-%{svnrevision}/README.FEDORA
%config(noreplace) %{_sysconfdir}/httpd/conf.d/zarafa-%{name}.conf
%dir %{_sysconfdir}/zarafa/
%dir %{_sysconfdir}/zarafa/%{name}/
%config(noreplace) %{_sysconfdir}/zarafa/%{name}/config.php
%if %{with_ldap}
%config(noreplace) %{_sysconfdir}/zarafa/%{name}/searchldap.php
%endif
%{_bindir}/z-push-admin
%{_datadir}/zarafa-%{name}/
%dir %{_localstatedir}/lib/zarafa-%{name}/
%attr(-,apache,apache) %dir %{_localstatedir}/lib/zarafa-%{name}/state/

%changelog
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
