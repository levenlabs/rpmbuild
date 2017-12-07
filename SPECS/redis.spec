Packager: Joe Admin <systems@getadmiral.com>

Name: redis
Version: 4.0.6
Release: 0%{dist}

Summary: levenlab's redis 3.2.3 compilation

License: BSD

Source: http://download.redis.io/releases/%{name}-%{version}.tar.gz
Source1: redis.service

BuildRequires: tcl

%define installprefix /usr

%description

%prep
%setup -q -n redis-%{version}

%build
make

%install
make PREFIX=$RPM_BUILD_ROOT%{installprefix} install

install -d $RPM_BUILD_ROOT/etc/redis
install -d $RPM_BUILD_ROOT/usr/lib/systemd/system
install -d $RPM_BUILD_ROOT/var/lib/redis
install -d $RPM_BUILD_ROOT/var/run/redis
install -m 0644 redis.conf $RPM_BUILD_ROOT/etc/redis/redis.conf
install -m 0644 %{SOURCE1} $RPM_BUILD_ROOT/usr/lib/systemd/system/redis.service
install -m 0644 sentinel.conf $RPM_BUILD_ROOT/etc/redis/sentinel.conf
install -m 0755 src/redis-trib.rb $RPM_BUILD_ROOT/usr/bin/redis-trib.rb

%files
%defattr(-,root,root)
/etc/redis
/usr/lib/systemd/system/redis.service
/var/lib/redis
/var/run/redis
%{installprefix}/bin/*

%clean

%post
useradd -M -r -s /bin/false redis
chown redis:redis /var/lib/redis
chown redis:redis /var/run/redis
systemctl daemon-reload
