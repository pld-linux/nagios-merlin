Summary:	Merlin: Module for Effortless Redundancy and Loadbalancing In Nagios
Name:		nagios-merlin
Version:	0.9.0
Release:	0.20
License:	GPL v2
Group:		Networking
Source0:	http://www.op5.org/op5media/op5.org/downloads/merlin-%{version}.tar.gz
# Source0-md5:	dd3fda7b4eea661e65b60f9b6a7d079e
Source1:	merlind.init
Source2:	README.PLD
Patch0:		ldflags-as-needed.patch
Patch1:		install.patch
URL:		http://www.op5.org/community/plugin-inventory/op5-projects/merlin
BuildRequires:	bash
BuildRequires:	libdbi-devel
BuildRequires:	rpm-pythonprov
BuildRequires:	rpmbuild(macros) >= 1.228
BuildRequires:	sed >= 4.0.9
Requires(post,preun):	/sbin/chkconfig
Requires:	libdbi-drivers-mysql
Requires:	nagios >= 3.2.4
Requires:	rc-scripts
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_sysconfdir	/etc/nagios
%define		appdir		%{_libdir}/nagios/merlin
%define		logdir		/var/log/nagios
%define		sockdir		/var/lib/nagios

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
%patch1 -p1

find -type f | xargs \
%{__sed} -i -e '
	s#@@DESTDIR@@/logs/neb.log#%{logdir}/merlin-neb.log#g
	s#@@DESTDIR@@/logs/daemon.log#%{logdir}/merlind.log#g
	s#@@DESTDIR@@/ipc.sock#%{sockdir}/ipc.sock#g
	s#/var/run/merlin.pid#/var/run/merlind.pid#

	# fix paths in "apps"
	# we cant just replace whole path, as the targets differ
	# sort -r the block when done adding
	s#/opt/monitor/var/status.log#/var/lib/nagios/status.dat#
	s#/opt/monitor/var/rw/#/var/lib/nagios/rw/#
	s#/opt/monitor/var/objects.cache#/var/lib/nagios/objects.cache#
	s#/opt/monitor/var/nagios.log#%{logdir}/nagios.log#
	s#/opt/monitor/var/conf_sync.log#%{logdir}/conf_sync.log#
	s#/opt/monitor/var/archives#%{logdir}/archives#
	s#/opt/monitor/pushed_logs#/var/log/merlin/pushed_logs#
	s#/opt/monitor/op5/merlin/merlin.conf#%{_sysconfdir}/merlin.conf#
	s#/opt/monitor/op5/merlin/logs/#/var/log/merlin/#
	s#/opt/monitor/op5/merlin#%{appdir}#
	s#/opt/monitor/etc/nagios.cfg#%{_sysconfdir}/nagios.cfg#g
	s#/opt/monitor/etc/#%{_sysconfdir}/#g
	s#/opt/monitor/bin/nagios#%{_sbindir}/nagios#g
	s#/etc/op5/distributed/state/#/var/lib/nagios/merlin/state/#
	s#/etc/init.d/#/etc/rc.d/init.d/#
	s#/usr/libexec/merlin#%{appdir}/lib#
'

cp -a %{SOURCE2} README.PLD

%build
%{__make} \
	V=1 \
	CC="%{__cc}" \
	CFLAGS='%{rpmcflags} -pipe -Wall -Wno-unused-parameter -fPIC -fno-strict-aliasing -rdynamic' \
	LDFLAGS="%{rpmldflags}"

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{/etc/rc.d/init.d,%{_sbindir},%{_sysconfdir}}
# script uses bash specificts (pushd, popd)
bash install-merlin.sh \
	--root=$RPM_BUILD_ROOT \
	--dest-dir=%{appdir} \
	--libexecdir=%{appdir}/lib \
	--bindir=%{_sbindir} \
	--batch \
	--install=files,apps

chmod a+rx $RPM_BUILD_ROOT%{appdir}/merlin.so
rm -f $RPM_BUILD_ROOT%{appdir}/init.sh
rm -f $RPM_BUILD_ROOT%{appdir}/install-merlin.sh
rm -f $RPM_BUILD_ROOT%{appdir}/example.conf

install -p %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/merlind
sed -i -e 's,/usr/lib/nagios/merlin,%{appdir},' $RPM_BUILD_ROOT/etc/rc.d/init.d/merlind

mv $RPM_BUILD_ROOT{%{appdir},%{_sbindir}}/merlind

mv $RPM_BUILD_ROOT{%{appdir},%{_sysconfdir}}/merlin.conf

%clean
rm -rf $RPM_BUILD_ROOT

%post
/sbin/chkconfig --add merlind
%service merlind restart

%preun
if [ "$1" = "0" ]; then
	%service -q merlind stop
	/sbin/chkconfig --del merlind
fi

%files
%defattr(644,root,root,755)
%doc COPYING HOWTO README SPECS TECHNICAL README.PLD
%doc example.conf
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/merlin.conf
%attr(754,root,root) /etc/rc.d/init.d/merlind
%attr(755,root,root) %{_sbindir}/merlind
%dir %{appdir}
%{appdir}/db.sql
%{appdir}/object_importer.inc.php
%attr(755,root,root) %{appdir}/import
%attr(755,root,root) %{appdir}/import.php
%attr(755,root,root) %{appdir}/merlin.so
%attr(755,root,root) %{appdir}/showlog

# apps
%attr(755,root,root) %{_sbindir}/mon
%dir %{appdir}/lib
%attr(755,root,root) %{appdir}/lib/-oconf
%attr(755,root,root) %{appdir}/lib/log.push.sh
%attr(755,root,root) %{appdir}/lib/node.py
%attr(755,root,root) %{appdir}/lib/oconf.py
%attr(755,root,root) %{appdir}/lib/restart.sh
%attr(755,root,root) %{appdir}/lib/sshkey.fetch.sh
%attr(755,root,root) %{appdir}/lib/sshkey.push.sh
%attr(755,root,root) %{appdir}/lib/start.sh
%attr(755,root,root) %{appdir}/lib/stop.sh
%{appdir}/lib/modules/compound_config.py
%{appdir}/lib/modules/merlin_apps_utils.py
%{appdir}/lib/modules/merlin_conf.py
