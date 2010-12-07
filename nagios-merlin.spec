Summary:	Merlin: Module for Effortless Redundancy and Loadbalancing In Nagios
Name:		nagios-merlin
Version:	0.9.0
Release:	0.3
License:	GPL v2
Group:		Networking
Source0:	http://www.op5.org/op5media/op5.org/downloads/merlin-%{version}.tar.gz
# Source0-md5:	dd3fda7b4eea661e65b60f9b6a7d079e
Source1:	merlind.init
Patch0:		ldflags-as-needed.patch
URL:		http://www.op5.org/community/plugin-inventory/op5-projects/merlin
BuildRequires:	bash
BuildRequires:	libdbi-devel
BuildRequires:	rpmbuild(macros) >= 1.228
BuildRequires:	sed >= 4.0.9
Requires(post,preun):	/sbin/chkconfig
Requires:	nagios >= 3.2.4
Requires:	rc-scripts
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_sysconfdir	/etc/nagios
%define		_appdir	%{_libdir}/nagios/merlin

%description
The Merlin project, or Module for Effortless Redundancy and
Loadbalancing In Nagios, was initially started to create an easy way
to set up distributed Nagios installations, allowing Nagios processes
to exchange information directly as an alternative to the standard
nagios way using NSCA. When starting the Ninja project we realised
that we could continue the work on Merlin and adopt the project to
function as backend for Ninja by adding support for storing the status
information in a database, fault tolearance and some other cool
things. This means that Merlin now are responsible for providing
status data, acting as a backend, for the Ninja GUI.

%prep
%setup -q -n merlin-%{version}
%patch0 -p1

%build
%{__make} \
	V=1 \
	CC="%{__cc}" \
	CFLAGS='%{rpmcflags} -pipe -Wall -Wno-unused-parameter -fPIC -fno-strict-aliasing -rdynamic' \
	LDFLAGS="%{rpmldflags}"

%install
rm -rf $RPM_BUILD_ROOT
# script uses bash specificts (pushd, popd)
bash install-merlin.sh \
	--root=$RPM_BUILD_ROOT \
	--dest-dir=%{_appdir} \
	--libexecdir=%{_libdir} \
	--batch \
	--install=files

chmod a+rx $RPM_BUILD_ROOT%{_appdir}/merlin.so
rm -f $RPM_BUILD_ROOT%{_appdir}/init.sh
rm -f $RPM_BUILD_ROOT%{_appdir}/install-merlin.sh
rm -f $RPM_BUILD_ROOT%{_appdir}/example.conf

install -d $RPM_BUILD_ROOT/etc/rc.d/init.d
install -p %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/merlind
sed -i -e 's,/usr/lib/nagios/merlin,%{_appdir},' $RPM_BUILD_ROOT/etc/rc.d/init.d/merlind

install -d $RPM_BUILD_ROOT%{_sbindir}
mv $RPM_BUILD_ROOT{%{_appdir},%{_sbindir}}/merlind

install -d $RPM_BUILD_ROOT%{_sysconfdir}
mv $RPM_BUILD_ROOT{%{_appdir},%{_sysconfdir}}/merlin.conf

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%doc COPYING HOWTO README SPECS TECHNICAL
%doc example.conf
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/merlin.conf
%attr(754,root,root) /etc/rc.d/init.d/merlind
%attr(755,root,root) %{_sbindir}/merlind
%dir %{_appdir}
%{_appdir}/db.sql
%{_appdir}/object_importer.inc.php
%attr(755,root,root) %{_appdir}/import
%attr(755,root,root) %{_appdir}/import.php
%attr(755,root,root) %{_appdir}/merlin.so
%attr(755,root,root) %{_appdir}/showlog
